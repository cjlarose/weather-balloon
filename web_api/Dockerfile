FROM        ubuntu:12.04

RUN         echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
RUN         apt-get update
RUN         apt-get install -y python python-dev python-pip

RUN         pip install --upgrade pip

ADD         . /data/web_api
RUN         cd /data/web_api && pip install -r requirements.txt

EXPOSE      8000
ENV         PYTHONPATH /data/web_api
CMD         ["/usr/bin/python", "/data/web_api/wbapi/__init__.py"]
