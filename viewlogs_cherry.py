#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import cherrypy
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))
tmpl = env.get_template('viewlogs.html')
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from readlog import listlogs, init_db, rereadlog, get_data

class Logviewer(object):

    @cherrypy.expose
    def index(self, logfile='', entries='', order=''):
        ## logfile = request.GET.get('logfile', '')
        ## entries = request.GET.get('entries', '')
        ## order = request.GET.get('order', '')
        if not logfile:
            init_db()
        else:
            rereadlog(logfile, entries, order)
        ## return str(get_data())
        return tmpl.render(**get_data())

    @cherrypy.expose
    def top(self):
        return tmpl.render(**get_data('first'))

    @cherrypy.expose
    def prev(self):
        return tmpl.render(**get_data('prev'))

    @cherrypy.expose
    def next(self):
        return tmpl.render(**get_data('next'))

    @cherrypy.expose
    def bottom(self):
        return tmpl.render(**get_data('last'))

    ## @cherrypy.expose
    ## def help(self):
        ## return static_file('help.html', root='.')

    ## @error(403)
    ## def mistake403(code):
        ## return 'The parameter you passed has the wrong format.'

    ## @error(404)
    ## def mistake404(code):
        ## return 'Sorry, this page does not exist.'

if __name__ == '__main__':
    cherrypy.quickstart(Logviewer())
