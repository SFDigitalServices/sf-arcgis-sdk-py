""" SF ArcGIS SDK module """
import math
import json
import urllib
import requests
import usaddress

class SfArcgis():
    """ SF ArcGIS class """

    def __init__(self):
        self.gis_layers = {}
        self.parcel_param_default = {
            'outFields':'blklot,block_num,lot_num,ADDRESS',
            'returnGeometry':'false', 'f':'json'
        }

    def set_layer(self, name, url):
        """ Sets a GIS layer """
        self.gis_layers[name] = url

    def get_fields_by_address(self, address, options=None):
        """ get fields by address from Planning ArcGIS """
        parcels = {}

        # validate it has proper layer set
        if self.has_missing_layers(['parcel']):
            self.print_error("missing parcel layer")
            return False

        addr = usaddress.tag(address)

        url = urllib.parse.urljoin(self.gis_layers.get('parcel')+'/', 'query')
        params = self.parcel_param_default

        if options:
            if 'outFields' in options:
                params['outFields'] = options['outFields']
            if 'returnGeometry' in options:
                params['returnGeometry'] = options['returnGeometry']

        if 'AddressNumber' in addr[0] and 'StreetName' in addr[0]:
            where = "base_address_num="+ addr[0]['AddressNumber']
            where += " and street_name='"+addr[0]['StreetName'].upper()+"'"
            if 'OccupancyIdentifier' in addr[0]:
                where += " and unit_address='"+addr[0]['OccupancyIdentifier'].upper()+"'"
            params['where'] = where
            response = self.query(url, params)
            if response and 'features' in response and response['features']:
                parcels = response['features']
            elif response is not None and options and options['returnSuggestions']:
                # auto suggestions
                if 'OccupancyIdentifier' in addr[0]:
                    where = "base_address_num="+ addr[0]['AddressNumber']
                    where += " and street_name='"+addr[0]['StreetName'].upper()+"'"
                    params['where'] = where
                    response = self.query(url, params)
                    if response and 'features' in response and response['features']:
                        parcels = response['features']
                if not parcels:
                    base_num = math.floor(int(addr[0]['AddressNumber'])/100)*100
                    where = "base_address_num >=" + str(base_num)
                    where += " and base_address_num <"+str(base_num+100)
                    where += " and street_name='"+addr[0]['StreetName'].upper()+"'"
                    params['where'] = where
                    response = self.query(url, params)
                    if response and 'features' in response and response['features']:
                        parcels = response['features']
        return parcels

    def get_fields_by_parcel(self, blklot, options=None):
        """ get fields by parcel number from Planning ArcGIS """
        parcels = {}

        # validate it has proper layer set
        if self.has_missing_layers(['parcel']):
            self.print_error("missing parcel layer")
            return False

        url = urllib.parse.urljoin(self.gis_layers.get('parcel')+'/', 'query')
        params = self.parcel_param_default
        if options:
            if 'outFields' in options:
                params['outFields'] = options['outFields']
            if 'returnGeometry' in options:
                params['returnGeometry'] = options['returnGeometry']

        where = "blklot='"+blklot+"'"
        params['where'] = where
        response = self.query(url, params)
        if response and 'features' in response and response['features']:
            parcels = response['features']

        return parcels

    def query(self, url, params):
        """ Queries an url """
        response = {}
        headers = {}
        try:
            request = requests.get(url, params=params, headers=headers)
            if request.status_code == 200:
                response = request.json()
            return response
        except requests.exceptions.RequestException as error:
            self.print_error("Request exception")
            self.print_error(error)
            self.print_error("url: " + url)
            self.print_error("params: " + json.dumps(params))
            return None


    def has_missing_layers(self, required_layers):
        """ Check if the required layers are set """
        missing = []
        for lyr in required_layers:
            if not self.gis_layers.get(lyr):
                missing.append(lyr)
        return missing

    def print_error(self, msg):
        """ Prints error message """
        print(type(self).__name__ + ": "+str(msg))
