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
"""Testing demo."""

import demo.app
import nose.tools
import os
import webtest

app = webtest.TestApp(demo.app.application())


def setup_func():
    """Set up test fixtures."""

    # We need a global site manager.
    demo.app.initGlobalSiteManager()


def teardown_func():
    """Tear down test fixtures."""

    demo.app.removeGlobalSiteManager()


def test_main():
    """Tries to call the main function"""

    demo.app.main()


@nose.tools.with_setup(setup_func, teardown_func)
def test_index():
    """Testing whether our application responds"""

    response = app.get('/')
    nose.tools.assert_equal(response.status, '200 OK')


@nose.tools.with_setup(setup_func, teardown_func)
def test_sessions():
    """Testing sessions"""
