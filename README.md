# Backend
backend of "Library Service System for Readers"
### build image
$docker build -t web_sever .
### run django container
#### for DEV
$docker run -e "ENV=DEV" -p 8000:8000 web_server
#### for UNIT
$docker run -e "ENV=UNIT" -p 8000:8000 web_server
#### for PROD
$docker run -p 8000:8000 web_server

