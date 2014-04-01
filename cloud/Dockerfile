FROM        ubuntu:12.04

RUN         echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
RUN         apt-get update
RUN         apt-get install -y python python-dev python-pip git libffi-dev libldap2-dev libsasl2-dev libpq-dev

# Supervisor
RUN         apt-get install -y supervisor
ADD         etc/supervisor.conf /etc/supervisor/conf.d/supervisor.conf

RUN         pip install --upgrade pip

ADD         . /data/wb_cloud
RUN         cd /data/wb_cloud && pip install --process-dependency-links -e .
RUN         mkdir -p /var/log/wb_cloud

EXPOSE      8000
CMD         ["/usr/bin/supervisord"]
