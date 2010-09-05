=======================
Think-Far application
=======================

Running the application out of the box
--------------------------------------

Build and run the application::

  $ python bootstrap.py
  $ ./bin/buildout
  $ ./bin/demo parts/demo

Then access the application using a web browser with the following URL::

  http://localhost:8080/


Uploading and managing
----------------------

To upload application files, run::

  $ ./bin/appcfg update parts/demo

For a more detailed documentation follow this url::

  http://code.google.com/appengine/docs/python/tools/uploadinganapp.html


Testing
-------

Run all tests by typing the following command::

  $ ./bin/nosetests --with-doctest --doctest-extension=txt --with-gae \
      --gae-application=src/demo/ src/thinkfar/

Running pydoc
-------------

To run pydoc with the correct import paths enter following command::

  $ ./bin/python /path/to/python/bin/pydoc -p <PORT>
