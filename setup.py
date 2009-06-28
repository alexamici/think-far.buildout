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
"""Setup script."""

import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup (
    name='demo',
    version='1.0.0',
    author="Tobias Rodaebel",
    author_email="tobias.rodaebel@googlemail.com",
    description="Demonstrates how to use the Zope Component Architecture "
                "within Google App Engine.",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license="GPL3",
    keywords="zope gae appengine",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Zope3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        ],
    url='',
    packages=find_packages('src/demo'),
    include_package_data=True,
    package_dir = {'':'src/demo'},
    install_requires=[
        'setuptools',
        'zope.component',
        'zope.interface',
        'zope.pagetemplate',
        ],
    zip_safe=False,
    )
