FROM        ubuntu:12.04

RUN         apt-get update
RUN         apt-get install -y python python-pip python-dev

ADD         . /data/wb_hosts
RUN         cd /data/wb_hosts && python setup.py develop

WORKDIR     /data/wb_hosts
CMD         python wb_hosts/server.py
EXPOSE      8000
