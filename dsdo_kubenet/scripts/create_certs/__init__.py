from ...lib import log_conf
from ...lib import kube_common
from ...lib import arguments
from ...lib import cluster_conf

import argparse
import json
from kubernetes import client, config
import kubernetes.client.rest as kube_rest
import logging
import pathlib as pl
from pprint import pprint
import subprocess as sp
import shlex
import sys
import yaml

from ipdb import set_trace


log_name = "dsdo.create_certs"


def create_certs(create_resources=True, config=None):
    log = logging.getLogger(log_name)
    
    route53_script = pl.Path(__file__).parent.\
      joinpath('route53.py')

    domain_name = config['general']['domain']
    cluster_name = config['kops']['cluster_name']

    domains = {
        'ldap': 'ldap.internal.{}.{}'.format(
            cluster_name, domain_name),
        'ldap-ui': 'ldap-ui.internal.{}.{}'.format(
            cluster_name, domain_name),
        }
    
    cmd_template = """
    certbot --text --agree-tos --email eric@ds-do.com \
        --expand --renew-by-default \
        --certbot-external-auth:out-public-ip-logging-ok \
        --configurator certbot-external-auth:out \
        --certbot-external-auth:out-dehydrated-dns \
        --certbot-external-auth:out-handler {r53_script} \
        --staging \
        -d {domain} \
        --work-dir /tmp/le-work/ --logs-dir /tmp/le-logs/ --config-dir /tmp/le-config/ \
        certonly
    """

    for k, domain in domains.items():
        # print(k, v)
        # print(cmd_template.format(domain=v, r53_script=route53_script))
        log.info('Creating domain {} for {}'.format(domain, k))

        cmd = cmd_template.format(domain=domain, r53_script=route53_script)

        process = sp.Popen(shlex.split(cmd), stdout=sp.PIPE)
        for c in iter(lambda: process.stdout.read(1), b''):
            sys.stdout.write(c.decode('utf-8'))

    return 0
    

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
    log.info("Creating certificates (Note: can take a few minutes)")

    parser = arguments.DSDOParser()
    args = parser.parse_args()

    config.load_kube_config()

    config_file = cluster_conf.load_config(args.config_file)
    
    create_resources = not args.delete

    create_certs(create_resources=create_resources, config=config_file)
    
    return 0


if __name__ == "__main__":
    exit(main())
    