"""LogViewer CherryPy version
"""
import sys
import time
import pathlib
import cherrypy
from jinja2 import Environment, FileSystemLoader
sys.path.insert(0, pathlib.Path(__file__).parent.resolve())
from readlog import init_db, rereadlog, get_data

env = Environment(loader=FileSystemLoader('templates'))
tmpl = env.get_template('viewlogs.html')


class Logviewer(object):
    """Application class
    """
    @cherrypy.expose
    def index(self, logfile='', entries='', order='', timestr=''):
        """load a log file and display a first page
        """
        try:
            test = self.timestr
        except AttributeError:
            self.timestr = str(int(time.time() * 10))
        if not logfile:
            init_db(self.timestr)
            # self.timestr = timestr
        else:
            rereadlog(logfile, entries, order, self.timestr)
        ## return str(get_data())
        return tmpl.render(**get_data(self.timestr))

    @cherrypy.expose
    def top(self):
        """Go to first displayable page
        """
        return tmpl.render(**get_data(self.timestr, 'first'))

    @cherrypy.expose
    def prev(self):
        """Go to prior displayable page
        """
        return tmpl.render(**get_data(self.timestr, 'prev'))

    @cherrypy.expose
    def next(self):
        """Go to next displayable page
        """
        return tmpl.render(**get_data(self.timestr, 'next'))

    @cherrypy.expose
    def bottom(self):
        """Go to last displayable page
        """
        return tmpl.render(**get_data(self.timestr, 'last'))

if __name__ == '__main__':
    cherrypy.quickstart(Logviewer())
