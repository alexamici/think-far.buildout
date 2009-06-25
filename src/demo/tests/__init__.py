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
import demo.interfaces
import demo.session
import nose.tools
import os
import time
import urllib
import webtest
import zope.component

app = webtest.TestApp(demo.app.application())


def setup_func():
    """Set up test fixtures."""

    # We need a global site manager to register our greetings view.
    demo.app.initGlobalSiteManager()

    # For some reason the test expects following environment variable
    # to be set.
    os.environ['USER_EMAIL'] = 'foo@bar.net'


def teardown_func():
    """Tear down test fixtures."""

    demo.app._global_site_manager = None


def test_index():
    """Testing whether our application responds"""

    response = app.get('/')
    nose.tools.assert_equal(response.status, '200 OK')


@nose.tools.with_setup(setup_func, teardown_func)
def test_post():
    """Posting greeting"""

    app.post('/', {'content':'foobar'})
    response = app.get('/')
    assert '<p><b>foo@bar.net</b> wrote:<br />foobar</p>\n' in response.body


@nose.tools.with_setup(setup_func, teardown_func)
def test_post_empty():
    """Posting empty greeting"""

    response = app.post('/')
    nose.tools.assert_equal('http://localhost/?status=%s' % 
                            urllib.quote('Enter some text!'),
                            response.location)


def test_session_manager():
    """Testing session manager"""

    session_manager = demo.session.SessionManager('test')
    assert repr(session_manager) == "SessionManager(test)"


def test_session_manager_with_session():
    """Testing simple non-persistent sessions"""

    # Create a session which expires right after creation.
    session = demo.session.Session()
    session.id = 'mesession'
    session.expires = time.time()
    assert repr(session) == "Session(id='mesession')"

    # Create a session storage to store our session.
    storage = demo.session.SessionStorage()
    storage['mesession'] = session
    assert len(storage) == 1

    # Purge expired sessions.
    storage.purgeExpired()

    # Store our session again.
    storage['mesession'] = session
    assert len(storage) == 1

    # Check the session manager api.
    sm = demo.session.SessionManager('test', storage=storage)
    sm.purgeExpiredSessions()
    assert len(sm.sessions) == 0


@nose.tools.raises(TypeError)
def test_session_manager_with_wrong_storage():
    """Testing session manager with wrong storage"""

    demo.session.SessionManager('test', storage=type)


@nose.tools.raises(TypeError)
def test_session_manager_with_wrong_session_class():
    """Testing session manager with wrong session class"""

    session_manager = demo.session.SessionManager('test', session_class=type)


@nose.tools.raises(TypeError)
def test_session_manager_with_wrong_request():
    """Testing session manager with wrong request"""

    session_manager = demo.session.SessionManager('test')
    session_manager.getSession(object(), object())


@nose.tools.raises(TypeError)
def test_session_manager_with_wrong_response():
    """Testing session manager with wrong response"""

    session_manager = demo.session.SessionManager('test')
    class DummyRequest:
        zope.interface.implements(demo.interfaces.IRequest)
    request = DummyRequest()
    session_manager.getSession(request, object())


@nose.tools.with_setup(setup_func, teardown_func)
def test_persistent_sessions():
    """Testing persistent sessions"""

    # Get the session manager.
    site_manager    = demo.app.globalSiteManager()
    session_manager = site_manager.getUtility(demo.interfaces.ISessionManager)

    # Create a session.
    app.get('/')
    assert len(session_manager.sessions) == 1
