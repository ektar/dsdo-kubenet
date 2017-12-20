#!/usr/bin/env bash

# Install required packages
packages="
jq 
openldap-clients
python-ldap 
telnet
"

echo $packages | xargs sudo yum install -y 

# Install KOPS
if [ ! -f /usr/local/bin/kops ]; then
  wget -O kops https://github.com/kubernetes/kops/releases/download/$(curl -s https://api.github.com/repos/kubernetes/kops/releases/latest | grep tag_name | cut -d '"' -f 4)/kops-linux-amd64
  chmod +x ./kops
  sudo mv ./kops /usr/local/bin/
fi

# Install kubectl
if [ ! -f /usr/local/bin/kubectl ]; then
  wget -O kubectl https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
  chmod +x ./kubectl
  sudo mv ./kubectl /usr/local/bin/kubectl
fi

# Install helm
if [ ! -f /usr/local/bin/helm ]; then
  curl https://raw.githubusercontent.com/kubernetes/helm/master/scripts/get > get_helm.sh
  chmod 700 get_helm.sh
  ./get_helm.sh
  rm -f ./get_helm.sh
fi

# Install miniconda for python environments
if [ ! -d ~/miniconda ]; then
  echo Installing miniconda
  wget http://repo.continuum.io/miniconda/Miniconda3-3.7.0-Linux-x86_64.sh -O ~/miniconda.sh
  bash ~/miniconda.sh -b -p $HOME/miniconda
  rm ~/miniconda.sh
  export PATH="$HOME/miniconda/bin:$PATH"

  PATH_LINE='export PATH="$HOME/miniconda/bin:$PATH"'
  grep -q -F "$PATH_LINE" ~/.bashrc || echo $PATH_LINE >> ~/.bashrc

  $HOME/miniconda/bin/conda update --yes conda
  
  $HOME/miniconda/bin/conda env create --file environment.yaml
  
  which conda 1>/dev/null 2>&1 || echo Execute "source ~/.bashrc" to load conda into path
fi


