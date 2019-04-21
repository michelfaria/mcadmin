#!/bin/bash

# Set current working directory to this script's location
cd "${0%/*}"

# Make CSS directory
mkdir ./mcadmin/static/css/

# Run the app
FLASK_APP=mcadmin.main FLASK_ENV=development flask run