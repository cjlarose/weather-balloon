class CloudException(Exception):
    pass

class ImageNotFound(CloudException):
    pass

class InstanceTypeNotFound(CloudException):
    pass
