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


class ISession(zope.interface.Interface):
    """Sessions allow associating information with individual visitors."""

    expires = zope.interface.Attribute("Expiration time as floating point "
                                       "number since the epoch (UTC)")
    id      = zope.interface.Attribute("Unique session id")

    def refresh():
        """Refresh the session."""


class ICounterView(zope.interface.Interface):
    """Interface definition for the counter view."""

    def render():
        """Renders HTML output."""


class IPage(zope.interface.Interface):
    """Interface for pages."""

    def render():
        """Renders HTML output."""


class IContext(zope.interface.Interface):
    """Market interface for context objects."""
