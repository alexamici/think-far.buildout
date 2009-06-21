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


class SessionManager(object):
    """The global session manager."""

    zope.interface.implements(interfaces.ISessionManager)

    def __init__(self, name):
        self.__name__ = name
        self.sessions = {}
        logging.info("Creating session manager")

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.__name__)

    def get_session(self, request, response):
        if not interfaces.IRequest.providedBy(request):
            raise TypeError, "%s must implement IRequest" % request
        if not interfaces.IResponse.providedBy(response):
            raise TypeError, "%s must implement IResponse" % response

        sid = request.cookies.get('__demo')

        if sid:
            logging.info(sid)
        else:
            m = hashlib.md5()
            m.update(str(time.time()+random.random()))
            sid = m.hexdigest()
            c = Cookie.SimpleCookie()
            c['__demo'] = sid
            c['__demo']['expires'] = 600
            h = c.output()
            re_obj = re.compile('^Set-Cookie: ')
            response.headers.add_header('Set-Cookie',
                                        str(re_obj.sub('', h, count=1)))

        # TODO: Creating and returning session objects.
        return None
