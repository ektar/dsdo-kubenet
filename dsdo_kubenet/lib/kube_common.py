from . import log_conf

import json
from kubernetes import client
import kubernetes.client.rest as kube_rest
import logging
from functools import partial
from time import sleep

from ipdb import set_trace

log_name = "dsdo.kube_common"


class DispatchTable():
    @staticmethod
    def _make_dispatch_rbac_auth_v1beta1():
        k8s = client.RbacAuthorizationV1beta1Api()
        dispatch_table = {
            'create': {
                'ClusterRole': {'func': k8s.create_cluster_role, 'namespaced': False},
                'ClusterRoleBinding': {'func': k8s.create_cluster_role_binding, 'namespaced': False},
                'Role': {'func': k8s.create_namespaced_role, 'namespaced': True},
                'RoleBinding': {'func': k8s.create_namespaced_role_binding, 'namespaced': True},
            },
            'delete': {
                'ClusterRole': {'func': partial(k8s.delete_cluster_role, body={}), 'namespaced': False},
                'ClusterRoleBinding': {'func': partial(k8s.delete_cluster_role_binding, body={}), 'namespaced': False},
                'Role': {'func': partial(k8s.delete_namespaced_role, body={}), 'namespaced': True},
                'RoleBinding': {'func': partial(k8s.delete_namespaced_role_binding, body={}), 'namespaced': True},
            }
        }
        return dispatch_table
    
    @staticmethod
    def _make_dispatch_v1():
        k8s = client.CoreV1Api()
        dispatch_table = {
            'create': {
                'Namespace': {'func': k8s.create_namespace, 'namespaced': False},
                'ConfigMap': {'func': k8s.create_namespaced_config_map, 'namespaced': True},
                'ServiceAccount': {'func': k8s.create_namespaced_service_account, 'namespaced': True},
                'Service': {'func': k8s.create_namespaced_service, 'namespaced': True},
                'PersistentVolumeClaim': {'func': k8s.create_namespaced_persistent_volume_claim, 'namespaced': True},
                'PersistentVolume': {'func': k8s.create_persistent_volume, 'namespaced': False},
                'Pod': {'func': k8s.create_namespaced_pod, 'namespaced': True},
                'Secret': {'func': k8s.create_namespaced_secret, 'namespaced': True},
            },
            'delete': {
                'Namespace': {'func': partial(k8s.delete_namespace, body={}), 'namespaced': False},
                'ConfigMap': {'func': partial(k8s.delete_namespaced_config_map, body={}), 'namespaced': True},
                'ServiceAccount': {'func': partial(k8s.delete_namespaced_service_account, body={}), 'namespaced': True},
                'Service': {'func': k8s.delete_namespaced_service, 'namespaced': True},
                'PersistentVolumeClaim': {'func': partial(k8s.delete_namespaced_persistent_volume_claim, body={}), 'namespaced': True},
                'PersistentVolume': {'func': k8s.delete_persistent_volume, 'namespaced': False},
                'Pod': {'func': partial(k8s.delete_namespaced_pod, body={}), 'namespaced': True},
                'Secret': {'func': partial(k8s.delete_namespaced_secret, body={}), 'namespaced': True},
            }
        }
        return dispatch_table
    
    @staticmethod
    def _make_dispatch_extensions_v1beta1():
        k8s = client.ExtensionsV1beta1Api()
        
        no_orphans_body = client.V1DeleteOptions(
            grace_period_seconds=0,
            propagation_policy="Foreground"
            )
        
        dispatch_table = {
            'create': {
                'Deployment': {'func': k8s.create_namespaced_deployment, 'namespaced': True},
                'DaemonSet': {'func': k8s.create_namespaced_daemon_set, 'namespaced': True},
                'Ingress': {'func': k8s.create_namespaced_ingress, 'namespaced': True}
            },
            'delete': {
                'Deployment': {'func': partial(k8s.delete_namespaced_deployment, body=no_orphans_body), 'namespaced': True},
                'DaemonSet': {'func': partial(k8s.delete_namespaced_daemon_set, body=no_orphans_body), 'namespaced': True},
                'Ingress': {'func': partial(k8s.delete_namespaced_ingress, body={}), 'namespaced': True}
            }
        }
        return dispatch_table
    
    @staticmethod
    def fetch(api_version):
        log = logging.getLogger(log_name)
    
        dispatch_tables = {
            'extensions/v1beta1': DispatchTable._make_dispatch_extensions_v1beta1,
            'v1': DispatchTable._make_dispatch_v1,
            'rbac.authorization.k8s.io/v1beta1': DispatchTable._make_dispatch_rbac_auth_v1beta1
        }
    
        if api_version in dispatch_tables:
            return dispatch_tables[api_version]()
        else:
            raise Exception('Resource api {} unknown'.format(api_version))
        
        
def create_resource(resource):
    log = logging.getLogger(log_name)

    disp_table = DispatchTable.fetch(resource['apiVersion'])

    try:
        if disp_table['create'][resource['kind']]['namespaced']:
            resp = disp_table['create'][resource['kind']]['func'](body=resource, namespace=resource['metadata']['namespace'])
        else:
            resp = disp_table['create'][resource['kind']]['func'](body=resource)    
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


def wait_for_pod_complete(namespace, name):
    log = logging.getLogger(log_name)

    k8s = client.CoreV1Api()

    phase = None
    while phase not in ['Succeeded', 'Failed']:
        sleep(2)
        pod = k8s.read_namespaced_pod_status(name, namespace, pretty=True)
        pod_dict = pod.to_dict()
        phase = pod_dict['status']['phase']
        log.info('Received pod status: {}'.format(phase))
        
    if phase == 'Failed':
        log.warning('Pod failed, status: {}'.format(str(pod)))

    return phase == 'Succeeded'


def delete_resource(resource):
    log = logging.getLogger(log_name)

    disp_table = DispatchTable.fetch(resource['apiVersion'])

    try:
        if disp_table['delete'][resource['kind']]['namespaced']:
            resp = disp_table['delete'][resource['kind']]['func'](name=resource['metadata']['name'], namespace=resource['metadata']['namespace'])
        else:
            resp = disp_table['delete'][resource['kind']]['func'](name=resource['metadata']['name'])    
        log.info("  Resource deleted")
    except KeyError as e:
        msg = 'Resource "{}" not found in dispatch table for api "{}"'.format(
            resource['kind'], resource['apiVersion'])
        log.error(msg)
        raise Exception(msg)
    except kube_rest.ApiException as e:
        error_dat = json.loads(e.body)
        # set_trace()
        if error_dat['reason'] == 'NotFound':
            log.info('  While deleting {}, received {}'.format(resource['kind'], error_dat['reason']))
        else:
            raise Exception('  Error deleting {}: {}'.format(resource['kind'], e))
    except Exception as e:
        # set_trace()
        raise Exception('  Error deleting {}: {}'.format(resource['kind'], e))
