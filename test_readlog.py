import pytest
import types
import readlog


def test_listlogs(monkeypatch, capsys):
    def mock_stat(self, *args):
        nonlocal counter
        counter += 1
        return types.SimpleNamespace(st_ctime='changetime{}'.format(counter))
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
        print("connecting to database identified by '{}'".format(args[0]))
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

