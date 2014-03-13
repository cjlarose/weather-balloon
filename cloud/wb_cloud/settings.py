import os
config = {}

# Database configuration. Uses SQlAlchemy's engine URL syntax. 
# http://docs.sqlalchemy.org/en/rel_0_9/core/engines.html#database-urls

config['db_url'] = "postgresql://%s:%s@%s:%s/%s" % (
    "username",
    "passowrd",
    os.environ['DB_PORT_5432_TCP_ADDR'],
    os.environ['DB_PORT_5432_TCP_PORT'],
    "database",
)

# Cloud provider configuration
# Each dictionary key of config['providers'] should be unique and never change 
# Each value is a tuple of the form (a, b) where a is the full qualified name
# of subclass of wb_cloud.cloud.cloud.CloudConnection, and b are the kwargs
# passed to the subclass to instantiate it.

config['providers'] = {
    'openstack_havana': (
        "wb_cloud.cloud.OpenStackRtwoCloud",
        {
            'username': 'username',
            'password': 'super_secret_password',
            'tenant_name': 'tenant_name',
            'auth_url': 'auth_url',
            'region_name': 'region_name',
        }
    ),
}
