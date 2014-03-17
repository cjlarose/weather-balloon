from boto import connect_ec2 
from boto.ec2.regioninfo import RegionInfo
from boto.ec2.connection import EC2Connection
from boto.exception import EC2ResponseError

from cloud import CloudConnection
from models import User, Image, Instance, InstanceType
from exception import ImageNotFound

class EC2Cloud(CloudConnection):
    def __init__(self):
        self.conn = self.get_connection()
        super(EC2Cloud, self).__init__()

    def get_connection(self):
        raise NotImplementedError()

    def get_running_instances(self):
        reservations = self.conn.get_all_instances()
        instance_tuples = reduce(list.__add__, map(EC2Cloud.extract_instances, reservations), [])
        instances = map(EC2Cloud.convert_instance, instance_tuples)
        return [i for i in instances if i.state == 'running']

    @staticmethod
    def convert_instance(instance_tuple):
        reservation, instance = instance_tuple
        # instance.ip_address yields the correct IP for AWS and OpenStack, but not
        # Euca.  Euca needs instance.public_dns_name
        address = instance.ip_address if instance.ip_address is not None\
            else instance.public_dns_name
        info = {
            'id': instance.id,
            'ip_address': address,
            'instance_type_id': instance.instance_type,
            'launch_time': instance.launch_time,
            'image_id': instance.image_id,
            'user_id': reservation.owner_id,
            'state': instance.state
        }
        return Instance(**info)

    # given a boto.ec2.instance.reservation, return a list of tuples of the form 
    # (boto.ec2.instance.reservation, boto.ec2.instance)
    @staticmethod
    def extract_instances(res):
        return map((lambda i: (res, i)), res.instances)

    def get_image(self, image_id):
        # this returns garbage sometimes. Don't trust it
        ec2image = self.conn.get_image(image_id)
        if ec2image.id != image_id:
            raise ImageNotFound()
        return Image(id=ec2image.id, type=ec2image.type)

    def get_user(self, user_id):
        return User(name=user_id)

    def get_instance_type(self, type_id):
        return InstanceType(name=type_id)

class EucaCloud(EC2Cloud):
    def __init__(self, access_key=None, secret_key=None, port=None, path=None, 
        region={}):
        self.secrets = {
            'access_key': access_key,
            'secret_key': secret_key,
            'port': port,
            'path': path,
            'region': region
        }
        super(EucaCloud, self).__init__()

    def get_connection(self):
        region = RegionInfo(**self.secrets['region'])
        c = connect_ec2(
            aws_access_key_id=self.secrets['access_key'], 
            aws_secret_access_key=self.secrets['secret_key'], 
            is_secure=False, 
            port=self.secrets['port'], 
            path=self.secrets['path'], 
            region=region
        )
        return c
        

class AWSCloud(EC2Cloud):
    def __init__(self, access_key=None, secret_key=None):
        self.secrets = {
            'access_key': access_key,
            'secret_key': secret_key
        }
        super(AWSCloud, self).__init__(conn)

    def get_connection(self):
        c = EC2Connection(self.secrets['access_key'], self.secrets['secret_key'])
