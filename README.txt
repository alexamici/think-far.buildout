Copyright (c) 2010-2011 Alessandro Amici. All rights reserved.

=====================
Think-Far application
=====================

Dependencies
------------

 * Python 2.5

    sudo add-apt-repository ppa:fkrull/deadsnakes
    sudo apt-get update
    sudo apt-get -y install python2.5-dev build-essential

 * lndir

    sudo apt-get -y install xutils-dev

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

    ./bin/appcfg update ./app/

For a more detailed documentation follow this url::

    http://code.google.com/appengine/docs/python/tools/uploadinganapp.html

Uploading initial data to the remote server:

    ./bin/appcfg upload_data --config_file=bulkloader.yaml \
        --filename=src/thinkfar/data/AssetModel.csv --kind=AssetModel \
        ./app/

Testing
-------

Run all tests by typing the following command::

    ./bin/nosetests --with-doctest --doctest-extension=txt --with-gae \
        --gae-application=./app/ src/thinkfar/

optionally with HTML coverage:

    ./bin/nosetests --with-doctest --doctest-extension=txt --with-gae \
        --gae-application=./app/ --with-coverage --cover-package=thinkfar \
        --cover-html-dir=coverage/ --cover-html --cover-erase src/thinkfar/

then connect to:

    firefox ./coverage/index.html

Running pydoc
-------------

To run pydoc with the correct import paths enter following command::

    ./bin/python /path/to/python/bin/pydoc -p <PORT>
