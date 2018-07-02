#!/bin/bash
set -e

echo "Starting server side"

cd cache_server

docker build --no-cache -t cache_middleware .
docker run -d --restart=always \
--name cache_middleware \
-p 11211:11211 \
cache_middleware

cd ..

docker build -t web_server .
docker run -d --restart=always \
--name web_server \
--link cache_middleware:cache_middleware \
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
