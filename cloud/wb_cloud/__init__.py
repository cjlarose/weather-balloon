import logging
import logging.config

import yaml

def setup_logging():
    path = 'logging.yaml'
    with open(path, 'rt') as f:
        config = yaml.load(f.read())
    logging.config.dictConfig(config)
