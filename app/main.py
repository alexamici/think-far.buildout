import logging

logging.getLogger().setLevel(logging.INFO)

import sys,os

sys.path.insert(0,'lib/dist')

from google.appengine.ext.webapp.util import run_wsgi_app

from thinkfar.run import app

# No idea what it does, but solves a pkg_resource NullProvider issue
# taken stright from a comment to: http://code.google.com/p/bfg-pages/wiki/PyramidTutorial
try:
    import pkg_resources
except ImportError:
    pass
else:
    if hasattr(os, '__loader__'):
        # This only seems to apply to the SDK
        pkg_resources.register_loader_type(type(os.__loader__), pkg_resources.DefaultProvider)

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
