# Python SDK for SF ArcGIS [![CircleCI](https://badgen.net/circleci/github/SFDigitalServices/sf-arcgis-sdk-py/master)](https://circleci.com/gh/SFDigitalServices/sf-arcgis-sdk-py) [![Coverage Status](https://coveralls.io/repos/github/SFDigitalServices/sf-arcgis-sdk-py/badge.svg?branch=master)](https://coveralls.io/github/SFDigitalServices/sf-arcgis-sdk-py?branch=master)

Python SDK for SF ArcGIS

## Install
> $ pipenv install "git+https://github.com/SFDigitalServices/sf-arcgis-sdk-py.git@master#egg=sf-arcgis-sdk"

## Example usage
> from sf_arcgis_sdk.sf_arcgis import SfArcgis

> sfarcgis = SfArcgis()

> sfarcgis.set_layer('parcel', <PLN_ARCGIS_PARCEL_LAYER_URL>)

> parcels = sfarcgis.get_fields_by_address(address, options)

## Tests
> pipenv run python -m pytest tests/ --cov=sf_arcgis_sdk --cov-report term-missing





