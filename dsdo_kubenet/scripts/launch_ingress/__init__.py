from ...lib import log_conf
from kubernetes import client, config
import logging
import pathlib as pl
import yaml


log_name = "dsdo.launch_ingress"

def launch_ingress():
    log = logging.getLogger(log_name)
    
    manifest_dir = pl.Path(__file__).parent.parent.parent.\
      joinpath('manifests').joinpath('nginx-ingress')

    # for f in manifest_dir.glob('*'):
    #     log.info(f)
    
    for resource_name in [
         'namespace', 'default-backend', 'configmap',
         'tcp-services-configmap', 'udp-services-configmap',
         'rbac', 'with-rbac']:
        log.info("Installing ingress resource {}".format(resource_name))
        
        fn = manifest_dir.joinpath("{}.yaml".format(resource_name)).as_posix()
        #with manifest_dir.joinpath("{}.yaml".format(resource_name)).open() as f:
        resource = yaml.load(fn)
        
        # dep = yaml.load(f)
        # k8s_beta = client.ExtensionsV1beta1Api()

def main():
    log = logging.getLogger(log_name)
    log.info("Launch ingress")
    launch_ingress()

if __name__ == "__main__":
    main()