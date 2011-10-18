import logging

logging.getLogger().setLevel(logging.INFO)

import sys,os

sys.path.insert(0,'lib/dist')

from thinkfar.run import app


def main():
    app.run()

if __name__ == '__main__':
    main()
