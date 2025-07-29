# iterfuncs

A collection of tools of async and sync iteration/caching and some funcitonal stuff

## Installation

`pip install iterfuncs`

## Requirements:

- Python 3.12

## Development

- clone the repo
- create and invoke a venv: `python -m venv .venv` | `. .venv/bin/activate`
- install the requirements: `pip install -r requirements.txt`
- install pre-commit and execute `pre-commit install`

## Deployment

- go to `setup.py` and increase the version
- commit your changes and push them to a new branch

## IMPORTANT

- DON'T DO `pip freeze > requirements.txt` - it can cause issues with the lambdas etc.

  Just add the packages to requirements manually, specifying versions if necessary
