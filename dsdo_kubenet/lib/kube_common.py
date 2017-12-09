from . import log_conf

import json
from kubernetes import client
import kubernetes.client.rest as kube_rest
import logging

log_name = "dsdo.launch_ingress"


def fetch_dispatch_table(api_version):
    log = logging.getLogger(log_name)

    dispatch_tables = dict()
    
    k8s = client.RbacAuthorizationV1beta1Api()
    dispatch_tables['rbac.authorization.k8s.io/v1beta1'] = {
        'ClusterRole': {'func': k8s.create_cluster_role, 'namespaced': False},
        'ClusterRoleBinding': {'func': k8s.create_cluster_role_binding, 'namespaced': False},
        'Role': {'func': k8s.create_namespaced_role, 'namespaced': True},
        'RoleBinding': {'func': k8s.create_namespaced_role_binding, 'namespaced': True}
    }

    k8s = client.CoreV1Api()
    dispatch_tables['v1'] = {
        'Namespace': {'func': k8s.create_namespace, 'namespaced': False},
        'ConfigMap': {'func': k8s.create_namespaced_config_map, 'namespaced': True},
        'ServiceAccount': {'func': k8s.create_namespaced_service_account, 'namespaced': True},
        'Service': {'func': k8s.create_namespaced_service, 'namespaced': True}
    }

    k8s = client.ExtensionsV1beta1Api()
    dispatch_tables['extensions/v1beta1'] = {
        'Deployment': {'func': k8s.create_namespaced_deployment, 'namespaced': True},
        'DaemonSet': {'func': k8s.create_namespaced_daemon_set, 'namespaced': True}
    }

    if api_version in dispatch_tables:
        return dispatch_tables[api_version]
    else:
        raise Exception('Resource api {} unknown'.format(api_version))
        
        
def create_resource(resource):
    log = logging.getLogger(log_name)

    disp_table = fetch_dispatch_table(resource['apiVersion'])

    try:
        if disp_table[resource['kind']]['namespaced']:
            resp = disp_table[resource['kind']]['func'](body=resource, namespace=resource['metadata']['namespace'])
        else:
            resp = disp_table[resource['kind']]['func'](body=resource)    
        log.info("  Resource created")
    except KeyError as e:
        msg = 'Resource "{}" not found in dispatch table for api "{}"'.format(
            resource['kind'], resource['apiVersion'])
        log.error(msg)
        raise Exception(msg)
    except kube_rest.ApiException as e:
        error_dat = json.loads(e.body)
        if error_dat['reason'] == 'AlreadyExists':
            log.info('  While creating {}, received {}'.format(resource['kind'], error_dat['reason']))
        else:
            raise Exception('  Error creating {}: {}'.format(resource['kind'], e))
    except Exception as e:
        raise Exception('  Error creating {}: {}'.format(resource['kind'], e))
