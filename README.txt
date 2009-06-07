=======================
Bridal demo application
=======================

This application demonstrates the usage of various zope packages within Google
App Engine.


Running the application out of the box
--------------------------------------

Build and run the application::

  $ python bootstrap.py
  $ ./bin/buildout
  $ ./bin/demo parts/demo

Then access the application using a web browser with the following URL::

  http://localhost:8080/


Testing
-------

Run all tests by typing the following command::

  $ ./bin/nosetests -c nose.cfg
