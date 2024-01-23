"""unittests for ./viewlogs_bottle.py
"""
import viewlogs_bottle as viewlogs


class MockRequest(viewlogs.bottle.request):
    """stub for bottle.request
    """

def mock_get_data(*args):
    """stub for readlog.get_data
    """
    return {str(x): y for x, y in enumerate(args)}

def mock_template(*args):
    """stub for bottle.template
    """
    return f'call bottle.template with args {args}'

def test_logviewer(monkeypatch, capsys):
    """unittest for viewlog.bottle.logviewer
    """
    def mock_init(*args):
        """stub
        """
        print('called init_db with args', args)
    def mock_reread(*args):
        """stub
        """
        print('called rereadlog with args', args)
    monkeypatch.setattr(viewlogs, 'get_data', mock_get_data)
    monkeypatch.setattr(viewlogs, 'init_db', mock_init)
    monkeypatch.setattr(viewlogs, 'rereadlog', mock_reread)
    monkeypatch.setattr(viewlogs, 'timestr', 'hallo')
    monkeypatch.setattr(viewlogs, 'request', MockRequest)
    monkeypatch.setattr(viewlogs.request, 'args', {'logfile': 'logfile', 'entries': 1,
                                                   'order': 'asc'})
    monkeypatch.setattr(viewlogs, 'template', mock_template)
    assert viewlogs.logviewer() == "call render for {'0': '11'}"
    assert capsys.readouterr().out == "called init_db with args ('11',)\n"
    assert viewlogs.logviewer('logfile', '1', 'asc', 'timestr') == "call render for {'0': 'hallo'}"
    assert capsys.readouterr().out == "called rereadlog with args ('logfile', '1', 'asc', 'hallo')\n"


def test_first_page(monkeypatch):
    """unittest for viewlog.bottle.first_page
    """
    monkeypatch.setattr(viewlogs, 'get_data', mock_get_data)
    monkeypatch.setattr(viewlogs, 'template', mock_template)
    monkeypatch.setattr(viewlogs, 'timestr', 'hallo')
    assert viewlogs.first_page() == "call render for {'0': 'hallo', '1': 'first'}"


def test_next_page(monkeypatch):
    """unittest for viewlog.bottle.next_page
    """
    monkeypatch.setattr(viewlogs, 'get_data', mock_get_data)
    monkeypatch.setattr(viewlogs, 'template', mock_template)
    monkeypatch.setattr(viewlogs, 'timestr', 'hallo')
    assert viewlogs.next_page() == "call render for {'0': 'hallo', '1': 'next'}"


def test_previous_page(monkeypatch):
    """unittest for viewlog.bottle.previous_page
    """
    monkeypatch.setattr(viewlogs, 'get_data', mock_get_data)
    monkeypatch.setattr(viewlogs, 'template', mock_template)
    monkeypatch.setattr(viewlogs, 'timestr', 'hallo')
    assert viewlogs.previous_page() == "call render for {'0': 'hallo', '1': 'prev'}"


def test_last_page(monkeypatch):
    """unittest for viewlog.bottle.last_page
    """
    monkeypatch.setattr(viewlogs, 'get_data', mock_get_data)
    monkeypatch.setattr(viewlogs, 'template', mock_template)
    monkeypatch.setattr(viewlogs, 'timestr', 'hallo')
    assert viewlogs.last_page() == "call render for {'0': 'hallo', '1': 'last'}"
