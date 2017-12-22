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

    le_prefix = config['general']['lets_encrypt_prefix']

    in_production = config['general']['in_production'].upper() == 'TRUE'
    if in_production:
        staging_flag = ''
    else:
        staging_flag = '--staging'

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
        {staging_flag} \
        -d {domain} \
        --work-dir {le_prefix}work/ --logs-dir {le_prefix}logs/ --config-dir {le_prefix}config/ \
        certonly
    """

    for k, domain in domains.items():
        log.info('Creating domain {} for {}'.format(domain, k))

        cmd = cmd_template.format(domain=domain, 
          r53_script=route53_script, 
          le_prefix=le_prefix,
          staging_flag=staging_flag)
          
        log.info('Running command {}'.format(cmd))

        process = sp.Popen(shlex.split(cmd), stdout=sp.PIPE)
        for c in iter(lambda: process.stdout.read(1), b''):
            sys.stdout.write(c.decode('utf-8'))

    return 0


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
    