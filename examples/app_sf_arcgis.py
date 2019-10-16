""" sf_arcgis example app """
import os
import json
import falcon
import jsend
from sf_arcgis_sdk.sf_arcgis import SfArcgis

def run():
    """ run function"""
    api = falcon.API()
    api.add_route('/page/{name}', Page())
    return api

class Page():
    """ Page class """
    def __init__(self):
        self.sfarcgis = None

    def on_get(self, _req, _resp, name):
        """ on page GET requests """
        dispatch = None
        if hasattr(self.__class__, name) and callable(getattr(self.__class__, name)):
            dispatch = getattr(self, name)
            self.sfarcgis = SfArcgis()
        dispatch(_req, _resp)

    def get_fields_by_address_example(self, req, resp):
        """ example get_fields_by_address with an address response """

        self.sfarcgis.set_layer('parcel', os.environ.get('PLN_ARCGIS_PARCEL_LAYER_URL'))

        if 'address' in req.params:
            address = req.params['address']
            options = {'returnGeometry':False, 'returnSuggestions':False}
            if 'returnSuggestions' in req.params and req.params['returnSuggestions'] == 'true':
                options['returnSuggestions'] = True
            if 'returnGeometry' in req.params:
                options['returnGeometry'] = req.params['returnGeometry']
            if 'outFields' in req.params:
                options['outFields'] = req.params['outFields']
            self.sfarcgis.set_layer('parcel', os.environ.get('PLN_ARCGIS_PARCEL_LAYER_URL'))
            parcels = self.sfarcgis.get_fields_by_address(address, options)
            response = {'parcels': parcels}
        resp.body = json.dumps(jsend.success(response))
        resp.status = falcon.HTTP_200

    def get_fields_by_parcel_example(self, req, resp):
        """ example get_fields_by_parcel with an parcel number response """

        self.sfarcgis.set_layer('parcel', os.environ.get('PLN_ARCGIS_PARCEL_LAYER_URL'))

        if 'parcel' in req.params:
            parcel = req.params['parcel']
            options = {'returnGeometry':False}
            if 'returnGeometry' in req.params:
                options['returnGeometry'] = req.params['returnGeometry']
            if 'outFields' in req.params:
                options['outFields'] = req.params['outFields']
            self.sfarcgis.set_layer('parcel', os.environ.get('PLN_ARCGIS_PARCEL_LAYER_URL'))
            parcels = self.sfarcgis.get_fields_by_parcel(parcel, options)
            response = {'parcels': parcels}
        resp.body = json.dumps(jsend.success(response))
        resp.status = falcon.HTTP_200
