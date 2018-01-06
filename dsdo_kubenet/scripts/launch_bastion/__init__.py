from ...lib import log_conf
from ...lib import kube_common
from ...lib import arguments
from ...lib import cluster_conf

import argparse
from jinja2 import Template
import json
from kubernetes import client, config
import kubernetes.client.rest as kube_rest
import logging
import pathlib as pl
import yaml
from pprint import pprint

from ipdb import set_trace


log_name = "dsdo.launch_bastion"


def load_org_info(config):
    log = logging.getLogger(log_name)

    org_info = {}
    
    org_info['organization'] = config['general']['organization']
    org_info['domain'] = config['general']['domain']
    org_info['admin_email'] = config['general']['admin_email']
    org_info['base_dn'] = config['ldap']['base']
    org_info['cluster_name'] = config['kops']['cluster_name']
    org_info['efs_name'] = config['general']['efs_name']

    return org_info


def launch_bastion(create_resources=True, config=None):
    log = logging.getLogger(log_name)
    
    manifest_dir = pl.Path(__file__).parent.parent.parent.\
      joinpath('manifests').joinpath('bastion')

    org_info = load_org_info(config)

    resources = [
        'deployment',
        'service'
    ]
    
    if not create_resources:
        resources = resources[::-1]
    
    for resource_name in resources:
        with manifest_dir.joinpath("{}.yaml".format(resource_name)).open() as f:
            t = Template(f.read())
            filled_t = t.render(
                org_info=org_info)
            resources = yaml.load_all(filled_t)
          
            for resource in resources:
                if create_resources:
                    log.info('Creating resource {}'.format(resource['kind']))
    
                    kube_common.create_resource(resource)
                else:
                    log.info('Deleting resource {}'.format(resource['kind']))
    
                    kube_common.delete_resource(resource)


def main():
    log = logging.getLogger(log_name)
    log.info("Launch bastion")

    parser = arguments.DSDOParser()
    # parser.add_argument("-d", "--delete", help="Delete resources", action="store_true")
    args = parser.parse_args()

    config_file = cluster_conf.load_config(args.config_file)

    config.load_kube_config()
    
    create_resources = not args.delete
    launch_bastion(create_resources=create_resources, config=config_file)
    
    return 0


if __name__ == "__main__":
    main()