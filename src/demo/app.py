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
import google.appengine.ext.db
import google.appengine.ext.webapp
import google.appengine.api
import interfaces
import logging
import os
import pagetemplate
import wsgiref.handlers
import zope.component
import zope.interface


GLOBAL_SITE_MANAGER = None  # The global site manager for registering adapters
                            # and utilities.


class Greeting(google.appengine.ext.db.Model):
    """Model declaration for greetings."""

    zope.interface.implements(interfaces.IGreeting)

    author  = google.appengine.ext.db.UserProperty()
    content = google.appengine.ext.db.StringProperty(multiline=True)
    date    = google.appengine.ext.db.DateTimeProperty(auto_now_add=True)


class GreetingsView(object):
    """View for greetings.

    This adapter is a view for greeting objects.
    """

    zope.interface.implements(interfaces.IGreetingsView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def render(self):
        output = ""
        if self.context.author:
            output += '<b>%s</b> wrote:' % self.context.author.nickname()
        else:
            output += 'An anonymous person wrote:'
        output += '<div>%s</div>' % cgi.escape(self.context.content)
        return output


class MainPage(object):
    """Implementation for the main page."""

    zope.interface.implements(interfaces.IPage)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def greetings(self):
        """Returns rendered greetings."""

        greetings = google.appengine.ext.db.GqlQuery("SELECT * "
                            "FROM Greeting "
                            "ORDER BY date DESC LIMIT 10")

        output = []

        for greeting in greetings:
            view = zope.component.getMultiAdapter((greeting, self.request),
                                                  interfaces.IGreetingsView)
            output.append(view.render())

        return u''.join(output)

    def render(self):
        """Writes rendered output to the response object."""
        template = pagetemplate.PageTemplate(
                        os.path.join(os.path.split(__file__)[0], 'index.pt'))

        return template(view=self, context=self.context, request=self.request)


class Guestbook(google.appengine.ext.webapp.RequestHandler):
    """The guestbook."""

    def get(self):
        """Handles GET."""

        # The Google App Engine request object must provide a special marker
        # interface to be adaptable.
        zope.interface.directlyProvides(self.request, interfaces.IRequest)

        # This is our main page.
        page = MainPage(self, self.request)
        # Let's write the rendered output to the resonse object.
        self.response.out.write(page.render())

    def post(self):
        """Handles POST."""

        greeting = Greeting()

        if google.appengine.api.users.get_current_user():
            greeting.author = google.appengine.api.users.get_current_user()

        greeting.content = self.request.get('content')
        greeting.put()
        self.redirect('/')


def application():
    """Returns WSGI application object."""

    # We register some request handlers for our application.
    app = google.appengine.ext.webapp.WSGIApplication([
        ('/', Guestbook), 
    ], debug=True)

    return app


def initGlobalSiteManager():
    """Inititalize the global site manager.

    We need a global site manager object to register adapters and utilities.
    Google App Engine caches the global site manager between requests.
    """

    global GLOBAL_SITE_MANAGER

    if GLOBAL_SITE_MANAGER is None:
        logging.info("Creating global site manager")
        GLOBAL_SITE_MANAGER = zope.component.getGlobalSiteManager()

        # Now we register an adapter.
        GLOBAL_SITE_MANAGER.registerAdapter(GreetingsView,
                                (interfaces.IGreeting, interfaces.IRequest),
                                interfaces.IGreetingsView)

def main():
    """The main function."""

    initGlobalSiteManager()
    wsgiref.handlers.CGIHandler().run(application())


if __name__ == '__main__':
    main()
