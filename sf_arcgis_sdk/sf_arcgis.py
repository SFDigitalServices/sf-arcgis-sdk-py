""" SF ArcGIS SDK module """
import math
import re
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

    # pylint: disable=too-many-branches
    def get_fields_by_address(self, address, options=None):
        """ get fields by address from Planning ArcGIS """
        parcels = {}

        # validate it has proper layer set
        if self.has_missing_layers(['parcel']):
            self.print_error("missing parcel layer")
            return False

        # replace number sign with unit so OccupancyIdentifier can be populated
        address = address.upper().replace("#", "UNIT ")

        addr = usaddress.tag(address)

        url = urllib.parse.urljoin(self.gis_layers.get('parcel')+'/', 'query')
        params = self.parcel_param_default

        if options:
            if 'outFields' in options:
                params['outFields'] = options['outFields']
            if 'returnGeometry' in options:
                params['returnGeometry'] = options['returnGeometry']

        if 'AddressNumber' in addr[0] and 'StreetName' in addr[0]:

            street_name = self.get_street_name(addr[0])

            where = "base_address_num="+ addr[0]['AddressNumber']
            where += " and street_name='"+street_name+"'"
            if 'OccupancyIdentifier' in addr[0]:
                where += " and unit_address='"+addr[0]['OccupancyIdentifier'].upper()+"'"
            params['where'] = where
            response = self.query(url, params)
            if response and 'features' in response and response['features']:
                parcels = response['features']
            elif response is not None:
                # auto suggestions
                if options and options['returnSuggestions']:
                # try without OccupancyIdentifier
                    if 'OccupancyIdentifier' in addr[0]:
                        where = "base_address_num="+ addr[0]['AddressNumber']
                        where += " and street_name='"+street_name+"'"
                        params['where'] = where
                        response = self.query(url, params)
                        if response and 'features' in response and response['features']:
                            parcels = response['features']
                    if not parcels:
                        # try look up and down the block
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
        params["where"] = where
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

    @staticmethod
    def get_street_name(addr):
        """ Return street name from address """
        street_name = addr['StreetName']
        street_name = re.sub('[^0-9a-zA-Z ]+', '', street_name)

        # numbered street names
        mapping = [
            ('01ST', ['1ST', 'FIRST']),
            ('02ND', ['2ND', 'SECOND']),
            ('03RD', ['3RD', 'THIRD']),
            ('04TH', ['4TH', 'FOURTH']),
            ('05TH', ['5TH', 'FIFTH']),
            ('06TH', ['6TH', 'SIXTH']),
            ('07TH', ['7TH', 'SEVENTH']),
            ('08TH', ['8TH', 'EIGHTH']),
            ('09TH', ['9TH', 'NINTH']),
            ('10TH', ['TENTH'])
        ]
        for key, vals in mapping:
            for val in vals:
                if street_name == val:
                    street_name = street_name.replace(val, key)

        # special exception for BayShore
        street_name = street_name.replace('BAYSHORE', 'BAY SHORE')

        # concat StreetNamePreType
        if 'StreetNamePreType' in addr:
            street_name = addr['StreetNamePreType'] + " " + street_name

        # directionals
        if 'StreetNamePreDirectional' in addr or 'StreetNamePostDirectional' in addr:
            # concat StreetNamePreDirectional
            if 'StreetNamePreDirectional' in addr:
                street_name = addr['StreetNamePreDirectional'] + " " + street_name

            mapping = [
                ('N', 'NORTH'),
                ('S', 'SOUTH'),
                ('W', 'WEST'),
                ('E', 'EAST')
                ]
            for key, val in mapping:
                street_name = (" "+street_name+" ").replace(" "+key+" ", " "+val+" ")

        street_name = " ".join(street_name.split()).strip()

        return street_name
