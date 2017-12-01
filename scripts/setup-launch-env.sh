#!/usr/bin/env bash

packages="
jq 
openldap-clients
python-ldap 
telnet
"

echo $packages | xargs sudo yum install -y 

