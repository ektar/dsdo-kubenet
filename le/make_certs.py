#!/usr/bin/env python
import shlex
import subprocess as sp
import sys

def main():
    cmd = """
    certbot --text --agree-tos --email eric@ds-do.com \
        --expand --renew-by-default \
        --certbot-external-auth:out-public-ip-logging-ok \
        --configurator certbot-external-auth:out \
        --certbot-external-auth:out-dehydrated-dns \
        --certbot-external-auth:out-handler ./route53.py \
        -d ldap.internal.kube.ds-do.com \
        --work-dir work/ --logs-dir logs/ --config-dir config \
        certonly
    """
    process = sp.Popen(shlex.split(cmd), stdout=sp.PIPE)
    for c in iter(lambda: process.stdout.read(1), b''):
        sys.stdout.write(c.decode('utf-8'))

    return 0
    
if __name__ == "__main__":
    exit(main())