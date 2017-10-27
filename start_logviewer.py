#! /usr/bin/env python3
"""start Logviewer web application
"""
import sys
import os
import pathlib
# sys.stdout = sys.stderr
import cgitb
import cherrypy
from viewlogs_cherry import Logviewer
cgitb.enable()

ROOT = pathlib.Path(__file__).parent.resolve()  # '/home/albert/logviewer'
os.chdir(str(ROOT))
sys.path.insert(0, str(ROOT))

application = cherrypy.tree.mount(Logviewer())
cherrypy.config.update({'environment': 'embedded'})
cherrypy.config.update({'engine.autoreload_on': False})
