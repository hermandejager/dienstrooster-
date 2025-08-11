import importlib

def test_import_app():
    mod = importlib.import_module('app')
    assert hasattr(mod, 'app')
    client = mod.app.test_client()
    resp = client.get('/', follow_redirects=False)
    # Zonder login verwachten we redirect naar /login
    assert resp.status_code in (301,302)
    assert '/login' in resp.headers.get('Location','')
