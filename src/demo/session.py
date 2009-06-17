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

import interfaces
import logging
import zope.interface


class SessionManager(object):
    """The global session manager."""

    zope.interface.implements(interfaces.ISessionManager)

    def __init__(self, name):
        self.__name__ = name
        logging.info("Creating session manager")

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.__name__)
