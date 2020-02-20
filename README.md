# Boilerplate SDK in Python [![CircleCI](https://badgen.net/circleci/github/SFDigitalServices/boilerplate-sdk-py/master)](https://circleci.com/gh/SFDigitalServices/boilerplate-sdk-py) [![Coverage Status](https://coveralls.io/repos/github/SFDigitalServices/boilerplate-sdk-py/badge.svg?branch=master)](https://coveralls.io/github/SFDigitalServices/boilerplate-sdk-py?branch=master)

Boilerplate for making your own SDK in Python

## Install
> $ pipenv install "git+https://github.com/hshaosf/boilerplate-sdk-py.git@master#egg=boilerplate-sdk"

## Example usage
> from boilerplate_sdk.example import Example

> example = Example()

> posts = example.get_posts({'userId':'1'})

## Tests
> pipenv run python -m pytest tests/ --cov=boilerplate_sdk --cov-report term-missing
  
## Example app
Start up example app
> pipenv run gunicorn --reload 'examples.app:run()'

## Run test for example app
> pipenv run python -m pytest examples/ --cov=examples/ --cov-report term-missing





