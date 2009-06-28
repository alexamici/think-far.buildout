# This file is part of the bridal demo.
#
# This demo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This demo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this demo.  If not, see <http://www.gnu.org/licenses/>.
"""Sample application for running ZCA within Google App Engine."""

import sys
sys.path.insert(0, 'packages.zip')

import cgi
import google.appengine.api
import google.appengine.ext.db
import google.appengine.ext.webapp
import interfaces
import logging
import pagetemplate
import session
import time
import wsgiref.handlers
import zope.component
import zope.interface


_global_site_manager = None  # The global site manager for registering adapters
                             # and utilities.


def getGlobalSiteManager():
    """Returns global site manager."""

    return _global_site_manager


class Session(google.appengine.ext.db.Model):
    """Persistent session implementation."""

    zope.interface.implements(interfaces.ISession)

    id      = google.appengine.ext.db.StringProperty()
    expires = google.appengine.ext.db.FloatProperty()
    count   = google.appengine.ext.db.IntegerProperty()

    def __repr__(self):
        return "Session(id='%s')" % self.id

    def refresh(self):
        self.expires = time.time() + 300
        self.put()


class SessionProvider(object):
    """Dictionary-like implementation for querying sessions."""

    zope.interface.implements(interfaces.ISessionProvider)

    def __iter__(self):
        for s in google.appengine.ext.db.GqlQuery("SELECT * FROM Session"):
            yield s.id

    def __len__(self):
        return len([s for s in self])

    def __setitem__(self, key, value):
        pass

    def __getitem__(self, key):
        try:
            result = google.appengine.ext.db.GqlQuery("SELECT * FROM Session "
                                                      "WHERE id = '%s'"
                                                      "LIMIT 1" % key)
        except google.appengine.ext.db.BadQueryError:
            raise KeyError

        try:
            return result[0]
        except IndexError:
            raise KeyError

    def __delitem__(self, key):
        s = self.get(key)
        if s:
            s.delete()
        else:
            raise KeyError

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self):
        return list(self)

    def purgeExpired(self):
        now = time.time()
        expired = google.appengine.ext.db.GqlQuery("SELECT * FROM Session "
                                                   "WHERE expires < %f" % now)
        for s in expired:
            s.delete()


class CounterView(object):
    """View for our counter."""

    zope.interface.implements(interfaces.ICounterView)

    template = pagetemplate.PageTemplate('counter.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def render(self):
        return self.template(view=self,
                             context=self.context,
                             request=self.request)


class MainPage(object):
    """Implementation for the main page."""

    zope.interface.implements(interfaces.IPage)

    template = pagetemplate.PageTemplate('index.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def counter(self):
        """Returns counter."""

        view = zope.component.getMultiAdapter((self.context, self.request),
                                              interfaces.ICounterView)
        return view.render()

    def render(self):
        """Writes rendered output to the response object."""

        return self.template(view=self,
                             context=self.context,
                             request=self.request)


class Context(object):
    """Provides a simple context object."""

    zope.interface.implements(interfaces.IContext)

    def __init__(self, s):
        self.session = s


class DemoRequestHandler(google.appengine.ext.webapp.RequestHandler):
    """The demo request handler."""

    def get(self):
        """Handles GET."""

        # The request object as well as the response object must provide a
        # special marker interface to be adaptable.
        zope.interface.directlyProvides(self.request, interfaces.IRequest)
        zope.interface.directlyProvides(self.response, interfaces.IResponse)

        current_session = None

        # Lookup our session manager.
        if _global_site_manager:
            sm = _global_site_manager.getUtility(interfaces.ISessionManager)
            # Remove expired sessions. This should be done by a background
            # process. See the documentation for tasks and queues.
            sm.purgeExpiredSessions()
            # Get the current session.
            current_session = sm.getSession(self.request, self.response)
            # And increase the hit counter.
            if current_session.count:
                current_session.count += 1
            else:
                current_session.count = 1
            current_session.refresh()

        # The MainPage adapter takes a context and the request object. We write
        # its rendered output to the response object.
        page = MainPage(Context(current_session), self.request)
        self.response.out.write(page.render())


def application():
    """Returns WSGI application object."""

    # We register some request handlers for our application.
    app = google.appengine.ext.webapp.WSGIApplication([
        ('/', DemoRequestHandler), 
    ], debug=True)

    return app


def initGlobalSiteManager():
    """Inititalize the global site manager.

    We need a global site manager object to register adapters and utilities.
    Google App Engine caches the global site manager between requests.
    """

    global _global_site_manager

    if _global_site_manager is None:
        logging.debug("Creating global site manager")
        _global_site_manager = zope.component.getGlobalSiteManager()

        # Now we register an adapter.
        _global_site_manager.registerAdapter(CounterView,
                                (interfaces.IContext, interfaces.IRequest),
                                interfaces.ICounterView)

        # We need a global utility for managing sessions.
        sm = session.SessionManager('demo', Session, SessionProvider())
        _global_site_manager.registerUtility(sm)


def main():
    """The main function."""

    initGlobalSiteManager()
    wsgiref.handlers.CGIHandler().run(application())


if __name__ == '__main__':
    main()
