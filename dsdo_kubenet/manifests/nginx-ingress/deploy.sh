#!/bin/bash

for resource in namespace default-backend configmap \
			  tcp-services-configmap udp-services-configmap \
			  rbac with-rbac; do
    echo $resource
    kubectl apply -f $resource.yaml
    done;

