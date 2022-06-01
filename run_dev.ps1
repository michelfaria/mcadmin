# Make CSS directory
New-Item -ItemType Directory -Force -Path ".\mcadmin\static\css\" | Out-Null

# Run the app
$env:FLASK_APP = "mcadmin.main"
$env:FLASK_ENV = "development"

py -3.7 -m pipenv run flask run
