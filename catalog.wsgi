#!/usr/bin/python
import os

app_path = os.path.dirname(os.path.realpath(__file__))
activate_this = app_path + '/env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,app_path)

from catalog.catalog import app as application
