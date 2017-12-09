from ...lib import log_conf
from ...lib import kube_common

import json
from kubernetes import client, config
import kubernetes.client.rest as kube_rest
import logging
import pathlib as pl
import yaml
from pprint import pprint

from ipdb import set_trace


log_name = "dsdo.launch_ingress"


def launch_ingress():
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
    
    for resource_name in resources:
        log.info("Installing ingress resource {}".format(resource_name))
        
        with manifest_dir.joinpath("{}.yaml".format(resource_name)).open() as f:
            resources = yaml.load_all(f)
          
            for resource in resources:
                log.info('Creating resource {}'.format(resource['kind']))

                kube_common.create_resource(resource)

def main():
    log = logging.getLogger(log_name)
    log.info("Launch ingress")
    config.load_kube_config()
    launch_ingress()

if __name__ == "__main__":
    main()