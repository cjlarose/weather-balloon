FROM ubuntu:12.04

ENV NAGIOS_HOME /opt/nagios
ENV NAGIOS_USER nagios
ENV NAGIOS_GROUP nagios
ENV NAGIOS_CMDUSER nagios
ENV NAGIOS_CMDGROUP nagios
ENV NAGIOS_CGI_CONFIG /etc/nagios/cgi.cfg
ENV NAGIOSADMIN_USER nagiosadmin
ENV NAGIOSADMIN_PASS nagios

RUN echo "deb http://security.ubuntu.com/ubuntu precise main universe" >> /etc/apt/sources.list
RUN apt-get update && apt-get install -y inetutils-ping build-essential snmp snmpd wget php5-cli apache2 libapache2-mod-php5
RUN ( egrep -i  "^${NAGIOS_GROUP}" /etc/group || groupadd $NAGIOS_GROUP ) && ( egrep -i "^${NAGIOS_CMDGROUP}" /etc/group || groupadd $NAGIOS_CMDGROUP )
RUN ( id -u $NAGIOS_USER || useradd $NAGIOS_USER -g $NAGIOS_GROUP -d $NAGIOS_HOME ) && ( id -u $NAGIOS_CMDUSER || useradd -d $NAGIOS_HOME -g $NAGIOS_CMDGROUP $NAGIOS_CMDUSER )
RUN cd /tmp && wget http://prdownloads.sourceforge.net/sourceforge/nagios/nagios-4.0.2.tar.gz
RUN cd /tmp && tar -zxvf nagios-4.0.2.tar.gz && cd nagios-4.0.2  && ./configure --prefix=${NAGIOS_HOME} --exec-prefix=/opt/nagios --disable-statusmap --disable-statuswrl --enable-event-broker --with-nagios-command-user=${NAGIOS_CMDUSER} --with-command-group=${NAGIOS_CMDGROUP} --with-nagios-user=${NAGIOS_USER} --with-nagios-group=${NAGIOS_GROUP} && make all
RUN cd /tmp && wget --no-check-certificate http://www.nagios-plugins.org/download/nagios-plugins-1.5.tar.gz
RUN cd /tmp && tar -zxvf nagios-plugins-1.5.tar.gz && cd nagios-plugins-1.5 && ./configure --prefix=/opt/nagios && make
RUN sed -i.bak 's/.*\=www\-data//g' /etc/apache2/envvars
RUN echo "export APACHE_RUN_USER=$(echo $NAGIOS_CMDUSER)" >> /etc/apache2/envvars
RUN echo "export APACHE_RUN_GROUP=$(echo $NAGIOS_CMDGROUP)" >> /etc/apache2/envvars
RUN export DOC_ROOT="DocumentRoot $(echo $NAGIOS_HOME/share)"; sed -i "s,DocumentRoot.*,$DOC_ROOT," /etc/apache2/sites-enabled/000-default

ADD start.sh /usr/local/bin/start_nagios
RUN chmod +x /usr/local/bin/start_nagios

# NRPE Installation
RUN apt-get install -y libssl-dev
RUN cd /tmp && wget http://prdownloads.sourceforge.net/sourceforge/nagios/nrpe-2.x/nrpe-2.15/nrpe-2.15.tar.gz
RUN cd /tmp && tar -zxvf nrpe-2.15.tar.gz && cd nrpe-2.15 && ./configure --with-ssl=/usr/bin/openssl --with-ssl-lib=/usr/lib/x86_64-linux-gnu --prefix=${NAGIOS_HOME} --exec-prefix=/opt/nagios --with-nagios-user=${NAGIOS_USER} --with-nagios-group=${NAGIOS_GROUP}

# Configuration
RUN cd /tmp/nagios-4.0.2 && make install-config
ADD ./nagios-conf /etc/nagios
RUN chown -R ${NAGIOS_USER}.${NAGIOS_GROUP} /etc/nagios

CMD ["/usr/local/bin/start_nagios"]
EXPOSE 80
VOLUME /var/nagios/rw
VOLUME /etc/nagios
VOLUME /opt/nagios
