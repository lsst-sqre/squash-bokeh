#!/bin/bash

usage(){
	echo "Usage: $0 <template configuration> <configuration>"
	exit 1
}

if [ "$1" == "" ] || [ "$2" == "" ]; then
    usage
fi

# values returned if the service is not ready
HOST=""
PORT=""

# on minikube we don't have a load balancer ingress IP
if [ "$MINIKUBE" == "true" ]; then
    HOST=$(kubectl get endpoints kubernetes -o jsonpath --template='{.subsets[0].addresses[0].ip}')
    PORT=$(kubectl get services squash-bokeh -o jsonpath --template='{.spec.ports[0].nodePort}')
else
    # on GKE
    WAIT_TIME=5
    while [ "$HOST" == "" ] && [ "$WAIT_TIME" -le 10 ]; do
        echo "Waiting for the service to become available..."
        sleep $(( WAIT_TIME++ ))
        HOST=$(kubectl get service squash-bokeh -o jsonpath --template='{.status.loadBalancer.ingress[0].ip}')
    done
    PORT=443
fi

if [ "$HOST" == "" ] || [ "$PORT" == "" ]; then
    echo "Service is not ready..."
    echo "If you are deploying to a minikube local cluster, make sure you set MINIKUBE=true."
    exit 1
fi

echo "Service address: $HOST:$PORT"

sed -e "
s/{{ TAG }}/${TAG}/
s/{{ HOST }}/${HOST}/
s/{{ PORT }}/\"${PORT}\"/
" $1 > $2
