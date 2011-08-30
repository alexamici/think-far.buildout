import logging

logging.getLogger().setLevel(logging.INFO)

import sys,os

sys.path.insert(0,'lib/dist')

from google.appengine.ext.webapp.util import run_wsgi_app

from thinkfar.run import app

settings = {
    'reload_templates': 'true',
    'debug_authorization': 'true',
    'debug_notfound': 'true',
    'debug_templates': 'true',
    'default_locale_name': 'en',
}

def main():
    """ This function runs a Pyramid WSGI application.
    """
    run_wsgi_app(app())


if __name__ == '__main__':
  main() 
