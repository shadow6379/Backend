#!/bin/bash
set -e

echo "Starting server side"

docker build -t web_server .
docker run -d --restart=always \
--name web_server \
-p 8000:8000 \
web_server

cd reverse_proxy

docker build --no-cache -t reverse_proxy .
docker run -d --restart=always \
--name reverse_proxy \
--link web_server:web_server \
-p 80:80 \
-e NGINX_HOST=0.0.0.0 \
-e NGINX_PROXY=http://0.0.0.0:8000 \
reverse_proxy

echo "Started"
