from . import log_conf

import argparse
import logging
import os
import pathlib as pl

log_name = "dsdo.arguments"

class DSDOParser(argparse.ArgumentParser):
    def __init__(self, 
                 require_config=True, 
                 **kwargs):
        super(DSDOParser, self).__init__(**kwargs)

        self._require_config = require_config

        self.add_argument("-d", "--delete", help="Delete resources", 
            action="store_true")

        self.add_argument("-c", "--config-file", 
            type=str, help="Path to configuration file",
            default=os.environ.get('DSDO_CONFIG_FILE', None))
            
    def parse_args(self, **kwargs):
        log = logging.getLogger(log_name)
        log.info('Parsing args')

        args = super(DSDOParser, self).parse_args(**kwargs)
        
        if self._require_config:
            if args.config_file is None:
                raise Exception('config_file is a required parameter')

            config_file = pl.Path(os.getcwd()).joinpath(args.config_file)
            
            if not config_file.is_file():
                raise Exception('File {} does not exist'.format(config_file))

            args.config_file = config_file.as_posix()
    
        return args