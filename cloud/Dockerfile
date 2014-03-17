FROM        ubuntu:12.04

RUN         echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
RUN         apt-get update
RUN         apt-get install -y python python-dev python-pip git libffi-dev libldap2-dev libsasl2-dev libpq-dev

ADD         . /data/wb_cloud
RUN         cd /data/wb_cloud && pip install -e .

WORKDIR     /data/wb_cloud
CMD         python wb_cloud/server.py
EXPOSE      8000
