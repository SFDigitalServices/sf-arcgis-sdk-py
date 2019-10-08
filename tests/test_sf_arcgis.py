"""Tests for sf_arcgis_sdk package"""
import json
from unittest.mock import patch
from sf_arcgis_sdk.sf_arcgis import SfArcgis

TEST_ARCGIS_LAYER_URL = "https://arcgis/rest/services/Landscape_Trees/FeatureServer/0"

def test_set_layer():
    """ test set_layer method """
    test_layer_name = "test"

    sfarcgis = SfArcgis()
    sfarcgis.set_layer(test_layer_name, TEST_ARCGIS_LAYER_URL)
    assert sfarcgis.gis_layers[test_layer_name] == TEST_ARCGIS_LAYER_URL

def test_get_fields_by_address():
    """ test get_fields_by_address method """
    with open('tests/mocks/parcel_request.json', 'r') as file_obj:
        mock_request = json.load(file_obj)

    with open('tests/mocks/parcel.json', 'r') as file_obj:
        mock_data = json.load(file_obj)

    sfarcgis = SfArcgis()
    sfarcgis.set_layer("parcel", TEST_ARCGIS_LAYER_URL)

    with patch('sf_arcgis_sdk.sf_arcgis.requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_request
        options = {
            'outFields':'blklot,block_num,lot_num,ADDRESS',
            'returnGeometry':'false', 'f':'json'
        }
        parcel = sfarcgis.get_fields_by_address('600 MONTGOMERY ST #100', options)

    with patch('sf_arcgis_sdk.sf_arcgis.requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_request
        options = {
            'outFields':'blklot,block_num,lot_num,ADDRESS',
            'returnGeometry':'false', 'f':'json'
        }
        parcel = sfarcgis.get_fields_by_address('600 MONTGOMERY ST #100', options)
    assert parcel == mock_data

def test_get_fields_by_address_missing_layer():
    """ test get_fields_by_address method
        missing layer state """
    test = SfArcgis()
    parcel = test.get_fields_by_address('600 MONTGOMERY ST #100')
    assert parcel is False

def test_query():
    """ test query method """
    sfarcgis = SfArcgis()
    assert sfarcgis.query("https://jsonplaceholder.typicode.com/posts", {})

def test_query_eror():
    """ test query method
        error state """
    sfarcgis = SfArcgis()
    assert sfarcgis.query("http://test", {}) is None
