from novaclient.v1_1 import client as nova_client
from novaclient.exceptions import NotFound
from quantumclient.v2_0 import client as quantum_client
from keystoneclient.v2_0 import client as keystone_client

from weatherballoon.cloud.cloud import CloudConnection
from weatherballoon.cloud.models import Instance, User, Image, InstanceType
from weatherballoon.cloud.exception import ImageNotFound, InstanceTypeNotFound

class OpenStackCloud(CloudConnection):
    def __init__(self, username=None, password=None, tenant_name=None, 
        auth_url=None, region_name=None):
        self.settings = {
            'username': username,
            'password': password,
            'tenant_name': tenant_name,
            'auth_url': auth_url,
            'region_name': region_name
        }

        self.nova = nova_client.Client( self.settings['username'], 
            self.settings['password'], 
            self.settings['tenant_name'], 
            self.settings['auth_url'], 
            service_type='compute'
        )
        self.nova.client.region_name = self.settings['region_name']

        self.quantum = quantum_client.Client(**self.settings)
        self.keystone = keystone_client.Client(
            username=self.settings['username'],
            password=self.settings['password'],
            tenant_name=self.settings['tenant_name'],
            auth_url=self.settings['auth_url']
        )

        super(OpenStackCloud, self).__init__()

    def get_all_instances(self):
        servers = self.nova.servers.list(True, {'all_tenants': '1'}) 
        floating_ips = self.quantum.list_floatingips()['floatingips']
        ports = self.quantum.list_ports()['ports']
        port_dict = dict([(port['id'], port) for port in ports])
        instance_to_fip = {}
        for fip in floating_ips:
            if fip['port_id'] in port_dict:
                port = port_dict[fip['port_id']]
                if port['device_id'] not in instance_to_fip:
                    instance_to_fip[port['device_id']] = []
                instance_to_fip[port['device_id']].append(fip)

        instances = []
        for server in servers:
            if server.id in instance_to_fip:
                instance_attrs = {
                    'id': server.id,
                    'ip_address': instance_to_fip[server.id][0]['floating_ip_address'],
                    'instance_type_id': server.flavor['id'],
                    'launch_time': server.created,
                    'image_id': server.image['id'],
                    'user_id': server.user_id,
                    'state': server.status
                }
                instances.append(Instance(**instance_attrs))

        #return (servers, floating_ips, ports, port_dict, instance_to_fip, instances)
        #return (servers, instances)
        return instances

    def get_running_instances(self):
        instances = self.get_all_instances()
        return [i for i in instances if i.state == 'ACTIVE']

    def get_image(self, image_id):
        try:
            nova_image = self.nova.images.get(image_id)
        except NotFound:
            raise ImageNotFound()
        image_attrs = {
            'id': nova_image.id,
            'name': nova_image.name,
            'type': 'machine'
        }
        return Image(**image_attrs)

    def get_user(self, user_id):
        keystone_user = self.keystone.users.get(user_id)
        return User(name=keystone_user.name)

    def get_instance_type(self, type_id):
        try:
            nova_flavor = self.nova.flavors.get(type_id)
        except NotFound:
            raise InstanceTypeNotFound()
        return InstanceType(name=nova_flavor.name)
