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
"""Lightweight implementation for session management."""

import Cookie
import hashlib
import interfaces
import logging
import random
import re
import time
import zope.interface


class Session(object):
    """Sessions allow associating information with individual visitors."""

    zope.interface.implements(interfaces.ISession)

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return "Session(id='%s')" % self.id


class SessionManager(object):
    """The global session manager."""

    zope.interface.implements(interfaces.ISessionManager)

    def __init__(self, name):
        self.__name__    = name
        self.cookie_name = name + '_session'
        self.sessions    = {}
        logging.info("Creating session manager")

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.__name__)

    def get_session(self, request, response):
        if not interfaces.IRequest.providedBy(request):
            raise TypeError, "%s must implement IRequest" % request
        if not interfaces.IResponse.providedBy(response):
            raise TypeError, "%s must implement IResponse" % response

        # Try to obtain a session id from a cookie.
        sid = request.cookies.get(self.cookie_name)

        if not sid:
            # We need a new session id.
            m = hashlib.md5()
            m.update(str(time.time()+random.random()))
            sid = m.hexdigest()

            # Write a new cookie.
            c = Cookie.SimpleCookie()
            c[self.cookie_name] = sid
            c[self.cookie_name]['expires'] = 10
            h = re.compile('^Set-Cookie: ').sub('', c.output(), count=1)
            response.headers.add_header('Set-Cookie', str(h))

        return Session(sid)
