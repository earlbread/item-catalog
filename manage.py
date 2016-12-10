#!/usr/bin/env python

from flask_script import Manager
from catalog.catalog import app
from catalog.models import db

manager = Manager(app)

@manager.command
def createdb():
    db.create_all()

if __name__ == '__main__':
    manager.run()
