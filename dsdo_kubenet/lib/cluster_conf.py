from . import log_conf

import logging
import yaml

log_name = "dsdo.cluster_conf"

def load_config(config_file):
    log = logging.getLogger(log_name)

    log.info('Loading config file')
    
    with open(config_file) as f:
        config = yaml.load(f)
    
    return config