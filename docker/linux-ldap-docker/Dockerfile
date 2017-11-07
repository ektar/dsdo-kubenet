from ektar/linux-ldap:1.0.2
MAINTAINER eric@ds-do.com

RUN export DEBIAN_FRONTEND=noninteractive && \
	apt-get update && apt install -qy \
	docker.io \
&& rm -rf /var/lib/apt/lists/*

RUN usermod -a -G docker ecarlson
RUN usermod -a -G sudo ecarlson

ENTRYPOINT ["/data/startup.sh"]

EXPOSE 22