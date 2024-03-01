# -*- coding: utf-8 -*-

from main import app
from fastapi.testclient import TestClient

client = TestClient(app)




def test_add ():
    resp = client.put('/mul?x=10&y=5')
    assert resp.status_code == 200
    assert resp.json()=={"result": 50}
    resp = client.put('/mul?x=10&y=X')
    assert resp.status_code == 422

def test_msg ():
    resp = client.get('/msg/Me')
    assert resp.status_code == 200
    assert resp.json()=={"msg": "Hello, Me !"}
    resp = client.get('/msg/You')
    assert resp.status_code == 200
    assert resp.json()=={"msg": "Hello, You !"}

def test_div ():
    resp = client.put('/div?x=10&y=5')
    assert resp.status_code == 200
    assert resp.json()=={"result": 2}
    resp = client.put('/div?x=10&y=0')
    assert resp.status_code == 200
