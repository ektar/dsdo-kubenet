secret.yaml: environment/my-env.startup.yaml environment/my-env.yaml
	STARTUPSEC=$$(./environment/file-to-base64.sh environment/my-env.startup.yaml) && \
	ENVSEC=$$(./environment/file-to-base64.sh environment/my-env.yaml) && \
	sed "s/ENVSEC/$$ENVSEC/" secret.yaml.template | \
	sed "s/STARTUPSEC/$$STARTUPSEC/" > secret.yaml

up: secret.yaml
	kubectl apply -f secret.yaml
	kubectl apply -f deployment.yaml
	kubectl apply -f service.yaml

down:
	kubectl delete -f service.yaml
	kubectl delete -f deployment.yaml
	kubectl delete -f secret.yaml

