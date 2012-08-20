#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from bottle import route, run, debug, template, request, validate, static_file, error
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from readlog import listlogs, init_db, rereadlog, get_data

@route('/')
def logviewer():
    logfile = request.GET.get('logfile', '')
    entries = request.GET.get('entries', '')
    order = request.GET.get('order', '')
    if not logfile:
        init_db()
    else:
        rereadlog(logfile, entries, order)
    ## return str(get_data())
    return template('viewlogs', get_data())

@route('/top')
def first_page():
    return template('viewlogs', get_data('first'))

@route('/prev')
def previous_page():
    return template('viewlogs', get_data('prev'))

@route('/next')
def next_page():
    return template('viewlogs', get_data('next'))

@route('/bottom')
def last_page():
    return template('viewlogs', get_data('last'))

@route('/help')
def help():
    return static_file('help.html', root='.')

## @error(403)
## def mistake403(code):
    ## return 'The parameter you passed has the wrong format.'

## @error(404)
## def mistake404(code):
    ## return 'Sorry, this page does not exist.'

if __name__ == '__main__':
    debug(True)
    run(reloader=True, port=9002)
