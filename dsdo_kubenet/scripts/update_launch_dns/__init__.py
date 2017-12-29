from ...lib import log_conf
from ...lib import kube_common
from ...lib import arguments
from ...lib import cluster_conf
from ...lib import aws

import boto3
import json
import logging
import os
import pathlib as pl
from pprint import pprint

from ipdb import set_trace

log_name = "dsdo.update_launch_dns"


def update_launch_dns(config):
    log = logging.getLogger(log_name)
    instance_id = aws.fetch_current_instance_id()
    log.info("Instance ID = {}".format(instance_id))
    log.info('Fetching instance data')
    instance_dat = aws.describe_instance(instance_id=instance_id)
    public_ip = instance_dat['PublicIpAddress']
    log.info("Public ip address = {}".format(public_ip))

    client = boto3.client('route53')

    hosted_zone = config['general']['domain']
    launch_fqdn = 'launch.{}'.format(hosted_zone)

    zones = client.list_hosted_zones_by_name(
        DNSName="{0}.".format(hosted_zone),
        MaxItems="1")
    zone = zones['HostedZones'][0]

    zone_id = zone['Id'].replace('/hostedzone/', '')

    response = client.change_resource_record_sets(
  		HostedZoneId=zone_id,
  		ChangeBatch= {
  						'Comment': 'Adding current launcher ip',
  						'Changes': [
  							{
  							 'Action': 'UPSERT',
  							 'ResourceRecordSet': {
  								 'Name': launch_fqdn,
  								 'Type': 'A',
  								 'TTL': 60,
                  'ResourceRecords': [{
                      'Value': '{0}'.format(public_ip)
                    }]  								 
  							}
  						}]
  		})


def main():
    log = logging.getLogger(log_name)

    log.info('Update launch dns')

    parser = arguments.DSDOParser()
    args = parser.parse_args()
    
    config = cluster_conf.load_config(args.config_file)
    
    update_launch_dns(config)
    
    return 0
    
if __name__ == "__main__":
    exit(main())