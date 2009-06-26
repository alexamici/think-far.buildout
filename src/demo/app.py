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
import os
import pagetemplate
import session
import time
import urllib
import wsgiref.handlers
import zope.component
import zope.interface


_global_site_manager = None  # The global site manager for registering adapters
                             # and utilities.


def globalSiteManager():
    """Returns global site manager."""

    return _global_site_manager


class Greeting(google.appengine.ext.db.Model):
    """Model declaration for greetings."""

    zope.interface.implements(interfaces.IGreeting)

    author  = google.appengine.ext.db.UserProperty()
    content = google.appengine.ext.db.StringProperty(multiline=True)
    date    = google.appengine.ext.db.DateTimeProperty(auto_now_add=True)


class Session(google.appengine.ext.db.Model):
    """Persistent session implementation."""

    zope.interface.implements(interfaces.ISession)

    id      = google.appengine.ext.db.StringProperty()
    data    = google.appengine.ext.db.ByteStringProperty()
    expires = google.appengine.ext.db.FloatProperty()

    def __repr__(self):
        return "Session(id='%s')" % self.id

    def refresh(self):
        self.expires = time.time() + 300
        self.put()


class SessionRetrieval(object):
    """Dictionary-like implementation for querying sessions."""

    zope.interface.implements(interfaces.ISessionRetrieval)

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
        session = self.get(key)
        if session:
            session.delete()
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


class GreetingView(object):
    """View for greetings."""

    zope.interface.implements(interfaces.IGreetingView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def render(self):
        output = ['<p>']
        if self.context.author:
            output.append('<b>%s</b> wrote:' % self.context.author.nickname())
        else:
            output.append('An anonymous person wrote:')
        output.append('<br />')
        output.append(cgi.escape(self.context.content))
        output.append('</p>')
        return u''.join(output)


class MainPage(object):
    """Implementation for the main page."""

    zope.interface.implements(interfaces.IPage)

    template = pagetemplate.PageTemplate(
                    os.path.join(os.path.split(__file__)[0], 'index.pt'))

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def greetings(self):
        """Returns rendered greetings."""

        greetings = google.appengine.ext.db.GqlQuery(
                                "SELECT * FROM Greeting "
                                "ORDER BY date DESC LIMIT 10")

        output = []

        for greeting in greetings:
            view = zope.component.getMultiAdapter((greeting, self.request),
                                                  interfaces.IGreetingView)
            output.append(view.render())

        return u''.join(output)

    def status(self):
        """Returns a status message by parsing the query string."""

        return self.request.get(u'status')

    def render(self):
        """Writes rendered output to the response object."""

        return self.template(view=self,
                             context=self.context,
                             request=self.request)


class Context(object):
    """Provides a simple context object."""

    def __init__(self, session):
        self.session = session


class DemoRequestHandler(google.appengine.ext.webapp.RequestHandler):
    """The demo request handler."""

    def get(self):
        """Handles GET."""

        # The request object as well as the response object must provide a
        # special marker interface to be adaptable.
        zope.interface.directlyProvides(self.request, interfaces.IRequest)
        zope.interface.directlyProvides(self.response, interfaces.IResponse)

        session = None

        # Lookup our session manager.
        if _global_site_manager:
            sm = _global_site_manager.getUtility(interfaces.ISessionManager)
            # Remove expired sessions. This should be done by a background
            # process. See the documentation for tasks and queues.
            sm.purgeExpiredSessions()
            # Get a session.
            session = sm.getSession(self.request, self.response)

        # The MainPage adapter takes a context and the request object. We write
        # its rendered output to the response object.
        page = MainPage(Context(session), self.request)
        self.response.out.write(page.render())

    def post(self):
        """Handles POST."""

        # Get contents from the request.
        content = self.request.get('content')

        if content:
            # So we create a greeting instance.
            greeting = Greeting()

            if google.appengine.api.users.get_current_user():
                greeting.author = google.appengine.api.users.get_current_user()

            greeting.content = content

            # And put it to the db.
            greeting.put()

            self.redirect('/')
            return

        self.redirect('/?status=%s' % urllib.quote('Enter some text!'))


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
        _global_site_manager.registerAdapter(GreetingView,
                                (interfaces.IGreeting, interfaces.IRequest),
                                interfaces.IGreetingView)

        # We need a global utility for managing sessions.
        sm = session.SessionManager('demo', Session, SessionRetrieval())
        _global_site_manager.registerUtility(sm)


def main():
    """The main function."""

    initGlobalSiteManager()
    wsgiref.handlers.CGIHandler().run(application())


if __name__ == '__main__':
    main()
