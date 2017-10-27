# -*- coding: utf-8 -*-
"""LogViewer Bottle version
"""
import pathlib
from bottle import route, run, debug, template, request, static_file  # , validate, error
import sys
sys.path.insert(0, pathlib.Path(__file__).parent.resolve()
from readlog import init_db, rereadlog, get_data

timestr = str(int(time.time() * 10))


@route('/')
def logviewer():
    """load a log file and display a first page
    """
    logfile = request.GET.get('logfile', '')
    entries = request.GET.get('entries', '')
    order = request.GET.get('order', '')
    if not logfile:
        init_db(timestr)
    else:
        rereadlog(logfile, entries, order, timestr)
    ## return str(get_data())
    return template('viewlogs', get_data(timestr))


@route('/top')
def first_page():
    """Go to first displayable page
    """
    return template('viewlogs', get_data('first'))


@route('/prev')
def previous_page():
    """Go to prior displayable page
    """
    return template('viewlogs', get_data('prev'))


@route('/next')
def next_page():
    """Go to nextt displayable page
    """
    return template('viewlogs', get_data('next'))


@route('/bottom')
def last_page():
    """Go to last displayable page
    """
    return template('viewlogs', get_data('last'))


@route('/help')
def help():
    """show help page
    """
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
