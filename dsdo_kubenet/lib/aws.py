from . import log_conf
import boto3

import logging
import requests

log_name = "dsdo.aws"


def fetch_current_instance_id():
    log = logging.getLogger(log_name)
    
    # Note: Fixed iP, per documentation:
    #   http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html
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
    
def describe_vpc(vpc_id=None):
    ec2 = boto3.client('ec2')  
    vpc_dat = ec2.describe_vpcs(VpcIds=[vpc_id])
    return vpc_dat['Vpcs'][0]
