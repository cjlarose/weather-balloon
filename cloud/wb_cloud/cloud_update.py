import logging
import sys
import os
import importlib
from time import localtime, strftime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from wb_cloud.models import Cloud, Instance
from wb_cloud.settings import config
from wb_cloud.hosts_service import HostsService
from wb_cloud.sync import CloudSyncManager
from wb_cloud.sync.ldap_client import LDAPClient

logger = logging.getLogger(__name__)

class CloudUpdate(object):

    def __init__(self, db_session, hosts_service, providers, ldap_client):
        self.db = db_session
        self.hosts_service = hosts_service
        self.providers = providers
        self.ldap_client = ldap_client

    def get_providers(self):
        """
        Returns a list of tuples (a, b) such that a is an instance of
        wb_cloud.cloud.cloud.CloudConnection and b is an instance of
        wb_cloud.models.Cloud.
        """
        for cloud_name, (cls, args) in self.providers.iteritems():
            module_name, class_name = cls.rsplit('.', 1)
            cloud_module = importlib.import_module(module_name)
            cloud_connection_cls = getattr(cloud_module, class_name)
            cloud_connection = cloud_connection_cls(**args)

            cloud_model = self.db.query(Cloud).filter(Cloud.name == cloud_name).one()

            yield cloud_connection, cloud_model

    def get_monitored_vms(self):
        return self.db.query(Instance).filter(Instance.end_date == None)

    def notify_monitor(self, instances):
        """
        Update monitor to set the current list of instances. Monitor
        will then add/remove hosts as it sees fit.
        """
        payload = [{
            'id': instance.client_name,
            'display_name': instance.client_name,
            'address': instance.address
        } for instance in instances]
        self.hosts_service.set_hosts(payload)

    def run(self):
        logger.debug( "Start time: " + strftime("%c", localtime()))

        clouds = self.get_providers()
        for (cloud, cloud_model) in clouds:
            logger.debug("Checking cloud %s" % cloud_model.name)

            manager = CloudSyncManager(cloud, cloud_model, self.db, self.ldap_client)
            to_deploy = manager.synchronize()
            for instance in to_deploy:
                print instance

        hosts = self.get_monitored_vms()
        self.notify_monitor(hosts)

        logger.debug( "End time: " + strftime("%c", localtime()))

        logger.debug("\n\n" + "=" * 80 + "\n\n")

def main():
    providers = config['providers']

    engine = create_engine(config['db_url'])
    Session = sessionmaker(bind=engine)

    hosts_service = HostsService(*config['host_service'])
    ldap_client = LDAPClient(config['ldap_server'])
    cloud_update = CloudUpdate(Session(), hosts_service, providers, ldap_client)
    cloud_update.run()

if __name__ == "__main__":
    main()
