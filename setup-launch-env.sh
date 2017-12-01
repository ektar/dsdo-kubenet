#!/usr/bin/env bash

packages="
jq 
openldap-clients
python-ldap 
telnet
"

echo $packages | xargs sudo yum install -y 

if [ ! -d ~/miniconda ]; then
  echo Installing miniconda
  wget http://repo.continuum.io/miniconda/Miniconda3-3.7.0-Linux-x86_64.sh -O ~/miniconda.sh
  bash ~/miniconda.sh -b -p $HOME/miniconda
  rm ~/miniconda.sh
  export PATH="$HOME/miniconda/bin:$PATH"
fi

PATH_LINE='export PATH="$HOME/miniconda/bin:$PATH"'
grep -q -F "$PATH_LINE" ~/.bashrc || echo $PATH_LINE >> ~/.bashrc

which conda 2>&1 1>/dev/null || echo Execute "source ~/.bashrc" to load conda into path