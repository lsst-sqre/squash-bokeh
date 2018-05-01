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

# on GKE
WAIT_TIME=5
while [ "$HOST" == "" ] && [ "$WAIT_TIME" -le 20 ]; do
    echo "Waiting for the service to become available..."
    sleep $(( WAIT_TIME++ ))
    HOST=$(kubectl get service squash-bokeh -o jsonpath --template='{.status.loadBalancer.ingress[0].ip}')
done

if [ "$HOST" == "" ]; then
    echo "Service is not ready..."
    exit 1
fi

PORT=443
echo "Service address: $HOST:$PORT"

NAMESPACE=$(kubectl config current-context)

SQUASH_DASH_HOST="squash-${NAMESPACE}.lsst.codes"

if [ "$NAMESPACE" == "squash-prod" ]; then
    SQUASH_DASH_HOST="squash.lsst.codes"
fi

SQUASH_BOKEH_HOST="squash-bokeh-${NAMESPACE}.lsst.codes"

if [ "$NAMESPACE" == "squash-prod" ]; then
    SQUASH_BOKEH_HOST="squash-bokeh.lsst.codes"
fi

SQUASH_API_URL="https://squash-restful-api-${NAMESPACE}.lsst.codes"

if [ "$NAMESPACE" == "squash-prod" ]; then
    SQUASH_API_URL="https://squash-restful-api.lsst.codes"
fi

if [ -z "$SQUASH_BOKEH_APPS" ]; then
    SQUASH_BOKEH_APPS="monitor code_changes AMx"
fi

sed -e "
s/{{ TAG }}/${TAG}/
s/{{ SQUASH_DASH_HOST }}/${SQUASH_DASH_HOST}/
s/{{ SQUASH_BOKEH_HOST }}/${SQUASH_BOKEH_HOST}/
s|{{ SQUASH_API_URL }}|\"${SQUASH_API_URL}\"|
s|{{ SQUASH_BOKEH_APPS }}|\"${SQUASH_BOKEH_APPS}\"|
" $1 > $2
