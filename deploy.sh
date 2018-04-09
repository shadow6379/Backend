#!/bin/bash
set -e

echo "Starting server side"

docker run -d --restart=always \
--name web_server \
-p 8000:8000 \
web_server

docker run -d --restart=always \
--name proxy \
--link web_server:web_server \
-p 80:80 \
-e NGINX_HOST=localhost \
-e NGINX_PROXY=http://localhost:8000 \
proxy

echo "Started"

