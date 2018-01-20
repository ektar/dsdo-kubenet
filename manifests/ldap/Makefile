environment/my-env.startup.yaml: environment/my-env.startup.yaml.template ../../config/custom-vars
	/bin/bash -c "source ../../config/custom-vars && envsubst < environment/my-env.startup.yaml.template > environment/my-env.startup.yaml"

secret.yaml: environment/my-env.startup.yaml environment/my-env.yaml
	STARTUPSEC=$$(./environment/file-to-base64.sh environment/my-env.startup.yaml) && \
	ENVSEC=$$(./environment/file-to-base64.sh environment/my-env.yaml) && \
	sed "s/ENVSEC/$$ENVSEC/" secret.yaml.template | \
	sed "s/STARTUPSEC/$$STARTUPSEC/" > secret.yaml

config.ldif: config.ldif.template ../../config/custom-vars
	/bin/bash -c "source ../../config/custom-vars && envsubst < config.ldif.template > config.ldif"

up: secret.yaml environment/my-env.startup.yaml
	kubectl create -f secret.yaml
	kubectl create -f deployment.yaml
	kubectl create -f service.yaml

populate: config.ldif
	/bin/bash -c 'source ../../config/custom-vars && ldapadd -x -D cn=admin,$${LDAP_BASE} -W -f config.ldif -H ldaps://$${K8S_INGRESS}:30636'

down:
	kubectl delete -f secret.yaml
	kubectl delete -f deployment.yaml
	kubectl delete -f service.yaml

clean:
	rm -f config.ldif environment/my-env.startup.yaml
