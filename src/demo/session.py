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
import UserDict
import hashlib
import interfaces
import os
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


class SessionProvider(UserDict.IterableUserDict):
    """Simple session provider implementation."""

    zope.interface.implements(interfaces.ISessionProvider)

    def purgeExpired(self):
        now = time.time()
        expired = [s for s in self if now > self[s].expires]
        while expired:
            del self[expired.pop()]


class SessionManager(object):
    """The global session manager.

    An instance of this class should be installed as a global utility. The
    constructor takes a number of arguments:

    name (required)
    Name of the session manager utility

    session_class (default=Session)
    Use this class to instantiate session objects

    provider (default=None)
    Use this dictionary-like provider to store and query sessions

    The session manager can use a custom session class to instantiate session
    objects as long as the supplied class provides the ISession interface.
    """

    zope.interface.implements(interfaces.ISessionManager)

    def __init__(self, name, session_class=Session, provider=None):
        self.__name__     = name
        self.cookie_name  = name + '_session'

        if not interfaces.ISession.implementedBy(session_class):
            raise TypeError, "The session class must implement ISession"
        self.session_cls  = session_class

        if provider:
            if not interfaces.ISessionProvider.providedBy(provider):
                raise TypeError, "The provider must provide ISessionProvider"
            self.sessions = provider
        else:
            self.sessions = SessionProvider()

        self.lock         = threading.Lock()

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.__name__)

    def purgeExpiredSessions(self):
        with self.lock:
            self.sessions.purgeExpired()

    def getSession(self, request, response):
        if not interfaces.IRequest.providedBy(request):
            raise TypeError, "%s must provide IRequest" % request
        if not interfaces.IResponse.providedBy(response):
            raise TypeError, "%s must provide IResponse" % response

        # Try to obtain a session id from a cookie.
        cookie = os.environ.get('HTTP_COOKIE')
        session = None
        if cookie:
            sid = cookie[len(self.cookie_name)+1:]
            session = self.sessions.get(sid)

        if session:
            if session.expires <= time.time():
                session = None

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
