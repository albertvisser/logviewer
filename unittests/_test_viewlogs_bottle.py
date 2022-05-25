import pytest

import viewlogs_cherry as viewlogs

class MockTemplate:
    # @staticmethod
    def render(**kwargs):
        return 'call render for {}'.format(kwargs)


def mock_get_data(*args):
    return {str(x): y for x, y in enumerate(args)}


def test_index(monkeypatch, capsys):
    def mock_init(*args):
        print('called init_db with args', args)
    def mock_reread(*args):
        print('called rereadlog with args', args)
    monkeypatch.setattr(viewlogs.time, 'time', lambda: 1.1)
    monkeypatch.setattr(viewlogs, 'tmpl', MockTemplate)
    monkeypatch.setattr(viewlogs, 'get_data', mock_get_data)
    monkeypatch.setattr(viewlogs, 'init_db', mock_init)
    monkeypatch.setattr(viewlogs, 'rereadlog', mock_reread)
    testobj = viewlogs.Logviewer()
    assert testobj.index('', '1', 'asc', 'timestr') == "call render for {'0': '11'}"
    assert capsys.readouterr().out == "called init_db with args ('11',)\n"
    testobj = viewlogs.Logviewer()
    testobj.timestr = 'hallo'
    assert testobj.index('logfile', '1', 'asc', 'timestr') == "call render for {'0': 'hallo'}"
    assert capsys.readouterr().out == "called rereadlog with args ('logfile', '1', 'asc', 'hallo')\n"
