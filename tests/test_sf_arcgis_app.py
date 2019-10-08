# pylint: disable=redefined-outer-name
"""Tests for examples/app_sf_arcgis.py"""
import json
import pytest
import jsend
from falcon import testing
import examples.app_sf_arcgis

@pytest.fixture()
def client():
    """ client fixture """
    return testing.TestClient(examples.app_sf_arcgis.run())

def test_get_fields_by_address_example(client):
    """Test get_fields_by_address_example"""
    address = '1650 mission street'

    response = client.simulate_get(
        '/page/get_fields_by_address_example',
        params={'address':address, 'returnGeometry':True})
    assert response.status_code == 200

    content = json.loads(response.content)

    assert jsend.is_success(content)
    assert len(content['data']['parcels']) == 1
    assert content['data']['parcels'][0]['attributes']['blklot'] == '3512008'
    assert content['data']['parcels'][0]['attributes']['block_num'] == '3512'
    assert content['data']['parcels'][0]['attributes']['lot_num'] == '008'
    assert content['data']['parcels'][0]['attributes']['ADDRESS'] == '1650 MISSION ST'
    assert isinstance(content['data']['parcels'][0]['geometry']['rings'], list)

def test_get_fields_by_address_no_result_example(client):
    """Test get_fields_by_address with base address suggestion"""
    address = '1650 mission street #100'

    response = client.simulate_get(
        '/page/get_fields_by_address_example',
        params={'address':address, 'returnGeometry':False})
    assert response.status_code == 200

    content = json.loads(response.content)

    assert jsend.is_success(content)
    assert len(content['data']['parcels']) == 0

def test_get_fields_by_address_suggestion_base_example(client):
    """Test get_fields_by_address with base address suggestion"""
    address = '1650 mission street #100'

    response = client.simulate_get(
        '/page/get_fields_by_address_example',
        params={'address':address, 'returnGeometry':False, 'returnSuggestions':True})
    assert response.status_code == 200

    content = json.loads(response.content)

    assert jsend.is_success(content)
    assert len(content['data']['parcels']) == 1
    assert content['data']['parcels'][0]['attributes']['blklot'] == '3512008'
    assert content['data']['parcels'][0]['attributes']['block_num'] == '3512'
    assert content['data']['parcels'][0]['attributes']['lot_num'] == '008'
    assert content['data']['parcels'][0]['attributes']['ADDRESS'] == '1650 MISSION ST'
    assert 'geometry' not in content['data']['parcels'][0]

def test_get_fields_by_address_suggestion_multi_example(client):
    """Test get_fields_by_address with multiple suggestions"""
    address = '1651 mission street suite 1000'

    response = client.simulate_get(
        '/page/get_fields_by_address_example',
        params={'address':address, 'returnGeometry':False, 'returnSuggestions':True})
    assert response.status_code == 200

    content = json.loads(response.content)

    assert jsend.is_success(content)
    assert len(content['data']['parcels']) > 1
    for parcel in content['data']['parcels']:
        assert parcel['attributes']['blklot']
        assert parcel['attributes']['ADDRESS']
    assert 'geometry' not in content['data']['parcels'][0]
