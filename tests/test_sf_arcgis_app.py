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

def get_parcels_by_address_response(client, address, opts=None):
    """ get address parcel data """

    if (opts and 'returnGeometry' in opts):
        return_geometry = opts['returnGeometry']
    else:
        return_geometry = False

    if (opts and 'returnSuggestions' in opts):
        return_suggestions = opts['returnSuggestions']
    else:
        return_suggestions = False

    response = client.simulate_get(
        '/page/get_fields_by_address_example',
        params={'address':address,
                'returnGeometry':return_geometry,
                'returnSuggestions':return_suggestions})
    return response

def test_get_fields_by_address_example(client):
    """Test get_fields_by_address_example"""
    address = '1650 mission street'

    response = get_parcels_by_address_response(client, address, {'returnGeometry': True})
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

    response = get_parcels_by_address_response(client, address)
    assert response.status_code == 200

    content = json.loads(response.content)

    assert jsend.is_success(content)
    assert len(content['data']['parcels']) == 0

def test_get_fields_by_address_suggestion_base_example(client):
    """Test get_fields_by_address with base address suggestion"""
    address = '1650 mission street #100'

    response = get_parcels_by_address_response(client, address, {'returnSuggestions':True})
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

    response = get_parcels_by_address_response(client, address, {'returnSuggestions':True})
    assert response.status_code == 200

    content = json.loads(response.content)

    assert jsend.is_success(content)
    assert len(content['data']['parcels']) > 1
    for parcel in content['data']['parcels']:
        assert parcel['attributes']['blklot']
        assert parcel['attributes']['ADDRESS']
    assert 'geometry' not in content['data']['parcels'][0]

def test_get_fields_by_parcel_example(client):
    """Test test_get_fields_by_parcel_example"""
    parcel = '3512008'

    response = client.simulate_get(
        '/page/get_fields_by_parcel_example',
        params={'parcel':parcel, 'returnGeometry':True, 'outFields':'block_num,lot_num,ADDRESS'})
    assert response.status_code == 200

    content = json.loads(response.content)

    assert jsend.is_success(content)
    assert len(content['data']['parcels']) > 0
    assert 'blklot' not in content['data']['parcels'][0]['attributes']
    assert content['data']['parcels'][0]['attributes']['block_num'] == '3512'
    assert content['data']['parcels'][0]['attributes']['lot_num'] == '008'
    assert isinstance(content['data']['parcels'][0]['geometry']['rings'], list)

def test_get_fields_by_parcel_no_result_example(client):
    """Test get_fields_by_parcel no results"""
    parcel = 'ABCDEFG'

    response = client.simulate_get(
        '/page/get_fields_by_parcel_example',
        params={'parcel':parcel, 'returnGeometry':False})
    assert response.status_code == 200

    content = json.loads(response.content)

    assert jsend.is_success(content)
    assert len(content['data']['parcels']) == 0

def test_get_fields_by_address_numbered_streets(client):
    """
        Test get_fields_by_address with
        * The potential for leading zeros in the numbered streets and avenues
            e.g. 01st St versus 1st St e.g. 101 1st
        * Numbered streets being spelled out – First St, etc.
    """
    address = '101 01st'

    response = get_parcels_by_address_response(client, address)
    assert response.status_code == 200

    content = json.loads(response.content)

    assert jsend.is_success(content)
    assert len(content['data']['parcels']) > 0

    # The potential for leading zeros in the numbered streets and avenues
    # e.g. 01st St versus 1st St e.g. 101 1st
    address = '101 1st'

    response = get_parcels_by_address_response(client, address)
    assert response.status_code == 200

    content_nonzero = json.loads(response.content)

    assert content_nonzero == content

    # Numbered streets being spelled out – First St, etc.
    address = '101 First'

    response = get_parcels_by_address_response(client, address)
    assert response.status_code == 200

    content_spelled = json.loads(response.content)

    assert content_spelled == content

    address = '111 Tenth'

    response = get_parcels_by_address_response(client, address)
    assert response.status_code == 200

    content = json.loads(response.content)

    assert jsend.is_success(content)
    assert len(content['data']['parcels']) > 0


def test_get_fields_by_address_suffix(client):
    """
        Test get_fields_by_address with directional street suffixes
        e.g. Buena Vista Ave West, Burnett Ave North, Willard Street North
    """
    address = '783 Buena Vista Ave West'

    response = get_parcels_by_address_response(client, address)
    assert response.status_code == 200

    content = json.loads(response.content)

    assert jsend.is_success(content)
    assert len(content['data']['parcels']) > 0
    assert content['data']['parcels'][0]['attributes']['ADDRESS'] == address.upper()

def test_get_fields_by_address_prefix(client):
    """
        Test get_fields_by_address
        * Directional prefixes
            e.g. South Hill Blvd, West Point Rd, West Clay St and South Van Ness Ave
        * Shorthand directional prefix or suffix
    """
    address = '505 South Van Ness Ave'

    response = get_parcels_by_address_response(client, address)
    assert response.status_code == 200

    content_suffix = json.loads(response.content)

    assert jsend.is_success(content_suffix)
    assert len(content_suffix['data']['parcels']) > 0
    assert content_suffix['data']['parcels'][0]['attributes']['ADDRESS'] == address.upper()

    address = '505 Van Ness Ave'

    response = get_parcels_by_address_response(client, address)
    assert response.status_code == 200

    content = json.loads(response.content)

    assert jsend.is_success(content)
    assert len(content['data']['parcels']) > 0
    assert content['data']['parcels'][0]['attributes']['ADDRESS'] == address.upper()

    # Shorthand directional prefix or suffix
    address = '505 S Van Ness Ave'

    response = get_parcels_by_address_response(client, address)
    assert response.status_code == 200

    content_suffix_short = json.loads(response.content)

    assert content_suffix_short == content_suffix

def test_get_fields_by_address_special_character(client):
    """
        Test get_fields_by_address
        with The apostrophe in O'Farrell St can cause issues, and it gets dropped in EAS
    """
    address = "859 O'Farrell St"

    response = get_parcels_by_address_response(client, address)
    assert response.status_code == 200

    content = json.loads(response.content)

    assert jsend.is_success(content)
    assert len(content['data']['parcels']) > 0

def test_get_fields_by_address_unit_number(client):
    """
        Test get_fields_by_address with number sign(#) as unit type
    """
    address = '77 van ness ave #100'

    response = get_parcels_by_address_response(client, address)
    assert response.status_code == 200

    content = json.loads(response.content)

    assert jsend.is_success(content)
    assert len(content['data']['parcels']) == 1

def test_get_fields_by_address_name_spellings(client):
    """
        Test get_fields_by_address
        with Streets with contentious spellings
        e.g. Bay Shore Blvd or Bayshore Blvd
        EAS says Bay Shore, the street signs say Bayshore and people use both.
    """
    address = "99 bay shore blvd"

    response = get_parcels_by_address_response(client, address)
    assert response.status_code == 200

    content = json.loads(response.content)

    assert jsend.is_success(content)
    assert len(content['data']['parcels']) > 0

    address = "99 bayshore blvd"

    response = get_parcels_by_address_response(client, address)
    assert response.status_code == 200

    content_oneword = json.loads(response.content)

    assert content_oneword == content

def test_get_fields_by_address_pretype(client):
    """
        Test get_fields_by_address
        with Streets with pre type
        e.g. Avenue of the Palms versus Avenue of the Palms Ave
    """
    address = "1 Avenue of the Palms"

    response = get_parcels_by_address_response(client, address)
    assert response.status_code == 200

    content = json.loads(response.content)

    assert jsend.is_success(content)
    assert len(content['data']['parcels']) > 0
