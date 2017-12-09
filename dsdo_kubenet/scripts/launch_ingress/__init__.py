from ...lib import log_conf
from ...lib import kube_common
from ...lib import arguments

import argparse
import json
from kubernetes import client, config
import kubernetes.client.rest as kube_rest
import logging
import pathlib as pl
import yaml
from pprint import pprint

from ipdb import set_trace


log_name = "dsdo.launch_ingress"


def launch_ingress(create_resources=True):
    log = logging.getLogger(log_name)
    
    manifest_dir = pl.Path(__file__).parent.parent.parent.\
      joinpath('manifests').joinpath('nginx-ingress')

    resources = [
        'namespace',
        'default-backend',
        'configmap',
        'tcp-services-configmap',
        'udp-services-configmap',
        'rbac',
        'with-rbac'
    ]
    
    if not create_resources:
        resources = resources[::-1]
    
    for resource_name in resources:
        with manifest_dir.joinpath("{}.yaml".format(resource_name)).open() as f:
            resources = yaml.load_all(f)
          
            for resource in resources:
                if create_resources:
                    log.info('Creating resource {}'.format(resource['kind']))
    
                    kube_common.create_resource(resource)
                else:
                    log.info('Deleting resource {}'.format(resource['kind']))
    
                    kube_common.delete_resource(resource)


def main():
    log = logging.getLogger(log_name)
    log.info("Launch ingress")

    parser = arguments.DSDOParser()
    # parser.add_argument("-d", "--delete", help="Delete resources", action="store_true")
    args = parser.parse_args()

    config.load_kube_config()
    
    create_resources = not args.delete
    launch_ingress(create_resources=create_resources)


if __name__ == "__main__":
    main()