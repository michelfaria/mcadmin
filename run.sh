#!/bin/bash
pipenv shell
FLASK_APP=mcadmin.server FLASK_ENV=development flask run