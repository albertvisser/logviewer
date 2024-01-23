"""unittests for ./viewlogs_cherry.py
"""
import viewlogs_cherry as viewlogs

class MockTemplate:
    """stub for template loader
    """
    # @staticmethod
    def render(**kwargs):
        """stub
        """
        return f'call render with kwargs {kwargs}'


def mock_get_data(*args):
    """stub for readlog.get_data
    """
    return {str(x): y for x, y in enumerate(args)}


def test_index(monkeypatch, capsys):
    """unittest for viewlogs_cherry.LogViewer.index
    """
    def mock_init(*args):
        """stub
        """
        print('called init_db with args', args)
    def mock_reread(*args):
        """stub
        """
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


def test_top(monkeypatch):
    """unittest for viewlogs_cherry.LogViewer.top
    """
    monkeypatch.setattr(viewlogs, 'tmpl', MockTemplate)
    monkeypatch.setattr(viewlogs, 'get_data', mock_get_data)
    testobj = viewlogs.Logviewer()
    testobj.timestr = 'hallo'
    assert testobj.top() == "call render with kwargs {'0': 'hallo', '1': 'first'}"


def test_next(monkeypatch):
    """unittest for viewlogs_cherry.LogViewer.next
    """
    monkeypatch.setattr(viewlogs, 'tmpl', MockTemplate)
    monkeypatch.setattr(viewlogs, 'get_data', mock_get_data)
    testobj = viewlogs.Logviewer()
    testobj.timestr = 'hallo'
    assert testobj.next() == "call render with kwargs {'0': 'hallo', '1': 'next'}"


def test_prev(monkeypatch):
    """unittest for viewlogs_cherry.LogViewer.prev
    """
    monkeypatch.setattr(viewlogs, 'tmpl', MockTemplate)
    monkeypatch.setattr(viewlogs, 'get_data', mock_get_data)
    testobj = viewlogs.Logviewer()
    testobj.timestr = 'hallo'
    assert testobj.prev() == "call render with kwargs {'0': 'hallo', '1': 'prev'}"


def test_bottom(monkeypatch):
    """unittest for viewlogs_cherry.LogViewer.bottom
    """
    monkeypatch.setattr(viewlogs, 'tmpl', MockTemplate)
    monkeypatch.setattr(viewlogs, 'get_data', mock_get_data)
    testobj = viewlogs.Logviewer()
    testobj.timestr = 'hallo'
    assert testobj.bottom() == "call render with kwargs {'0': 'hallo', '1': 'last'}"


# module level code testen gaat waarschijnlijk toch op een andere manier - hoeft misschien ook niet?

class MockLogviewer:
    """stubi for viewlogs_cherry.LogViewer
    """
    def __str__(self):
        """stub
        """
        return 'Mock Logviewer'


def _test_main(monkeypatch):
    """unittest for viewlogs_cherry entrypoint
    """
    def mock_start(*args):
        """stub
        """
        print('called quickstart with args', args)
    monkeypatch.setattr(viewlogs, 'Logviewer', MockLogviewer)
    monkeypatch.setattr(viewlogs.cherrypy, 'quickstart', mock_start)
    monkeypatch.setattr(viewlogs, '__name__', '__main__')
