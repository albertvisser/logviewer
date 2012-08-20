#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from flask import Flask, request, render_template
app = Flask(__name__)
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from readlog import listlogs, init_db, rereadlog, get_data

@app.route('/')
def logviewer():
    ## if request:
        ## app.logger.debug('We have a request: {}'.format(str(request.args.__dict__)))
    logfile = request.args.get('logfile', '')
    entries = request.args.get('entries', '')
    order = request.args.get('order', '')
    ## app.logger.debug('log: {} entr: {} order: {}'.format(logfile, entries, order))
    if not logfile:
        ## app.logger.debug('init-ing db')
        init_db()
    else:
        rereadlog(logfile, entries, order)
    data = get_data()
    ## app.logger.debug('got data: ' + str(data))
    return render_template('viewlogs.html', **data)

@app.route('/top')
def first_page():
    return render_template('viewlogs.html', **get_data('first'))

@app.route('/prev')
def previous_page():
    return render_template('viewlogs.html', **get_data('prev'))

@app.route('/next')
def next_page():
    return render_template('viewlogs.html', **get_data('next'))

@app.route('/bottom')
def last_page():
    return render_template('viewlogs.html', **get_data('last'))

@app.route('/help')
def help():
    return static_file('help.html', root='.')

## @error(403)
## def mistake403(code):
    ## return 'The parameter you passed has the wrong format.'

## @error(404)
## def mistake404(code):
    ## return 'Sorry, this page does not exist.'

if __name__ == '__main__':
    app.run(debug=True)
