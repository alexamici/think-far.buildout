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
"""Interface definitions."""

import zope.interface


class IRequest(zope.interface.Interface):
    """Marker interface for request objects."""


class IResponse(zope.interface.Interface):
    """Marker interface for response objects."""


class IGreeting(zope.interface.Interface):
    """Marker interface for greetings."""


class IGreetingView(zope.interface.Interface):
    """Views for greetings should implement this interface."""

    def render():
        """Renders HTML output."""


class IPage(zope.interface.Interface):
    """Interface for pages."""

    def render():
        """Renders HTML output."""


class ISession(zope.interface.Interface):
    """Sessions allow associating information with individual visitors."""

    id      = zope.interface.Attribute("Unique session id")
    expires = zope.interface.Attribute("Expiration time as float")

    def refresh():
        """Refresh the session."""


class ISessionManager(zope.interface.Interface):
    """Interface for the global session manager."""

    def purge_sessions():
        """Deletes expired sessions."""

    def get_session(request, response):
        """Returns a session object."""
