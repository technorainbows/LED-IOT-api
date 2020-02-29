#!/usr/bin/env python3 -u

"""Test all API routes."""
import json
import sys
# from app.main import *
sys.path.append('../../LED-IOT-api')
# from ../app.main import server


# @pytest.fixture
# def app():
#     """Create a fixture whose name is "app" and returns our flask server instance."""
#     app = server.app
#     return app

"""Load client secrets."""
with open('./client_secrets.json', 'r') as myfile:
    data=myfile.read()
data = json.loads(data)
# print(data)
client_secrets = data['web']


def test_get_device(client):
    """Make a test call to /Devices/<device>."""
    response = client.get("/Devices/device200")

    assert response.status_code == 200
    assert response.json == [
        "device200",
        {
            "brightness": "255",
            "name": "Default",
            "onState": "true"
        }
    ]


def test_delete_device(client):
    """Make a test call to /Devices/<device>."""
    response = client.delete("/Devices/device200")

    assert response.status_code == 200
    assert response.json == [
        "Device deleted",
        200
    ]


def test_put_device(client):
    """Make a test put request to /Devices/<device>."""
    response = client.put("/Devices/device50",
                          data=json.dumps({"brightness": "0"}),
                          content_type='application/json')

    assert response.status_code == 200
    assert response.json == [
        "device50",
        {
            "brightness": "0",
            "name": "Default",
            "onState": "true"
        },
        200
    ]


def test_post_devices(client):
    """Make a test post to /Devices/."""
    response = client.post("/Devices/",
                           data=json.dumps(
                               {"brightness": "100", "name": "New Device", "onState": "False"}),
                           content_type='application/json')

    assert response.status_code == 200
    assert response.json[1] == {
        "brightness": "100",
        "name": "New Device",
        "onState": "False"
    }


def test_get_devicelist(client):
    """Make a test call to /Devices/"""
    response = client.get("/Devices/")

    assert response.status_code == 200


def test_post_hb(client):
    """Make a test post to set heartbeat."""
    response = client.post("/Devices/HB/device100",
                           data=json.dumps(
                               {"heartbeat": "device100"}),
                           content_type='application/json')

    assert response.status_code == 200
    assert response.json is True


def test_get_hblist(client):
    """Make a test call to /Devices/HB"""
    response = client.get("/Devices/HB/")

    assert response.status_code == 200


def test_full_hb(client):
    """Test posting and then getting a device heartbeat."""
    client.post("/Devices/HB/device100",
                data=json.dumps(
                    {"heartbeat": "device100"}),
                content_type='application/json')

    response2 = client.get("/Devices/HB/device100")

    assert response2.status_code == 200
    assert response2.json == ["hb_device100"]
