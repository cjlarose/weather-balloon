import os
import logging
import logging.config

import yaml

def setup_logging():
    parent_dir = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(parent_dir, 'logging.yaml')
    with open(path, 'rt') as f:
        config = yaml.load(f.read())
    logging.config.dictConfig(config)
