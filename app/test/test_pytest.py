#!/usr/bin/env python3 -u

"""Test all API routes."""
import json
import sys
sys.path.append('../../LED-IOT-api')


"""Load client secrets."""
with open('./client_secrets.json', 'r') as myfile:
    DATA = myfile.read()
DATA = json.loads(DATA)
CLIENT_SECRETS = DATA['web']


def test_authorization(client):
    """Make a test call to /devices/<device> with incorrect authorization headers."""
    response = client.get("/devices/device200",
                          headers={"Authorization": 'Bearer please '})

    assert response.status_code == 403


def test_get_device(client):
    """Make a test call to /devices/<device>."""
    response = client.get("/devices/device200",
                          headers={"Authorization": 'Bearer ' + CLIENT_SECRETS['auth_token']})

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
    """Make a test call to /devices/<device>."""
    response = client.delete("/devices/device200",
                             headers={"Authorization": 'Bearer ' + CLIENT_SECRETS['auth_token']})

    assert response.status_code == 200
    # assert response.json == [
    #     "Device deleted",
    #     200
    # ]


def test_put_device(client):
    """Make a test put request to /devices/<device>."""
    response = client.put("/devices/device50",
                          data=json.dumps({"brightness": "0"}),
                          content_type='application/json',
                          headers={"Authorization": 'Bearer ' + CLIENT_SECRETS['auth_token']})

    assert response.status_code == 201
    assert response.json == [
        "device50",
        {
            "brightness": "0",
            "name": "Default",
            "onState": "true"
        }
    ]


def test_post_devices(client):
    """Make a test post to /devices/."""
    response = client.post("/devices/",
                           data=json.dumps(
                               {"brightness": "100", "name": "New Device", "onState": "False"}),
                           content_type='application/json',
                           headers={"Authorization": 'Bearer ' + CLIENT_SECRETS['auth_token']})

    assert response.status_code == 201
    assert response.json[1] == {
        "brightness": "100",
        "name": "New Device",
        "onState": "False"
    }


def test_check_health(client):
    """Make a test call to /"""
    response = client.get("/health")
    assert response.status_code == 200


def test_get_devicelist(client):
    """Make a test call to /devices/"""
    response = client.get("/devices/",
                          headers={"Authorization": 'Bearer ' + CLIENT_SECRETS['auth_token']})

    assert response.status_code == 200


def test_post_hb(client):
    """Make a test post to set heartbeat."""
    response = client.post("/devices/hb/device100",
                           data=json.dumps(
                               {"heartbeat": "device100"}),
                           content_type='application/json',
                           headers={"Authorization": 'Bearer ' + CLIENT_SECRETS['auth_token']})

    assert response.status_code == 201
    assert response.json == {'message': 'Heartbeat set'}


def test_get_hblist(client):
    """Make a test call to /devices/hb"""
    response = client.get("/devices/hb/",
                          headers={"Authorization": 'Bearer ' + CLIENT_SECRETS['auth_token']})

    assert response.status_code == 200


def test_full_hb(client):
    """Test posting and then getting a device heartbeat."""
    client.post("/devices/hb/device100",
                data=json.dumps(
                    {"heartbeat": "device100"}),
                content_type='application/json',
                headers={"Authorization": 'Bearer ' + CLIENT_SECRETS['auth_token']})

    response2 = client.get("/devices/hb/device100",
                           headers={'Authorization': 'Bearer ' + CLIENT_SECRETS['auth_token']})

    assert response2.status_code == 200
    assert response2.json == ["hb_device100"]
