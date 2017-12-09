import argparse

class DSDOParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(DSDOParser, self).__init__(*args, **kwargs)

        self.add_argument("-d", "--delete", help="Delete resources", action="store_true")