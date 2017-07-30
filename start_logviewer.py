#! /usr/bin/env python3
"""start Logviewer web application
"""
import sys
import os
# sys.stdout = sys.stderr
import cgitb
import cherrypy
from viewlogs_cherry import Logviewer
cgitb.enable()

ROOT = os.path.dirname(os.path.abspath(__file__))  # '/home/albert/logviewer'
os.chdir(ROOT)
sys.path.insert(0, ROOT)

application = cherrypy.tree.mount(Logviewer())
cherrypy.config.update({'environment': 'embedded'})
cherrypy.config.update({'engine.autoreload_on': False})
