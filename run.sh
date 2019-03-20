#!/bin/bash
pipenv shell
FLASK_APP=mcadmin.main FLASK_ENV=development flask run