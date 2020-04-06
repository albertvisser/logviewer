LogViewer
=========

Originally a PHP application in an attempt to build a quick and dirty something
to read my server logs from within my web browser,
rebuilt in Python using various web frameworks.

The Python version uses SQLite for storing its settings
and caching the currently selected logfile.


Usage
-----

Copy server config. Point to the chosen (local) domain after the following:

Use ``cherryd`` to run ``start_logviewer.py`` with the .conf file in this
directory.
In this configuration define the output to go to a specific port on localhost.
Configure your local webserver to pick up the output from the port and assign it
to a virtual domain. Have your hosts file translate the virtual domain to localhost.
Of course you can also pick up the output directly in the web browser by specifying
localhost:port.

Requirements
------------

- Python (with Sqlite) 
- CherryPy and Jinja2 for the current version
- Bottle and Flask for other Python versions
