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

from __future__ import with_statement

import Cookie
import hashlib
import interfaces
import logging
import random
import re
import threading
import time
import zope.interface


class Session(object):
    """Sessions allow associating information with individual visitors.

    This is a sample non-persistent implementation.
    """

    zope.interface.implements(interfaces.ISession)

    def __init__(self):
        self.id      = None
        self.expires = None
        self.refresh()

    def __repr__(self):
        return "Session(id='%s')" % self.id

    def refresh(self):
        self.expires = time.time() + 300


class SessionManager(object):
    """The global session manager.

    An instance of this class should be installed as a global utility. The
    constructor takes a number of arguments:

    name (required)
    Name of the session manager utility

    session_class (default=Session)
    Use this class to instantiate session objects

    dictionary (default=None)
    Store sessions into this dictionary-like object

    The session manager can use a custom session class to instantiate session
    objects as long as the supplied class provides the ISession interface.
    """

    zope.interface.implements(interfaces.ISessionManager)

    def __init__(self, name, session_class=Session, dictionary=None):
        self.__name__     = name
        self.cookie_name  = name + '_session'

        if not interfaces.ISession.implementedBy(session_class):
            raise TypeError, "The session class must implement ISession"
        self.session_cls  = session_class

        if dictionary:
            self.sessions = dictionary
        else:
            self.sessions = {}

        self.lock         = threading.Lock()
        logging.info("Creating session manager")

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.__name__)

    def purgeExpiredSessions(self):
        with self.lock:
            expired_sessions = []
            for s in self.sessions:
                if time.time() > self.sessions[s].expires:
                    expired_sessions.insert(0, s)
            while expired_sessions:
                del self.sessions[expired_sessions.pop()]

    def getSession(self, request, response):
        if not interfaces.IRequest.providedBy(request):
            raise TypeError, "%s must implement IRequest" % request
        if not interfaces.IResponse.providedBy(response):
            raise TypeError, "%s must implement IResponse" % response

        # Try to obtain a session id from a cookie.
        sid = request.cookies.get(self.cookie_name)
        session = None

        if sid:
            session = self.sessions.get(sid)

        if not session:
            # We need a new session id.
            m = hashlib.md5()
            m.update(str(time.time()+random.random()))
            sid = m.hexdigest()

            # Write a new cookie.
            c = Cookie.SimpleCookie()
            c[self.cookie_name] = sid
            h = re.compile('^Set-Cookie: ').sub('', c.output(), count=1)
            response.headers.add_header('Set-Cookie', str(h))

            # Create session object.
            session = self.session_cls()
            session.id = sid
            self.sessions[sid] = session

        session.refresh()

        return session
