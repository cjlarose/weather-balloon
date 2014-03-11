import logging
import sys
import os
from time import localtime, strftime

from sqlalchemy import engine_from_config
from pyramid.paster import get_appsettings, setup_logging

from weatherballoon.models import DBStdSession as DBSession
from weatherballoon.models import Cloud, Instance
from weatherballoon.cloud import EucaCloud, AWSCloud, OpenStackCloud, OpenStackRtwoCloud
from weatherballoon.cloud_secrets import PROVIDERS
from weatherballoon.deploy import enqueue_deploy_instance
from weatherballoon.monitor import set_hosts
from weatherballoon.sync import CloudSyncManager

logger = logging.getLogger(__name__)

def get_monitored_vms():
    return DBSession.query(Instance)\
        .filter(Instance.end_date == None)

def notify_monitor(instances):
    """
    Update monitor to set the current list of instances. Monitor 
    will then add/remove hosts as it sees fit
    """ 
    payload = [{
        'client_name': instance.client_name,
        'address': instance.address
    } for instance in instances]
    set_hosts(payload)

def update_clouds(settings):
    logger.debug( "Start time: " + strftime("%c", localtime()))

    cloud_connections = [
        (EucaCloud(**PROVIDERS['euca']), 'Eucalyptus'), 
        (OpenStackCloud(**PROVIDERS['openstack']), 'OpenStack'),
        #(AWSCloudCloud(**PROVIDERS['aws']), 'AWS'),
        (OpenStackRtwoCloud(**PROVIDERS['havanastack']), 'HavanaStack'),
    ]
    clouds = [
        (connection, DBSession.query(Cloud).filter(Cloud.name == name).one()) 
        for (connection, name) in cloud_connections
    ]
    for (cloud, cloud_model) in clouds:
        logger.debug("Checking cloud %s" % cloud_model.name)

        manager = CloudSyncManager(cloud, cloud_model, DBSession)
        to_deploy = manager.synchronize()
        for instance in to_deploy:
            enqueue_deploy_instance.delay(instance, settings)

    hosts = get_monitored_vms()
    notify_monitor(hosts)

    logger.debug( "End time: " + strftime("%c", localtime()))
    
    logger.debug("\n\n" + "=" * 80 + "\n\n")

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)

def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    update_clouds(settings)
