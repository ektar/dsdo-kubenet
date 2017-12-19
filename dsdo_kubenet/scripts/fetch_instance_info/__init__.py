from ...lib import log_conf
from ...lib import aws

import json
import logging
from pprint import pprint

from ipdb import set_trace

log_name = "dsdo.fetch_instance_info"

def main():
    log = logging.getLogger(log_name)
    
    log.info('Fetching current id')
    instance_id = aws.fetch_current_instance_id()
    log.info("Instance ID = {}".format(instance_id))
    log.info('Fetching instnace data')
    instance_dat = aws.describe_instance(instance_id=instance_id)
    log.info("Instance VPC = {}".format(instance_dat['VpcId']))
    log.info("Instance Subnet = {}".format(instance_dat['SubnetId']))
    region = instance_dat['Placement']['AvailabilityZone']
    log.info("Instance Region = {}".format(region))
    public_ip = instance_dat['PublicIpAddress']
    log.info("Public ip address = {}".format(public_ip))
    
    # set_trace()
    
    # pprint(instance_dat)
    return 0
    
if __name__ == "__main__":
    exit(main())