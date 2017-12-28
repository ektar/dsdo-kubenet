from ...lib import log_conf
from ...lib import kube_common
from ...lib import arguments
from ...lib import cluster_conf

import argparse
import base64
from jinja2 import Template
import json
from kubernetes import client, config
import kubernetes.client.rest as kube_rest
import logging
import pathlib as pl
import yaml
from pprint import pprint

from ipdb import set_trace


log_name = "dsdo.launch_ldap"


def load_certs(le_prefix, domains):
    certs = {}
    for prefix, domain in domains.items():
        base_path = pl.Path(le_prefix+'config').joinpath('live').joinpath(domain)
        with base_path.joinpath('privkey.pem').open('rb') as f:
            private_key = f.read()
        with base_path.joinpath('cert.pem').open('rb') as f:
            cert = f.read()

        private_key_b64 = base64.b64encode(private_key)
        cert_b64 = base64.b64encode(cert)
        certs[prefix] = {
            'key': private_key_b64.decode('utf-8'),
            'crt': cert_b64.decode('utf-8')
        }
    return certs


def launch_ldap(create_resources=True, config=None):
    log = logging.getLogger(log_name)
    
    manifest_dir = pl.Path(__file__).parent.parent.parent.\
      joinpath('manifests').joinpath('ldap')

    le_prefix = config['general']['lets_encrypt_prefix']
    domain_name = config['general']['domain']
    cluster_name = config['kops']['cluster_name']

    domains = {
        'ldap': 'ldap.internal.{}.{}'.format(
            cluster_name, domain_name),
        'ldap-ui': 'ldap-ui.internal.{}.{}'.format(
            cluster_name, domain_name),
        }

    certs = load_certs(le_prefix, domains)

    resources = [
        'ldap-namespace',
        'ldap-secrets',
        'ldap-volumes',
        # 'ldap-deployment',
        # 'ldap-service',
        # 'ldap-ui-deployment',
        # 'ldap-ui-service',
        # 'ldap-ui-ingress'
    ]
    
    if not create_resources:
        resources = resources[::-1]
    
    for resource_name in resources:
        with manifest_dir.joinpath("{}.yaml".format(resource_name)).open() as f:
            t = Template(f.read())
            filled_t = t.render(
                certs=certs)
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
    log.info("Launch ldap")

    parser = arguments.DSDOParser()
    parser.add_argument("-u", "--user", help="User info")
    args = parser.parse_args()

    config_file = cluster_conf.load_config(args.config_file)

    config.load_kube_config()
    
    create_resources = not args.delete
    launch_ldap(create_resources=create_resources, config=config_file)
    
    return 0


if __name__ == "__main__":
    main()