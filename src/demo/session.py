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
"""Lightweight session implementation."""

import Cookie
import hashlib
import interfaces
import os
import random
import re
import time
import zope.component
import zope.interface

DEFAULT_SESSION_KEY_PREFIX = 'session_'
DEFAULT_SESSION_LIFETIME   = 300


def getdict(data):
    """Returns dictionary from key-value pairs in given data.

    >>> getdict(['foo=bar', 'number=42'])
    {'foo': 'bar', 'number': '42'}
    """

    d = {}
    for e in data:
        k, v = e.split('=')
        d[k] = v
    return d


def _lookupowner(attr, class_):
    """Returns first possible owner.

    >>> class C:
    ...     i = 0
    >>> class D(C):
    ...     pass
    >>> assert _lookupowner(int, D) == C
    >>> class E:
    ...     pass
    >>> assert _lookupowner(int, E) == None
    >>> class F(D):
    ...     pass
    >>> assert _lookupowner(int, F) == D
    >>> class G(E, C, F):
    ...     pass
    >>> assert _lookupowner(int, G) == C
    """

    vtypes = [type(v) for v in class_.__dict__.values()]
    if attr not in vtypes:
        for c in class_.__bases__:
            if _lookupowner(attr, c) is not None:
                return c
    else:
        return class_


class SessionPropertyCookie(object):
    """Session property implementation.

    Stores keys and values in cookies.

    >>> import wsgiref
    >>> class TestResponse(object):
    ...     def __init__(self):
    ...         self.__wsgi_headers = []
    ...         self.headers = wsgiref.headers.Headers(self.__wsgi_headers)
    >>> class Foo:
    ...     p = SessionPropertyCookie(str)
    ...     def __init__(self, response):
    ...         self.response = response
    >>> foo = Foo(TestResponse())
    >>> foo.p
    ''
    >>> foo.p = 'test'
    >>> foo.p
    'test'
    >>> import os
    >>> os.environ['HTTP_COOKIE'] = DEFAULT_SESSION_KEY_PREFIX + 'p' + '=baz'
    >>> foo = Foo(TestResponse())
    >>> foo.p
    'baz'
    >>> class Baz:
    ...     p = SessionPropertyCookie(str)
    >>> baz = Baz()
    >>> baz.p
    Traceback (most recent call last):
    ...
    AttributeError: Baz instance has no attribute 'response'
    """
        
    def __init__(self, type_):
        self.type = type_

    @classmethod
    def _name(cls, self, instance):
        owner = _lookupowner(cls, instance.__class__)
        for k in owner.__dict__:
            if isinstance(owner.__dict__[k], cls):
                if owner.__dict__[k] == self:
                    return DEFAULT_SESSION_KEY_PREFIX + k
 
    def __set__(self, instance, value):
        c = Cookie.SimpleCookie()
        c[self._name(self, instance)] = value
        h = re.compile('^Set-Cookie: ').sub('', c.output(), count=1)
        instance.response.headers.add_header('Set-Cookie', str(h))
 
    def __get__(self, instance, owner):
        data = instance.response.headers.get_all('Set-Cookie')
        cookies = getdict(data)
        name = self._name(self, instance)
        if name in cookies:
            return self.type(cookies[name])
        if 'HTTP_COOKIE' in os.environ:
            data = [c.strip() for c in os.environ.get('HTTP_COOKIE').split(';')]
        else:
            data = []
        cookies = getdict(data)
        if name in cookies:
            result = self.type(cookies[name])
            return result
        return self.type()
 

def FloatProperty():
    return SessionPropertyCookie(float)


def IntegerProperty():
    return SessionPropertyCookie(int)


def StringProperty():
    return SessionPropertyCookie(str)


class Session(object):
    """Sessions allow associating information with individual visitors.

    This session class works as an adapter for a request-response pair. The
    session properties will be stored as simple cookies.

    >>> import wsgiref
    >>> class TestResponse(object):
    ...     def __init__(self):
    ...         self.__wsgi_headers = []
    ...         self.headers = wsgiref.headers.Headers(self.__wsgi_headers)
    >>> s = Session(TestResponse())
    >>> assert s.count == 0
    >>> s.count += 1
    >>> assert s.count == 1
    >>> assert s.expires == 0.0
    >>> s.refresh()
    >>> assert s.expires > 0.0
    >>> assert type(s.id) == str
    """

    zope.component.adapts(interfaces.IResponse)
    zope.interface.implements(interfaces.ISession)

    count   = IntegerProperty()
    expires = FloatProperty()
    id      = StringProperty()

    def __init__(self, response):
        self.response = response
        if self.id == '':
            # We need a new session id.
            m = hashlib.md5()
            m.update(str(time.time()+random.random()))
            self.id = m.hexdigest()

    def refresh(self):
        self.expires = time.time() + DEFAULT_SESSION_LIFETIME

    def __repr__(self):
        return "Session(id='%s')" % self.id

    def __call__(self):
        return repr(self)
