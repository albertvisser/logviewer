# -*- coding: utf-8 -*-
"""LogViewer Flask version
"""
import os
from flask import Flask, request, render_template
app = Flask(__name__)
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from readlog import init_db, rereadlog, get_data

timestr = str(int(time.time() * 10))


@app.route('/')
def logviewer():
    """load a log file and display a first page
    """
    ## if request:
        ## app.logger.debug('We have a request: {}'.format(str(request.args.__dict__)))
    logfile = request.args.get('logfile', '')
    entries = request.args.get('entries', '')
    order = request.args.get('order', '')
    ## app.logger.debug('log: {} entr: {} order: {}'.format(logfile, entries, order))
    if not logfile:
        ## app.logger.debug('init-ing db')
        init_db(timestr)
    else:
        rereadlog(logfile, entries, order, timestr)
    data = get_data(timestr)
    ## app.logger.debug('got data: ' + str(data))
    return render_template('viewlogs.html', **data)


@app.route('/top')
def first_page():
    """Go to first displayable page
    """
    return render_template('viewlogs.html', **get_data('first'))


@app.route('/prev')
def previous_page():
    """Go to prior displayable page
    """
    return render_template('viewlogs.html', **get_data('prev'))


@app.route('/next')
def next_page():
    """Go to next displayable page
    """
    return render_template('viewlogs.html', **get_data('next'))


@app.route('/bottom')
def last_page():
    """Go to last displayable page
    """
    return render_template('viewlogs.html', **get_data('last'))


## @app.route('/help')
## def help():
    ## return static_file('help.html', root='.')


## @error(403)
## def mistake403(code):
    ## return 'The parameter you passed has the wrong format.'


## @error(404)
## def mistake404(code):
    ## return 'Sorry, this page does not exist.'

if __name__ == '__main__':
    app.run(debug=True)
