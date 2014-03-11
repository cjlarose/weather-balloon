from hashlib import sha1
import logging

from rtwo.provider import OSProvider
from rtwo.identity import OSIdentity
from rtwo.driver import OSDriver

from weatherballoon.cloud.cloud import CloudConnection
from weatherballoon.cloud.models import Instance, Image, User, InstanceType
from weatherballoon.cloud.exception import ImageNotFound, InstanceTypeNotFound

logger = logging.getLogger(__name__)

class OpenStackRtwoCloud(CloudConnection):
    def __init__(self, username=None, password=None, tenant_name=None,
        auth_url=None, region_name=None):

        provider = OSProvider()
        OSProvider.set_meta()
        hashed_password = sha1(username).hexdigest()
        identity = OSIdentity(provider, key=username, secret=password,
            user=username, auth_url=auth_url, password=hashed_password,
            region_name=region_name, ex_tenant_name=tenant_name)
        self.driver = OSDriver(provider, identity, ex_force_auth_url=auth_url)

    @staticmethod
    def format_instance(instance):
        return Instance(
            id=instance.id,
            ip_address=instance.ip,
            launch_time=instance.extra['created'],
            state=instance.extra['status'],
            image_id=instance.machine.id,
            user_id=instance.extra['metadata']['creator'],
            instance_type_id=instance.size.id
        )

    def get_running_instances(self):
        instances = self.driver.list_all_instances()
        result = []
        for i in instances:
            if i.extra['status'] == 'active':
                try:
                    instance = OpenStackRtwoCloud.format_instance(i)
                    if instance.ip_address:
                        result.append(instance)
                except KeyError:
                    logger.warn("%s has no creator. Ignoring it" % instance.id)
        return result

    def get_image(self, image_id):
        machine = self.driver.get_machine(image_id)
        if not machine:
            raise ImageNotFound("No image found with id %s" % image_id)
        return Image(
            id=machine.id,
            type='machine',
            name=machine.name
        )

    def get_user(self, user_id):
        return User(name=user_id)

    def get_instance_type(self, type_id):
        size = self.driver.get_size(type_id)
        if not size:
            raise InstanceTypeNotFound()
        return InstanceType(name=size.id)
