import viewlogs_cherry as viewlogs

class MockTemplate:
    # @staticmethod
    def render(**kwargs):
        return f'call render with kwargs {kwargs}'


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
    assert testobj.index('', '1', 'asc', 'timestr') == "call render with kwargs {'0': '11'}"
    assert capsys.readouterr().out == "called init_db with args ('11',)\n"
    testobj = viewlogs.Logviewer()
    testobj.timestr = 'hallo'
    assert testobj.index('logfile', '1', 'asc', 'timestr') == "call render with kwargs {'0': 'hallo'}"
    assert capsys.readouterr().out == "called rereadlog with args ('logfile', '1', 'asc', 'hallo')\n"


def test_top(monkeypatch, capsys):
    monkeypatch.setattr(viewlogs, 'tmpl', MockTemplate)
    monkeypatch.setattr(viewlogs, 'get_data', mock_get_data)
    testobj = viewlogs.Logviewer()
    testobj.timestr = 'hallo'
    assert testobj.top() == "call render with kwargs {'0': 'hallo', '1': 'first'}"


def test_next(monkeypatch, capsys):
    monkeypatch.setattr(viewlogs, 'tmpl', MockTemplate)
    monkeypatch.setattr(viewlogs, 'get_data', mock_get_data)
    testobj = viewlogs.Logviewer()
    testobj.timestr = 'hallo'
    assert testobj.next() == "call render with kwargs {'0': 'hallo', '1': 'next'}"


def test_prev(monkeypatch, capsys):
    monkeypatch.setattr(viewlogs, 'tmpl', MockTemplate)
    monkeypatch.setattr(viewlogs, 'get_data', mock_get_data)
    testobj = viewlogs.Logviewer()
    testobj.timestr = 'hallo'
    assert testobj.prev() == "call render with kwargs {'0': 'hallo', '1': 'prev'}"


def test_bottom(monkeypatch, capsys):
    monkeypatch.setattr(viewlogs, 'tmpl', MockTemplate)
    monkeypatch.setattr(viewlogs, 'get_data', mock_get_data)
    testobj = viewlogs.Logviewer()
    testobj.timestr = 'hallo'
    assert testobj.bottom() == "call render with kwargs {'0': 'hallo', '1': 'last'}"


# module level code testen gaat waarschijnlijk toch op een andere manier - hoeft misschien ook niet?

class MockLogviewer:
    def __str__(self):
        return 'Mock Logviewer'


def _test_main(monkeypatch, capsys):
    def mock_start(*args):
        print('called quickstart with args', args)
    monkeypatch.setattr(viewlogs, 'Logviewer', MockLogviewer)
    monkeypatch.setattr(viewlogs.cherrypy, 'quickstart', mock_start)
    monkeypatch.setattr(viewlogs, '__name__', '__main__')
