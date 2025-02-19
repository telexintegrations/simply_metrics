''' Testing the functionality of the app'''

import pytest
from app import app, send_notification


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome to simply_metric home page!" in response.data

def test_metrics(client):
    response = client.get('/metric')
    assert response.status_code == 200
    assert b'cpu_usage_percent' in response.data

def test_notify(client, monkeypatch):
    def mock_send_notification():
        return {"status": "success"}
    monkeypatch.setattr("app.send_notification", mock_send_notification)
    
    response = client.get('/tick')
    assert response.status_code == 202
    assert b'{"result":{"status":"success"}}' in response.data
