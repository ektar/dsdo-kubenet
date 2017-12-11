import argparse
import os

class DSDOParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(DSDOParser, self).__init__(*args, **kwargs)

        self.add_argument("-d", "--delete", help="Delete resources", 
            action="store_true")

        self.add_argument("-c", "--config-file", 
            type=str, help="Path to configuration file",
            default=os.environ.get('DSDO_CONFIG_FILE', None))