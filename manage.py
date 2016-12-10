#!/usr/bin/env python

from flask_script import Manager
from catalog.catalog import app

manager = Manager(app)

if __name__ == '__main__':
    manager.run()
