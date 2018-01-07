from ...lib import aws
from ...lib import log_conf
from ...lib import kube_common
from ...lib import arguments
from ...lib import cluster_conf

import argparse
import boto3
from ipdb import set_trace
import json
from kubernetes import client, config
import kubernetes.client.rest as kube_rest
import logging
import pathlib as pl
from pprint import pprint
from time import sleep
import uuid
import yaml

log_name = "dsdo.prepare_efs"


def create_efs(region, vpc_id, subnet_id):
    log = logging.getLogger(log_name)

    efsc = boto3.client('efs')

    efs_id = None

    log.info('Creating file system')

    creation_token = str(uuid.uuid1())

    resp = efsc.create_file_system(
        CreationToken=creation_token,
        PerformanceMode='generalPurpose',
        Encrypted=False
    )

    log.info('Creation id = {}'.format(creation_token))
    
    while resp['LifeCycleState'] != 'available':
        log.info('Waiting for efs to be available, currently "{}"'.format(
            resp['LifeCycleState']))
        sleep(5)
        desc_resp = efsc.describe_file_systems(
            CreationToken=creation_token,
        )
        resp = desc_resp['FileSystems'][0]
    
    efs_id = resp['FileSystemId']

    efsc.create_tags(
        FileSystemId=efs_id, 
        Tags=[{
          'Key': 'Name',
          'Value': 'DS-DO General EFS'
        }])
    
    return efs_id


def list_efs(region, vpc_id, subnet_id):
    log = logging.getLogger(log_name)

    efs_id = None
    
    efsc = boto3.client('efs')

    fs_list = efsc.describe_file_systems()
    
    fs_dict = {}
    for fs in fs_list['FileSystems']:
        fs_id = fs['FileSystemId']
        fs_name = fs.get('Name', '')
        fs_num_mnts = fs['NumberOfMountTargets']
        fs_size = round(fs['SizeInBytes']['Value']/1e9)
        fs_dict[fs_id] = {
            'name': fs_name,
            'num_mounts': fs_num_mnts,
            'size': fs_size
        }

    if len(fs_dict) > 0:
        log.info('Found the following file systems:')
        fs_keys = {}
        for ind, (fs_key, fs_dat) in enumerate(fs_dict.items()):
            fs_keys[ind+1] = fs_key
            log.info('  {}: {} (Name: {}, Size: {} GB)'.
                format(ind+1, fs_key, fs_dat['name'], fs_dat['size']))
        resp = input('Enter file system number ({}) to select, enter to continue: '.
            format(', '.join([str(k) for k in fs_keys.keys()]) ) )
        try:
            efs_id = fs_keys[int(resp)]
        except:
            pass

    return efs_id


def find_efs(config, region, vpc_id, subnet_id):
    log = logging.getLogger(log_name)

    efsc = boto3.client('efs')

    efs_id = config['general']['efs_id']
    
    if efs_id is None:
        log.info('No EFS id specified in config')

        efs_id = list_efs(region, vpc_id, subnet_id)

        if efs_id is None:
            resp = input('No EFS id specified in config, create? (y/N) ') 
            if resp.lower() == 'y':
                efs_id = create_efs(region, vpc_id, subnet_id)

    return efs_id


def get_mount_points(efs_id):
    log = logging.getLogger(log_name)

    efsc = boto3.client('efs')

    resp = efsc.describe_mount_targets(
        FileSystemId=efs_id
        )
    
    return resp['MountTargets']


def mount_point_in_vpc(mount_points, subnet_id, vpc_id):
    log = logging.getLogger(log_name)

    in_vpc = False

    for mnt_pt in mount_points:
        subnet_id = mnt_pt['SubnetId']
        subnet_vpc_id = vpc_from_subnet(subnet_id)
        if subnet_vpc_id == vpc_id:
            in_vpc = True
            break

    return in_vpc


def create_mount_point(efs_id, subnet_id):
    log = logging.getLogger(log_name)

    efsc = boto3.client('efs')

    log.info('Creating mount point (this can take a few minutes...)')
    resp = efsc.create_mount_target(
        FileSystemId=efs_id,
        SubnetId=subnet_id,
    )
    
    mount_target_id = resp['MountTargetId']

    while resp['LifeCycleState'] != 'available':
        log.info('Waiting for mount point to be available, currently "{}"'.format(
            resp['LifeCycleState']))
        sleep(10)
        desc_resp = efsc.describe_mount_targets(
            MountTargetId=mount_target_id
        )
        resp = desc_resp['MountTargets'][0]
    
    return mount_target_id

    
def prepare_efs(efs_id, region):
    log = logging.getLogger(log_name)

    pass


def vpc_from_subnet(subnet_id):
    ec2c = boto3.client('ec2')
    subnet_dat = ec2c.describe_subnets(SubnetIds=[subnet_id])
    vpc_id = subnet_dat['Subnets'][0]['VpcId']
    return vpc_id


def region_from_av(availability_zone):
    ec2c = boto3.client('ec2')
    av_dat = ec2c.describe_availability_zones(ZoneNames=[availability_zone])
    region = av_dat['AvailabilityZones'][0]['RegionName']
    return region


def get_region(config):
    log = logging.getLogger(log_name)

    region = config['general']['region']
    
    if region is None:
        try:
            instance_id = aws.fetch_current_instance_id()
            instance_dat = aws.describe_instance(instance_id=instance_id)
            potential_av = instance_dat['Placement']['AvailabilityZone']
            potential_region = region_from_av(potential_av)
            msg = ("Region not set, terminal running on {}" 
                  ", please set to continue").format(potential_region)
        except:
            msg = "Region not set, please set to continue"
        log.error(msg)
        raise Exception(msg)
    return region
    
    
def get_vpc_id(config):
    log = logging.getLogger(log_name)

    vpc_id = config['general']['vpc_id']
    
    if vpc_id is None:
        try:
            instance_id = aws.fetch_current_instance_id()
            instance_dat = aws.describe_instance(instance_id=instance_id)
            potential_vpc_id = instance_dat['VpcId']
            msg = ("VPC ID not set, terminal running in {}" 
                  ", please set to continue").format(potential_vpc_id)
        except:
            msg = "VPC ID not set, please set to continue"
        log.error(msg)
        raise Exception(msg)

    return vpc_id

    
def get_subnet_id(config):
    log = logging.getLogger(log_name)

    subnet_id = config['general']['efs_subnet_id']
    
    if subnet_id is None:
        try:
            instance_id = aws.fetch_current_instance_id()
            instance_dat = aws.describe_instance(instance_id=instance_id)
            potential_subnet_id = instance_dat['SubnetId']
            msg = ("Subnet ID not set, terminal running in {}" 
                  ", please set to continue").format(potential_subnet_id)
        except:
            msg = "Subnet ID not set, please set to continue"
        log.error(msg)
        raise Exception(msg)

    return subnet_id


def verify_base_settings(region, vpc_id, subnet_id):
    log = logging.getLogger(log_name)

    ec2c = boto3.resource('ec2')
    subnet_dat = ec2c.Subnet(subnet_id)
    
    if subnet_dat.vpc_id != vpc_id:
        msg = ("VPC id from configuration ({}) does not "
               "match VPC id of subnet ({})".format(
                   vpc_id, subnet_dat.vpc_id))
        log.error(msg)
        raise Exception(msg)

    subnet_region = region_from_av(subnet_dat.availability_zone)
    
    if subnet_region != region:
        msg = ("Region from configuration ({}) does not "
               "match region of subnet ({})".format(
                   region, subnet_region))
        log.error(msg)
        raise Exception(msg)

    return True


def entry_point(config=None):
    log = logging.getLogger(log_name)
    
    region = get_region(config)
    vpc_id = get_vpc_id(config)
    subnet_id = get_subnet_id(config)
    
    verify_base_settings(region, vpc_id, subnet_id)

    efs_id = None
    if config['general']['efs_id'] is None:
        efs_id = find_efs(config, region, vpc_id, subnet_id)
        if efs_id is not None:
            log.info('Please set efs_id to {} in your configuration'.format(
                efs_id))
            return 0
        else:
            log.warning('EFS not found')
            return 1
    else:
        efs_id = config['general']['efs_id']

    mount_points = get_mount_points(efs_id)
    
    if not mount_point_in_vpc(mount_points, subnet_id, vpc_id):
        log.info('EFS has no mount points in VPC, need to create')
        create_mount_point(efs_id, subnet_id)

    prepare_efs(efs_id, region)


def main():
    log = logging.getLogger(log_name)
    log.info("Prepare efs")

    parser = arguments.DSDOParser()
    args = parser.parse_args()

    config_data = cluster_conf.load_config(args.config_file)

    config.load_kube_config()
    
    return entry_point(config=config_data)


if __name__ == "__main__":
    main()