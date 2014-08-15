# -*- coding: utf-8 -*-

import sys
import os
import glob
import sqlite3
from contextlib import closing
if sys.version < '3':
    from httplib import responses
else:
    from http.client import responses

LOGROOT = '/var/log/nginx'
DATABASE = '/tmp/loglines.db'

def listlogs():
    "bouw een lijst op van logfiles, meest recent aangepaste het eerst"
    lijst = []
    for item in glob.glob(os.path.join(LOGROOT, '*.log')):
        lijst.append((os.path.getctime(item), os.path.basename(item)))
    lijst.sort()
    lijst.reverse()
    return [x[1] for x in lijst]

def connect_db():
    return sqlite3.connect(DATABASE)

def init_db():
    """initialiseer de tabel met sessieparameters
    """
    with closing(connect_db()) as db:
        cur = db.cursor()
        cur.execute('DROP TABLE IF EXISTS parms;')
        cur.execute('CREATE TABLE parms (id INTEGER PRIMARY KEY, '
            'logfile STRING NOT NULL, entries INTEGER NOT NULL, '
            'current INTEGER NOT NULL, total INTEGER NOT NULL, '
            'ordering STRING NOT NULL, mld STRING NOT NULL);')
        db.commit()
        cur.execute('INSERT INTO parms VALUES (?, ?, ?, ?, ?, ?, ?)', (1, '', 10,
            0, 0, 'desc', ''))
        db.commit()

def rereadlog(logfile, entries, order):
    """read the designated logfile and store in temporary database
    """
    old_logfile, old_entries, old_order = logfile, entries, order
    with closing(connect_db()) as db:
        cur = db.cursor()
        try:
            data = cur.execute('SELECT logfile, entries, ordering FROM parms '
                'where id == 1')
        except sqlite3.OperationalError:
            init_db()
        else:
            for row in data:
                old_logfile, old_entries, old_order = row
                break
    if logfile == old_logfile and entries == old_entries and order == old_order:
        return
    with closing(connect_db()) as db:
        cur = db.cursor()
        cur.execute('UPDATE parms SET logfile = ?, entries = ? , ordering = ? '
            'WHERE id == 1', (logfile, entries, order))
        db.commit()
    fnaam = os.path.join(LOGROOT, logfile)
    with open(fnaam) as _in:
        data = _in.readlines()
    total = len(data)
    with closing(connect_db()) as db:
        cur = db.cursor()
        parms = cur.execute('SELECT ordering FROM parms where id == 1')
        for row in parms:
            order = row[0]
            break
        cur.execute('DROP TABLE IF EXISTS log;')
        cur.execute('CREATE TABLE log (id INTEGER PRIMARY KEY, '
            'line varchar(1000) NOT NULL);')
        db.commit()
        if order == 'desc':
             data.reverse()
        for ix, line in enumerate(data):
            cur.execute('INSERT INTO log VALUES (?, ?)', (ix + 1, line))
        db.commit()
        check = cur.execute('SELECT COUNT(*) FROM log;')
        for item in check:
            check = item[0]
            break
        if check != total:
            raise ValueError('Waarom dit verschil tussen {} and {}?'.format(total,
                check))
        else:
            cur.execute('UPDATE parms SET total = ? WHERE id == 1', (total,))
            db.commit()

def get_data(position='first'):
    outdict = {
        'loglist': listlogs(),
        'logfile': '',
        'order': '',
        'errorlog': False,
        'numentries': ('5','10','15','20','25','30'),
        'entries': '',
        'mld': '',
        'logdata': [],
        }
    with closing(connect_db()) as db:
        cur = db.cursor()
        try:
            data = cur.execute('SELECT logfile, entries, current, total, ordering, '
                'mld FROM parms where id == 1')
        except sqlite3.OperationalError:
            init_db()
            outdict['mld'] = 'No data available, try refreshing the display'
        else:
            for row in data:
                logfile, entries, current, total, order, mld = row
                break
            is_errorlog = True if 'error' in logfile else False
            outdict['logfile'] = logfile
            outdict['order'] = order
            outdict['errorlog'] = is_errorlog
            outdict['entries'] = str(entries)
            outdict['mld'] = mld
            if position == 'first':
                current = 1
            elif position == 'prev':
                newtop = current - entries
                if newtop > 0:
                    current = newtop
                else:
                    outdict['mld'] = 'Geen vorige pagina'
            elif position == 'next':
                newtop = current + entries
                if newtop <= total:
                    current = newtop
                else:
                    outdict['mld'] = 'Geen volgende pagina'
            elif position == 'last':
                current = int(total / entries) * entries + 1
            cur.execute('UPDATE parms SET current = ? WHERE id == 1', (current,))
            db.commit()

            if logfile:
                lines = cur.execute('SELECT line FROM log '
                    'WHERE id BETWEEN {} and {}'.format(current,
                        current + entries - 1))
                for line in lines:
                    if is_errorlog:
                        parts = showerror(line[0])
                    else:
                        parts = showaccess(line[0])
                    outdict['logdata'].append(parts)
            start = len(outdict['logdata'])
            for i in range(start, entries):
                outdict['logdata'].append({'client': '', 'date': '', 'data': ''})
    return outdict

def showerror(text):
    errortypes = ('[notice]', '[error]')
    client, date, data = '', '', ''
    for item in errortypes:
        if item in text:
            date, data = text.split(item)
            # add error type back to message
            error = item[1:-1]
            data = error + data
            break
    if not date:
        # regular cherrypy error log lines start with the date between square brackets
        test = text.split('] ', 1)
        if len(test) == 2 and test[0].startswith('['):
            date, text = test
            date = date[1:]
        data = text
    if ', client' in data:
        data, client = data.split(', client')
        client = 'client' + client
    parts = {"client": client, "date": date, "data": data}
    return parts

def showaccess(text):
    parts = {'client': '', 'date': '', 'data': ''}
    parsed = text.split(' -', 2)
    parts['client'] = parsed[0]
    if len(parsed) > 1:
        parsed = parsed[-1].split(' [',1)
        if len(parsed) > 1:
            parsed = parsed[1].split('] "', 1)
            parts['date'] = parsed[0]
            if len(parsed) > 1:
                parsed = parsed[1].split('" ', 1)
                data = parsed[0]
                if len(parsed) > 1:
                    parsed = parsed[1].split(' ', 1)
                    parts['data'] = '{} {}: {}'.format(parsed[0],
                        responses[int(parsed[0])], data)
                else:
                    parts['data'] = data
    return parts
