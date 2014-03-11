class Instance(object):
    def __init__(self, *args, **kwargs):
        self.id = kwargs['id']
        self.ip_address = kwargs['ip_address']
        self.launch_time = kwargs['launch_time']
        self.state = kwargs['state']
        self.image_id = kwargs['image_id']
        self.user_id = kwargs['user_id']
        self.instance_type_id = kwargs['instance_type_id']

class Image(object):
    def __init__(self, *args, **kwargs):
        self.id = kwargs['id']
        self.type = kwargs['type']
        self.name = kwargs['name'] if 'name' in kwargs else None

class User(object):
    def __init__(self, *args, **kwargs):
        self.name = kwargs['name']

class InstanceType(object):
    def __init__(self, *args, **kwargs):
        self.name = kwargs['name']
