all:
PREFIX = lsstsqre/squash-bokeh
NGINX_CONFIG = kubernetes/nginx/nginx.conf
REPLACE = ./kubernetes/replace.sh
DEPLOYMENT_TEMPLATE = kubernetes/deployment-template.yaml
DEPLOYMENT_CONFIG = kubernetes/deployment.yaml
SERVICE_CONFIG = kubernetes/service.yaml

build: check-tag
	docker build -t $(PREFIX):${TAG} .

push: check-tag
	docker push $(PREFIX):${TAG}

configmap:
	@echo "Creating config map for nginx configuration..."
	kubectl delete --ignore-not-found=true configmap squash-bokeh-nginx-conf
	kubectl create configmap squash-bokeh-nginx-conf --from-file=$(NGINX_CONFIG)

service:
	@echo "Creating service..."
	kubectl delete --ignore-not-found=true services squash-bokeh
	kubectl create -f $(SERVICE_CONFIG)

# The deployment is created after the service because the external IP
# and port must be sent to the bokeh container

deployment: check-tag configmap
	@echo "Creating deployment..."
	@$(REPLACE) $(DEPLOYMENT_TEMPLATE) $(DEPLOYMENT_CONFIG)
	kubectl delete --ignore-not-found=true deployment squash-bokeh
	kubectl create -f $(DEPLOYMENT_CONFIG)


update: check-tag
	@echo "Updating squash-bokeh deployment..."
	@$(REPLACE) $(DEPLOYMENT_TEMPLATE) $(DEPLOYMENT_CONFIG)
	kubectl apply -f $(DEPLOYMENT_CONFIG) --record
	kubectl rollout history deployment squash-bokeh

clean:
	rm $(DEPLOYMENT_CONFIG)

check-tag:
	@if test -z ${TAG}; then echo "Error: TAG is undefined."; exit 1; fi

