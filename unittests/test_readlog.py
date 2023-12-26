# import os
import types
import pytest
import readlog


def test_listlogs(monkeypatch, capsys):
    def mock_stat(self, *args):
        nonlocal counter
        counter += 1
        return types.SimpleNamespace(st_ctime='changetime{counter}')
    monkeypatch.setattr(readlog.pathlib.Path, 'iterdir', lambda x: [readlog.pathlib.Path('log1.log'),
                                                                    readlog.pathlib.Path('geen-log'),
                                                                    readlog.pathlib.Path('log2.log')])
    monkeypatch.setattr(readlog.pathlib.Path, 'stat',mock_stat)
    counter = 0
    assert readlog.listlogs() == ['log2.log', 'log1.log']


def test_connect_db(monkeypatch, capsys):
    monkeypatch.setattr(readlog.sqlite3, 'connect', lambda x: x)
    assert readlog.connect_db('xxx') == '/tmp/loglines_xxx.db'


class MockCursor(readlog.sqlite3.Cursor):
    def execute(self, *args):
        print('executing', *args)


class MockConnection(readlog.sqlite3.Connection):
    def cursor(self, *args, **kwargs):
        return MockCursor(self, *args, **kwargs)
    def commit(self, *args):
        print('executing commit')
    def close(self, *args):
        print('executing close')


def test_init_db(monkeypatch, capsys):
    def mock_connect(*args):
        print(f"connecting to database identified by '{args[0]}'")
        return MockConnection(*args)
    monkeypatch.setattr(readlog, 'connect_db', mock_connect)
    monkeypatch.setattr(readlog.sqlite3, 'Connection', MockConnection)
    # breakpoint()
    readlog.init_db('xxx')
    assert capsys.readouterr().out == (
            "connecting to database identified by 'xxx'\n"
            'executing DROP TABLE IF EXISTS parms;\n'
            'executing CREATE TABLE parms (id INTEGER PRIMARY KEY, logfile STRING NOT NULL,'
            ' entries INTEGER NOT NULL, current INTEGER NOT NULL, total INTEGER NOT NULL,'
            ' ordering STRING NOT NULL, mld STRING NOT NULL);\n'
            'executing commit\n'
            "executing INSERT INTO parms VALUES (?, ?, ?, ?, ?, ?, ?) (1, '', 10, 0, 0, 'desc', '')\n"
            'executing commit\n'
            'executing close\n')


def test_startswith_date(monkeypatch, capsys):
    assert readlog.startswith_date('bladibla') is False
    assert readlog.startswith_date('bla dibla') is False
    assert readlog.startswith_date('[bladibla') is False
    assert readlog.startswith_date('[bla dibla') is False
    assert readlog.startswith_date('2022/03/10') is False
    assert readlog.startswith_date('2022/03/10 more data') is True
    assert readlog.startswith_date('[10/Mar/2022') is False
    assert readlog.startswith_date('[10/Mar/2022:more data') is True


def test_rereadlog(monkeypatch, capsys, tmp_path):
    def mock_read_parms(*args):
        print('called read_and_set_parms with args', args)
    monkeypatch.setattr(readlog, 'read_and_set_parms', mock_read_parms)
    def mock_check(lines):
        print(f'called check_for_python_tracebacks with arg `{lines}`')
        return lines
    monkeypatch.setattr(readlog, 'check_for_python_tracebacks', mock_check)
    def mock_update_cache(*args):
        print('called update_cache with args', args)
    monkeypatch.setattr(readlog, 'update_cache', mock_update_cache)
    testlogroot = tmp_path / 'test_readlog'
    testlogroot.mkdir()
    monkeypatch.setattr(readlog, 'LOGROOT', str(testlogroot))

    # test: read access log
    (testlogroot / 'logfile').write_text('logline_1\nlogline_2\n')
    readlog.rereadlog('logfile', '5', 'A', 'timestr')
    assert capsys.readouterr().out == ("called read_and_set_parms with args ('logfile', '5', 'A',"
                                       " 'timestr')\n"
                                       "called update_cache with args ('timestr', ['logline_1\\n',"
                                       " 'logline_2\\n'])\n")
    # test: read error log from backup
    (testlogroot / 'errorlogfile').touch()
    (testlogroot / 'errorlogfile.1').write_text('logline_1\nlogline_2\n')
    readlog.rereadlog('errorlogfile', '5', 'A', 'timestr')
    assert capsys.readouterr().out == ("called read_and_set_parms with args ('errorlogfile', '5', 'A',"
                                       " 'timestr')\n"
                                       "called check_for_python_tracebacks with arg `['logline_1\\n',"
                                       " 'logline_2\\n']`\n"
                                       "called update_cache with args ('timestr', ['logline_1\\n',"
                                       " 'logline_2\\n'])\n")
    # test: read access log gives no data, no backup log
    (testlogroot / 'logfile').write_text('')
    readlog.rereadlog('logfile', '5', 'A', 'timestr')
    assert capsys.readouterr().out == ("called read_and_set_parms with args ('logfile', '5', 'A',"
                                       " 'timestr')\n"
                                       "called update_cache with args ('timestr', [])\n")


def test_read_and_set_parms(monkeypatch, capsys):
    def mock_execute_raises(*args):
        raise readlog.sqlite3.OperationalError
    def mock_execute(self, *args):
        nonlocal counter
        print(*args)
        counter += 1
        if counter == 1:
            return [['logfile', 11, 'asc']]
    def mock_connect(*args):
        print(f"connecting to database identified by '{args[0]}'")
        return MockConnection(*args)
    def mock_init(*args):
        print('called init_db')
    counter = 0
    monkeypatch.setattr(MockCursor, 'execute', mock_execute_raises)
    monkeypatch.setattr(readlog, 'connect_db', mock_connect)
    monkeypatch.setattr(readlog.sqlite3, 'Connection', MockConnection)
    monkeypatch.setattr(readlog, 'init_db', mock_init)
    readlog.read_and_set_parms('logfile', '10', 'A', 'timestr')
    assert capsys.readouterr().out == ("connecting to database identified by 'timestr'\n"
                                       'called init_db\n'
                                       'executing close\n')
    counter = 0
    monkeypatch.setattr(MockCursor, 'execute', mock_execute)
    monkeypatch.setattr(readlog, 'connect_db', mock_connect)
    monkeypatch.setattr(readlog.sqlite3, 'Connection', MockConnection)
    readlog.read_and_set_parms('logfile', '10', 'A', 'timestr')
    assert capsys.readouterr().out == ("connecting to database identified by 'timestr'\n"
                                       'SELECT logfile, entries, ordering FROM parms where id == 1\n'
                                       'executing close\n'
                                       "connecting to database identified by 'timestr'\n"
                                       "UPDATE parms SET logfile = ?, entries = ? , ordering = ?"
                                       " WHERE id == 1 ('logfile', '10', 'A')\n"
                                       'executing commit\n'
                                       'executing close\n')


def test_check_for_python_tracebacks(monkeypatch, capsys):
    def mock_startswith_date(line):
        return line.startswith('l')
    monkeypatch.setattr(readlog, 'startswith_date', mock_startswith_date)
    assert readlog.check_for_python_tracebacks(
            ['logline1\n', '  logline2\n', '  logline3\n', 'logline4\n', 'logline5\n']) == [
                    'logline1\n', '  logline2\n  logline3\n', 'logline4\n', 'logline5\n']
    assert readlog.check_for_python_tracebacks(
            ['logline1\n', 'logline2\n', 'logline3\n', '  logline4\n', '  logline5\n']) == [
                    'logline1\n', 'logline2\n', 'logline3\n', '  logline4\n  logline5\n']


def test_update_cache(monkeypatch, capsys):
    def mock_execute(self, *args):
        nonlocal counter
        print(*args)
        counter += 1
        if counter == 1:
            return [['asc']]
        elif counter == 6:
            return [[2]]
    def mock_execute_diff(self, *args):
        nonlocal counter
        print(*args)
        counter += 1
        if counter == 1:
            return [['desc']]
        elif counter == 6:
            return [[3]]
    def mock_connect(*args):
        print(f"connecting to database identified by '{args[0]}'")
        return MockConnection(*args)
    def mock_init(*args):
        print('called init_db')
    counter = 0
    monkeypatch.setattr(MockCursor, 'execute', mock_execute)
    monkeypatch.setattr(readlog, 'connect_db', mock_connect)
    monkeypatch.setattr(readlog.sqlite3, 'Connection', MockConnection)
    monkeypatch.setattr(readlog, 'init_db', mock_init)
    readlog.update_cache('timestr', ['logline1', 'logline2'])
    assert capsys.readouterr().out == ("connecting to database identified by 'timestr'\n"
                                       'SELECT ordering FROM parms where id == 1\n'
                                       'DROP TABLE IF EXISTS log;\n'
                                       'CREATE TABLE log (id INTEGER PRIMARY KEY, line varchar(1000)'
                                       ' NOT NULL);\n'
                                       'executing commit\n'
                                       "INSERT INTO log VALUES (?, ?) (1, 'logline1')\n"
                                       "INSERT INTO log VALUES (?, ?) (2, 'logline2')\n"
                                       'executing commit\n'
                                       'SELECT COUNT(*) FROM log;\n'
                                       'UPDATE parms SET total = ? WHERE id == 1 (2,)\n'
                                       'executing commit\n'
                                       'executing close\n')
    # test op exception vanwege verschil tussen aantal regels gelezen en aantal regels dat in de
    # database gezet wordt (kan in de werkelijke situatie niet)
    counter = 0
    monkeypatch.setattr(MockCursor, 'execute', mock_execute_diff)
    monkeypatch.setattr(readlog, 'connect_db', mock_connect)
    monkeypatch.setattr(readlog.sqlite3, 'Connection', MockConnection)
    monkeypatch.setattr(readlog, 'init_db', mock_init)
    with pytest.raises(ValueError):
        readlog.update_cache('timestr', ['logline1', 'logline2'])
    assert capsys.readouterr().out == ("connecting to database identified by 'timestr'\n"
                                       'SELECT ordering FROM parms where id == 1\n'
                                       'DROP TABLE IF EXISTS log;\n'
                                       'CREATE TABLE log (id INTEGER PRIMARY KEY, line varchar(1000)'
                                       ' NOT NULL);\n'
                                       'executing commit\n'
                                       "INSERT INTO log VALUES (?, ?) (1, 'logline2')\n"
                                       "INSERT INTO log VALUES (?, ?) (2, 'logline1')\n"
                                       'executing commit\n'
                                       'SELECT COUNT(*) FROM log;\n'
                                       'executing close\n')


def test_get_data(monkeypatch, capsys):
    def mock_execute_raises(*args):
        raise readlog.sqlite3.OperationalError
    def mock_execute(self, *args):
        nonlocal counter
        print(*args)
        counter += 1
        if counter == 1:
            return [['logfile', 10, 1, 100, 'asc', '']]
        elif counter == 3:
            return ['logline_1', 'logline_2']
    def mock_execute_next(self, *args):
        nonlocal counter
        print(*args)
        counter += 1
        if counter == 1:
            return [['logfile', 10, 1, 10, 'asc', '']]
        elif counter == 3:
            return ['logline_1', 'logline_2']
    def mock_execute_prev(self, *args):
        nonlocal counter
        print(*args)
        counter += 1
        if counter == 1:
            return [['logfile', 10, 11, 100, 'asc', '']]
        elif counter == 3:
            return ['logline_1', 'logline_2']
    def mock_execute_errorlog(self, *args):
        nonlocal counter
        print(*args)
        counter += 1
        if counter == 1:
            return [['error_logfile', 10, 1, 100, 'asc', '']]
        elif counter == 3:
            return ['logline_1', 'logline_2']
    def mock_execute_errorlog_91(self, *args):
        nonlocal counter
        print(*args)
        counter += 1
        if counter == 1:
            return [['error_logfile', 10, 1, 91, 'asc', '']]
        elif counter == 3:
            return ['logline_1', 'logline_2']
    def mock_connect(*args):
        print(f"connecting to database identified by '{args[0]}'")
        return MockConnection(*args)
    def mock_init(*args):
        print('called init_db')
    def mock_showerror(*args):
        print('reading error log line')
    def mock_showaccess(*args):
        print('reading access log line')
    monkeypatch.setattr(readlog, 'listlogs', lambda: ['log1', 'log2'])
    initial_outdict = {'loglist': ['log1', 'log2'],
               'logfile': '',
               'order': '',
               'errorlog': False,
               'numentries': ('5', '10', '15', '20', '25', '30'),
               'entries': '',
               'mld': '',
               'logdata': [],
               'timestr': 'timestr'}
    monkeypatch.setattr(MockCursor, 'execute', mock_execute_raises)
    monkeypatch.setattr(readlog, 'connect_db', mock_connect)
    monkeypatch.setattr(readlog.sqlite3, 'Connection', MockConnection)
    monkeypatch.setattr(readlog, 'init_db', mock_init)
    expected_outdict = {x: y for x, y in initial_outdict.items()}
    expected_outdict.update(mld='No data available, try refreshing the display')
    actual_outdict = readlog.get_data('timestr')
    assert actual_outdict == expected_outdict
    assert capsys.readouterr().out == ("connecting to database identified by 'timestr'\n"
                                       'called init_db\nexecuting close\n')
    counter = 0
    monkeypatch.setattr(MockCursor, 'execute', mock_execute)
    monkeypatch.setattr(readlog, 'connect_db', mock_connect)
    monkeypatch.setattr(readlog.sqlite3, 'Connection', MockConnection)
    monkeypatch.setattr(readlog, 'showaccess', mock_showaccess)
    monkeypatch.setattr(readlog, 'showerror', mock_showerror)
    expected_outdict = {x: y for x, y in initial_outdict.items()}
    expected_outdict.update(entries='10',
                       logdata=[None, None] + 8 * [{'client': '', 'data': '', 'date': ''}],
                       logfile = 'logfile', loglist = ['log1', 'log2'], order='asc',
                       numentries=('5', '10', '15', '20', '25', '30'))
    actual_outdict = readlog.get_data('timestr')
    assert actual_outdict == expected_outdict
    assert capsys.readouterr().out == ("connecting to database identified by 'timestr'\n"
                                       'SELECT logfile, entries, current, total, ordering,'
                                       ' mld FROM parms where id == 1\n'
                                       'UPDATE parms SET current = ? WHERE id == 1 (1,)\n'
                                       'executing commit\n'
                                       'SELECT line FROM log WHERE id BETWEEN ? and ? (1, 10)\n'
                                       'reading access log line\n'
                                       'reading access log line\n'
                                       'executing close\n')
    counter = 0
    monkeypatch.setattr(MockCursor, 'execute', mock_execute)
    monkeypatch.setattr(readlog, 'connect_db', mock_connect)
    monkeypatch.setattr(readlog.sqlite3, 'Connection', MockConnection)
    expected_outdict = {x: y for x, y in initial_outdict.items()}
    expected_outdict.update(entries='10',
                       logdata=[None, None] + 8 * [{'client': '', 'data': '', 'date': ''}],
                       logfile = 'logfile', loglist = ['log1', 'log2'], order='asc',
                       numentries=('5', '10', '15', '20', '25', '30'))
    actual_outdict = readlog.get_data('timestr', position='next')
    assert actual_outdict == expected_outdict
    assert capsys.readouterr().out == ("connecting to database identified by 'timestr'\n"
                                       'SELECT logfile, entries, current, total, ordering,'
                                       ' mld FROM parms where id == 1\n'
                                       'UPDATE parms SET current = ? WHERE id == 1 (11,)\n'
                                       'executing commit\n'
                                       'SELECT line FROM log WHERE id BETWEEN ? and ? (11, 20)\n'
                                       'reading access log line\n'
                                       'reading access log line\n'
                                       'executing close\n')
    counter = 0
    monkeypatch.setattr(MockCursor, 'execute', mock_execute_next)
    monkeypatch.setattr(readlog, 'connect_db', mock_connect)
    monkeypatch.setattr(readlog.sqlite3, 'Connection', MockConnection)
    expected_outdict = {x: y for x, y in initial_outdict.items()}
    expected_outdict.update(entries='10',  mld='Geen volgende pagina',
                       logdata=[None, None] + 8 * [{'client': '', 'data': '', 'date': ''}],
                       logfile = 'logfile', loglist = ['log1', 'log2'], order='asc',
                       numentries=('5', '10', '15', '20', '25', '30'))
    actual_outdict = readlog.get_data('timestr', position='next')
    assert actual_outdict == expected_outdict
    assert capsys.readouterr().out == ("connecting to database identified by 'timestr'\n"
                                       'SELECT logfile, entries, current, total, ordering,'
                                       ' mld FROM parms where id == 1\n'
                                       'UPDATE parms SET current = ? WHERE id == 1 (1,)\n'
                                       'executing commit\n'
                                       'SELECT line FROM log WHERE id BETWEEN ? and ? (1, 10)\n'
                                       'reading access log line\n'
                                       'reading access log line\n'
                                       'executing close\n')
    counter = 0
    monkeypatch.setattr(MockCursor, 'execute', mock_execute_prev)
    monkeypatch.setattr(readlog, 'connect_db', mock_connect)
    monkeypatch.setattr(readlog.sqlite3, 'Connection', MockConnection)
    expected_outdict = {x: y for x, y in initial_outdict.items()}
    expected_outdict.update(entries='10',
                       logdata=[None, None] + 8 * [{'client': '', 'data': '', 'date': ''}],
                       logfile = 'logfile', loglist = ['log1', 'log2'], order='asc',
                       numentries=('5', '10', '15', '20', '25', '30'))
    actual_outdict = readlog.get_data('timestr', position='prev')
    assert actual_outdict == expected_outdict
    assert capsys.readouterr().out == ("connecting to database identified by 'timestr'\n"
                                       'SELECT logfile, entries, current, total, ordering,'
                                       ' mld FROM parms where id == 1\n'
                                       'UPDATE parms SET current = ? WHERE id == 1 (1,)\n'
                                       'executing commit\n'
                                       'SELECT line FROM log WHERE id BETWEEN ? and ? (1, 10)\n'
                                       'reading access log line\n'
                                       'reading access log line\n'
                                       'executing close\n')
    counter = 0
    monkeypatch.setattr(MockCursor, 'execute', mock_execute)
    monkeypatch.setattr(readlog, 'connect_db', mock_connect)
    monkeypatch.setattr(readlog.sqlite3, 'Connection', MockConnection)
    expected_outdict = {x: y for x, y in initial_outdict.items()}
    expected_outdict.update(entries='10', mld='Geen vorige pagina',
                       logdata=[None, None] + 8 * [{'client': '', 'data': '', 'date': ''}],
                       logfile = 'logfile', loglist = ['log1', 'log2'], order='asc',
                       numentries=('5', '10', '15', '20', '25', '30'))
    actual_outdict = readlog.get_data('timestr', position='prev')
    assert actual_outdict == expected_outdict
    assert capsys.readouterr().out == ("connecting to database identified by 'timestr'\n"
                                       'SELECT logfile, entries, current, total, ordering,'
                                       ' mld FROM parms where id == 1\n'
                                       'UPDATE parms SET current = ? WHERE id == 1 (1,)\n'
                                       'executing commit\n'
                                       'SELECT line FROM log WHERE id BETWEEN ? and ? (1, 10)\n'
                                       'reading access log line\n'
                                       'reading access log line\n'
                                       'executing close\n')
    counter = 0
    monkeypatch.setattr(MockCursor, 'execute', mock_execute_errorlog)
    monkeypatch.setattr(readlog, 'connect_db', mock_connect)
    monkeypatch.setattr(readlog.sqlite3, 'Connection', MockConnection)
    expected_outdict = {x: y for x, y in initial_outdict.items()}
    expected_outdict.update(entries='10', errorlog=True,
                       logdata=[None, None] + 8 * [{'client': '', 'data': '', 'date': ''}],
                       logfile = 'error_logfile', loglist = ['log1', 'log2'], order='asc',
                       numentries=('5', '10', '15', '20', '25', '30'))
    actual_outdict = readlog.get_data('timestr', position='last')
    assert actual_outdict == expected_outdict
    assert capsys.readouterr().out == ("connecting to database identified by 'timestr'\n"
                                       'SELECT logfile, entries, current, total, ordering,'
                                       ' mld FROM parms where id == 1\n'
                                       'UPDATE parms SET current = ? WHERE id == 1 (91,)\n'
                                       'executing commit\n'
                                       'SELECT line FROM log WHERE id BETWEEN ? and ? (91, 100)\n'
                                       'reading error log line\n'
                                       'reading error log line\n'
                                       'executing close\n')
    counter = 0
    monkeypatch.setattr(MockCursor, 'execute', mock_execute_errorlog_91)
    monkeypatch.setattr(readlog, 'connect_db', mock_connect)
    monkeypatch.setattr(readlog.sqlite3, 'Connection', MockConnection)
    expected_outdict = {x: y for x, y in initial_outdict.items()}
    expected_outdict.update(entries='10', errorlog=True,
                       logdata=[None, None] + 8 * [{'client': '', 'data': '', 'date': ''}],
                       logfile = 'error_logfile', loglist = ['log1', 'log2'], order='asc',
                       numentries=('5', '10', '15', '20', '25', '30'))
    actual_outdict = readlog.get_data('timestr', position='last')
    assert actual_outdict == expected_outdict
    assert capsys.readouterr().out == ("connecting to database identified by 'timestr'\n"
                                       'SELECT logfile, entries, current, total, ordering,'
                                       ' mld FROM parms where id == 1\n'
                                       'UPDATE parms SET current = ? WHERE id == 1 (91,)\n'
                                       'executing commit\n'
                                       'SELECT line FROM log WHERE id BETWEEN ? and ? (91, 100)\n'
                                       'reading error log line\n'
                                       'reading error log line\n'
                                       'executing close\n')


def test_showerror(monkeypatch, capsys):
    assert readlog.showerror('x') == {'client': '', 'date': '', 'data': 'x'}
    assert readlog.showerror('x[otice]y') == {'client': '', 'date': '', 'data': 'x[otice]y'}
    assert readlog.showerror('x[notice]y') == {'client': '', 'date': 'x', 'data': '[notice]y'}
    assert readlog.showerror('x[error]y') == {'client': '', 'date': 'x', 'data': '[error]y'}
    assert readlog.showerror('x[crit]y') == {'client': '', 'date': 'x', 'data': '[crit]y'}
    assert readlog.showerror('[x] y') == {'client': '', 'date': 'x', 'data': 'y'}
    assert readlog.showerror('[x] y, client z') == {'client': 'client z', 'date': 'x', 'data': 'y'}
    assert readlog.showerror('[x] y, z [client qr] [client q] s') == {'client': 'client: qr',
                                                                      'date': 'x', 'data': 'y, z s'}
    assert readlog.showerror('[x] y, z [client qr] [client v] s') == {'client': 'client: qr / v',
                                                                      'date': 'x', 'data': 'y, z s'}
    assert readlog.showerror('[x] y, z [client qr] s') == {'client': 'client: qr', 'date': 'x',
                                                           'data': 'y, z s'}


def test_showaccess(monkeypatch, capsys):
    assert readlog.showaccess('x') == {'client': 'x', 'date': '', 'data': ''}
    assert readlog.showaccess('x -y') == {'client': 'x', 'date': '', 'data': ''}
    assert readlog.showaccess('x - [y') == {'client': 'x', 'date': 'y', 'data': ''}
    assert readlog.showaccess('x - [y] "z') == {'client': 'x', 'date': 'y', 'data': ''}
    with pytest.raises(ValueError):
        readlog.showaccess('x - [y] "z" ')
    assert readlog.showaccess('x - [y] "z" 1') == {'client': 'x', 'date': 'y',
                                                   'data': '1 unknown status: z'}
    monkeypatch.setattr(readlog, 'responses', {1: 'status'})
    assert readlog.showaccess('x - [y] "z" 1') == {'client': 'x', 'date': 'y', 'data': '1 status: z'}
    assert readlog.showaccess('x - [y] "z" 1 q') == {'client': 'x', 'date': 'y', 'data': '1 status: z'}
