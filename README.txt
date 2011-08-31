=====================
Think-Far application
=====================

Running the application out of the box
--------------------------------------

Build and run the application::

    python2.5 bootstrap.py
    ./bin/buildout -nv
    ./bin/dev_appserver

Then access the application using a web browser with the following URL::

    http://localhost:8080/


Uploading and managing
----------------------

To upload application files, run::

    ./bin/appcfg update ./app

For a more detailed documentation follow this url::

    http://code.google.com/appengine/docs/python/tools/uploadinganapp.html

Uploading initial data to the remote server:

    ./bin/appcfg upload_data --config_file=bulkloader.yaml \
        --filename=src/thinkfar/data/AssetModel.csv --kind=AssetModel \
        ./app

Testing
-------

Run all tests by typing the following command::

    ./bin/nosetests --with-doctest --doctest-extension=txt --with-gae \
        --gae-application=src/demo/ src/thinkfar/

optionally with HTML coverage:

    ./bin/nosetests --with-doctest --doctest-extension=txt --with-gae \
        --gae-application=src/demo/ --with-coverage --cover-package=thinkfar \
        --cover-html-dir=coverage/ --cover-html --cover-erase src/thinkfar/

then connect to:

    firefox ./coverage/index.html

Running pydoc
-------------

To run pydoc with the correct import paths enter following command::

    ./bin/python /path/to/python/bin/pydoc -p <PORT>
