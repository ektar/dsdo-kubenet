from ...lib import log_conf

import boto3
import json
import logging
import subprocess
import requests

log_name = "dsdo.fetch_instance_info"


def fetch_current_instance_id():
    log = logging.getLogger(log_name)
    aws_url = "http://169.254.169.254/latest/meta-data/instance-id"
    
    response = requests.get(aws_url)
    if response.status_code != 200:
        raise Exception(response)
    instance_id = response.text
    return instance_id


def describe_instance(instance_id=None):
    ec2 = boto3.client('ec2')  
    reservation_dat = ec2.describe_instances(InstanceIds=[instance_id])
    instance_dat = reservation_dat['Reservations'][0]['Instances'][0]
    return instance_dat


def main():
    log = logging.getLogger(log_name)
    
    log.info('Fetching current id')
    instance_id = fetch_current_instance_id()
    log.info("Instance ID = {}".format(instance_id))
    log.info('Fetching instnace data')
    instance_dat = describe_instance(instance_id=instance_id)
    log.info("Instance VPC = {}".format(instance_dat['VpcId']))
    log.info("Instance Subnet = {}".format(instance_dat['SubnetId']))
    return 0
    
if __name__ == "__main__":
    exit(main())