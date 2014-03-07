#!/bin/bash

if [[ ! -d ${NAGIOS_HOME}/bin ]]; then
        cd /tmp/nagios-4.0.2 && make install && make install-commandmode && make install-webconf
        cd /tmp/nagios-plugins-1.5 && make install
        cd /tmp/nrpe-2.15 && make all && make install-plugin && make install-daemon
        mkdir -p /var/nagios/spool/checkresults && chown -R ${NAGIOS_USER}:${NAGIOS_GROUP} /var/nagios
        mkdir -p /var/nagios/spool/graphios && chown -R ${NAGIOS_USER}:${NAGIOS_GROUP} /var/nagios
        mv /tmp/graphios.py /opt/nagios/bin/graphios.py
        python /opt/nagios/bin/graphios.py &
        ln -s /opt/nagios/bin/nagios /usr/local/bin/nagios
        htpasswd -c -b -s /etc/nagios/htpasswd.users ${NAGIOSADMIN_USER} ${NAGIOSADMIN_PASS}
        env --unset NAGIOSADMIN_PASS
        sed -i 's,/opt/nagios/etc,/etc/nagios,g' /etc/apache2/conf.d/nagios.conf
        if [[ ! -z $NAGIOS_CGI_CONFIG ]]; then
                echo "SetEnv NAGIOS_CGI_CONFIG $NAGIOS_CGI_CONFIG" >> /etc/apache2/conf.d/nagios.conf
        fi
        if [[ ! -f /etc/nagios/nagios.cfg ]]; then
                cd /tmp/nagios-4.0.2 && make install-config
                cp ${NAGIOS_HOME}/etc/* /etc/nagios/
        fi
fi


chown -R ${NAGIOS_USER}.${NAGIOS_GROUP} /var/nagios
chown -R ${NAGIOS_CMDUSER}.${NAGIOS_CMDGROUP} /var/nagios/rw
chown -R ${NAGIOS_USER}.${NAGIOS_GROUP} ${NAGIOS_HOME}
chown -R ${NAGIOS_USER}.${NAGIOS_GROUP} /etc/nagios
/etc/init.d/apache2 start
/opt/nagios/bin/nrpe -c /etc/nagios/nrpe.cfg -d
/usr/local/bin/nagios /etc/nagios/nagios.cfg
