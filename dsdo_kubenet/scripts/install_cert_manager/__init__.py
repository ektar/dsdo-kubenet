from ...lib import log_conf
from ...lib import kube_common
from ...lib import arguments

import argparse
import json
from kubernetes import client, config
import kubernetes.client.rest as kube_rest
import logging
import pathlib as pl
from pprint import pprint
import subprocess as sp
import shlex
import yaml

from ipdb import set_trace


log_name = "dsdo.install_cert_manager"


def install_cm(create_resources=True):
    log = logging.getLogger(log_name)
    
    manifest_dir = pl.Path(__file__).parent.parent.parent.\
      joinpath('manifests').joinpath('cert-manager')

    cmd = 'helm install --name cert-manager --namespace kube-system {}'.format(manifest_dir)
    log.info('Run `{}`'.format(cmd))
    # output = sp.check_output(shlex.split(cmd), 
    #     shell=True,
    #     stderr=sp.STDOUT)
    # print(output.decode('utf-8'))

    # resources = [
    #     # 'ldap-namespace',
    #     # 'ldap-volumes',
    #     # 'ldap-deployment',
    #     # 'ldap-service',
    #     # 'ldap-ui-deployment',
    #     # 'ldap-ui-service',
    #     # 'ldap-ui-ingress'
    # ]
    
    # if not create_resources:
    #     resources = resources[::-1]
    
    # for resource_name in resources:
    #     with manifest_dir.joinpath("{}.yaml".format(resource_name)).open() as f:
    #         resources = yaml.load_all(f)
          
    #         for resource in resources:
    #             if create_resources:
    #                 log.info('Creating resource {}'.format(resource['kind']))
    
    #                 kube_common.create_resource(resource)
    #             else:
    #                 log.info('Deleting resource {}'.format(resource['kind']))
    
    #                 kube_common.delete_resource(resource)


def main():
    log = logging.getLogger(log_name)
    log.info("Installing certificate manager")

    parser = arguments.DSDOParser()
    args = parser.parse_args()

    config.load_kube_config()
    
    create_resources = not args.delete
    install_cm(create_resources=create_resources)
    
    return 0


if __name__ == "__main__":
    main()