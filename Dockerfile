FROM python:3.6

RUN pip install django==2.0.3 uwsgi==2.0.17 pillow itsdangerous django-cors-headers python-memcached
RUN groupadd -r uwsgi && useradd -r -g uwsgi uwsgi
WORKDIR /web_server
COPY web_server /web_server
COPY cmd.sh /

# USER uwsgi

CMD ["/cmd.sh"]
