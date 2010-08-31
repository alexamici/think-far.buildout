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

import beaker.middleware
import chameleon.zpt.loader
import google.appengine.api
import google.appengine.ext.webapp
import google.appengine.ext.webapp.util
import interfaces
import logging
import os
import session
import wsgiref.handlers
import zope.component
import zope.interface

from thinkfar.gae import application as thinkfar_application

# The global site manager for registering adapters and utilities.
site_manager = None

template_path = os.path.dirname(__file__)
template_loader = chameleon.zpt.loader.TemplateLoader(
    template_path,
    auto_reload=os.environ.get('SERVER_SOFTWARE', '').startswith('Dev'))


class CounterView(object):
    """View for our counter."""

    zope.component.adapts(interfaces.IContext, interfaces.IRequest)
    zope.interface.implements(interfaces.ICounterView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def render(self):
        template = template_loader.load('counter.pt')
        return template(view=self, context=self.context, request=self.request)


class MainPage(object):
    """Implementation for the main page."""

    zope.component.adapts(interfaces.IContext, interfaces.IRequest)
    zope.interface.implements(interfaces.IPage)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def counter(self):
        """Returns counter."""

        view = zope.component.getMultiAdapter((self.context, self.request),
                                              interfaces.ICounterView)
        return view.render()

    def render(self):
        """Writes rendered output to the response object."""

        template = template_loader.load('index.pt')
        return template(view=self, context=self.context, request=self.request)


class Context(object):
    """Provides a simple context object."""

    zope.interface.implements(interfaces.IContext)

    def __init__(self, s):
        self.session = s


class MainRequestHandler(google.appengine.ext.webapp.RequestHandler):
    """The demo request handler."""

    def get(self):
        """Handles GET."""

        # The request object as well as the response object must provide a
        # special marker interface to be adaptable.
        zope.interface.directlyProvides(self.request, interfaces.IRequest)
        zope.interface.directlyProvides(self.response, interfaces.IResponse)

        # Get a valid session object by adapting the response.
        sess = interfaces.ISession(self.response)

        # Get a beaker session.
        beaker_sess = self.request.environ['beaker.session']

        # Increase the count and refresh our session.
        sess.count += 1
        sess.refresh()

        if not beaker_sess.has_key('count'):
            beaker_sess['count'] = 0
        beaker_sess['count'] += 1
        beaker_sess.save()

        # This is our context object. It holds the session.
        context = Context(sess)

        # Try to get a named multi adapter for a context object and the
        # request.
        page = zope.component.getMultiAdapter((context, self.request),
                                              interfaces.IPage, "index.html")

        # And write its rendered output to the response object.
        self.response.out.write(page.render())


def application():
    """Returns WSGI application object."""

    # We register some request handlers for our application.
    app = google.appengine.ext.webapp.WSGIApplication([
        ('/', MainRequestHandler), 
    ], debug=True)

    return app


def initGlobalSiteManager():
    """Inititalize the global site manager.

    We need a global site manager object to register adapters and utilities.
    Google App Engine caches the global site manager between requests.
    """

    global site_manager

    if site_manager is None:
        logging.debug("Creating global site manager")

        # Get a global site manager instance.
        site_manager = zope.component.getGlobalSiteManager()

        # Let's register our adapter factories.
        site_manager.registerAdapter(MainPage, name="index.html")
        site_manager.registerAdapter(CounterView)
        site_manager.registerAdapter(session.Session)


def removeGlobalSiteManager():
    """Deletes the global site manager instance."""

    global site_manager
    site_manager = None


def main():
    """The main function."""

    initGlobalSiteManager()

    session_opts = {
        'session.cookie_domain': 'localhost',
        'session.cookie_expires': True,
        'session.type': 'cookie',
        'session.validate_key': 'secret'
    }

    app = beaker.middleware.SessionMiddleware(thinkfar_application(), session_opts)

    google.appengine.ext.webapp.util.run_wsgi_app(app)


if __name__ == '__main__':
    main()
