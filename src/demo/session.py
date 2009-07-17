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
import binascii
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


def lookupowner(klass, attr):
    """Returns first possible owner.

    >>> class C:
    ...     i = 0
    >>> class D(C):
    ...     pass
    >>> assert lookupowner(D, int) == C
    >>> class E:
    ...     pass
    >>> assert lookupowner(E, int) == None
    >>> class F(D):
    ...     pass
    >>> assert lookupowner(F, int) == D
    >>> class G(E, C, F):
    ...     pass
    >>> assert lookupowner(G, int) == C
    """

    attrs = [type(v) for v in klass.__dict__.values()]
    if attr not in attrs:
        for c in klass.__bases__:
            if lookupowner(c, attr) is not None:
                return c
    else:
        return klass


class SessionPropertyCookie(object):
    """Session property implementation.

    Stores keys and values in cookies.

    >>> import wsgiref
    >>> class TestResponse(object):
    ...     def __init__(self):
    ...         self.__wsgi_headers = []
    ...         self.headers = wsgiref.headers.Headers(self.__wsgi_headers)
    >>> class Foo(object):
    ...     s = SessionPropertyCookie(str)
    ...     def __init__(self, response):
    ...         self.response = response
    >>> foo = Foo(TestResponse())
    >>> foo.s
    ''
    >>> foo.s = 'test'
    >>> foo.s
    'test'
    >>> import os
    >>> os.environ['HTTP_COOKIE'] = DEFAULT_SESSION_KEY_PREFIX + 's' + '=76616c'
    >>> foo = Foo(TestResponse())
    >>> foo.s
    'val'
    >>> class Baz:
    ...     s = SessionPropertyCookie(str)
    >>> baz = Baz()
    >>> baz.s
    Traceback (most recent call last):
    ...
    AttributeError: Baz instance has no attribute 'response'
    >>> class Base:
    ...     pass
    >>> class MyFoo(Base, Foo):
    ...     pass
    >>> myfoo = MyFoo(TestResponse())
    >>> myfoo.s = 'new value'
    >>> myfoo.s
    'new value'
    """
        
    def __init__(self, t):
        self.type = t

    def attrname(self, instance):
        owner = lookupowner(instance.__class__, self.__class__)
        for k in owner.__dict__:
            if isinstance(owner.__dict__[k], self.__class__):
                if owner.__dict__[k] == self:
                    return k

    def encode(self, value):
        if self.type == str:
            return binascii.hexlify(value)
        return self.type(value)

    def decode(self, value):
        if self.type == str:
            return binascii.unhexlify(value)
        return self.type(value)

    def __set__(self, instance, value):
        v = self.encode(value)
        c = Cookie.SimpleCookie()
        c[DEFAULT_SESSION_KEY_PREFIX+self.attrname(instance)] = v
        h = re.compile('^Set-Cookie: ').sub('', c.output(), count=1)
        instance.response.headers.add_header('Set-Cookie', str(h))

    def __get__(self, instance, owner):
        data = instance.response.headers.get_all('Set-Cookie')
        cookies = getdict(data)
        name = DEFAULT_SESSION_KEY_PREFIX + self.attrname(instance)
        if name in cookies:
            return self.decode(cookies[name])
        if 'HTTP_COOKIE' in os.environ:
            data = [c.strip() for c in os.environ.get('HTTP_COOKIE').split(';')]
        else:
            data = []
        cookies = getdict(data)
        if name in cookies:
            return self.decode(cookies[name])
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
