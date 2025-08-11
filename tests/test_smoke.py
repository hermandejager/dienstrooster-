import importlib

def test_import_app():
    mod = importlib.import_module('app')
    assert hasattr(mod, 'app')
    client = mod.app.test_client()
    resp = client.get('/')
    assert resp.status_code == 200
