from ...lib import log_conf
from ...lib import kube_common
from ...lib import arguments
from ...lib import cluster_conf
from ...lib import aws

import boto3
from jinja2 import Template
import json
import logging
import pathlib as pl
from pprint import pprint
import subprocess
import requests

# from ipdb import set_trace

log_name = "dsdo.create_kops_config"


def main():
    log = logging.getLogger(log_name)

    log.info('Create kops config')

    parser = arguments.DSDOParser()
    args = parser.parse_args()
    
    config = cluster_conf.load_config(args.config_file)
    
    kops_template = pl.Path(__file__).parent.parent.parent.\
      joinpath('templates/kops/config.yaml')

    with kops_template.open() as f:
        template_dat = f.read()
        t = Template(template_dat)
    
    domain_name = config['general']['domain']
    cluster_name = config['kops']['cluster_name']
    kops_fqn = "{}.{}".format(cluster_name, domain_name)
    
    instance_id = aws.fetch_current_instance_id()
    instance_dat = aws.describe_instance(instance_id=instance_id)
    vpc_id = instance_dat['VpcId']
    subnet_id = instance_dat['SubnetId']
    region = instance_dat['Placement']['AvailabilityZone']
    vpc_dat = aws.describe_vpc(vpc_id)
    
    kops_file = t.render(
        kops_fqn=kops_fqn,
        kops_state_store=config['kops']['state_store_name'],
        vpc_id=vpc_id,
        region=region,
        vpc_cidr=vpc_dat['CidrBlock'],
        subnet_id=subnet_id
        )
    
    print(kops_file)
    
    return 0
    
if __name__ == "__main__":
    exit(main())