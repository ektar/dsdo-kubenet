from ektar/linux-base:1.0
MAINTAINER eric@ds-do.com

RUN export DEBIAN_FRONTEND=noninteractive && \
	apt-get update && apt install -qy \
	gosu \
	libpam-ldap \
	ldap-utils \
	libsasl2-dev \
	libldap2-dev \
	libssl-dev \
	nscd \
	python-ldap \
	python-pip \
	sudo \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

RUN pip install ssh-ldap-pubkey

RUN echo "AuthorizedKeysCommand /usr/local/bin/ssh-ldap-pubkey-wrapper\\nAuthorizedKeysCommandUser nobody" >> /etc/ssh/sshd_config

RUN echo "base dc=ds-do,dc=com\\nuri ldap://gw.internal.k8s.ds-do.com:30389\\nldap_version 3\\nbinddn cn=readonly,dc=ds-do,dc=com\\nbindpw readonly321\\nrootbinddn cn=admin,dc=dsp\\npam_password md5" > /etc/ldap.conf
RUN sed -i.bak 's/^\(\(passwd\|group\|shadow\):.*compat\)/\1 ldap/' /etc/nsswitch.conf
RUN sed -i.bak 's/pam_ldap.so use_authtok try_first_pass/pam_ldap.so try_first_pass/' /etc/pam.d/common-password
RUN echo "account required    pam_access.so" >> /etc/pam.d/common-auth

RUN sed -i.bak 's/^#\(PasswordAuthentication yes\)/\1/' /etc/ssh/sshd_config

RUN mkdir /data

COPY startup.sh /data/startup.sh

ENTRYPOINT ["/data/startup.sh"]

EXPOSE 22