#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
#sys.stdout = sys.stderr
import cgitb
cgitb.enable()
import cherrypy

ROOT = os.path.dirname(os.path.abspath(__file__)) # '/home/albert/logviewer'
os.chdir(ROOT)
sys.path.insert(0, ROOT)
from viewlogs_cherry import Logviewer


cherrypy.config.update({'environment': 'embedded'})

application = cherrypy.tree.mount(Logviewer())
cherrypy.config.update({'engine.autoreload_on': False,
        })
