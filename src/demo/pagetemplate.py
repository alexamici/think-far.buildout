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
"""Using zope page templates."""

import os
import zope.interface
import zope.pagetemplate.pagetemplate


class PageTemplate(zope.pagetemplate.pagetemplate.PageTemplate):
    """Subclass of zope's PageTemplate."""

    zope.interface.implements(
                        zope.pagetemplate.interfaces.IPageTemplateSubclassing)

    def __init__(self, pt):
        """Initialize page template."""

        f = open(os.path.join(os.path.split(__file__)[0], pt), 'r')
        self.write(f.read())
        f.close()

    def pt_getContext(self, args=(), options={}, **ignored):
        """See zope.pagetemplate.interfaces.IPageTemplateSubclassing."""

        names = {'template': self,
                 'view': options.get('view', None),
                 'context': options.get('context', None),
                 'request': options.get('request', None),
                 'nothing': None,
                 }

        names.update(self.pt_getEngine().getBaseNames())

        return names
