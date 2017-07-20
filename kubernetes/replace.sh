#!/bin/bash

HOST=$(kubectl describe services squash-bokeh | grep Ingress | cut -f4)
PORT=443

if test "$HOST" == ""; then
    echo "It looks like you are running on Minikube..."
    # minikube does not provide an external IP address
    HOST=$(kubectl describe services kubernetes | grep Endpoints | cut -f3 | cut -d: -f1)
    PORT=$(kubectl describe services squash-bokeh | grep NodePort | cut -f4 | cut -d/ -f1)
fi

echo "Service address: $HOST:$PORT"
sed -e "
s/{{ TAG }}/${TAG}/
s/{{ HOST }}/${HOST}/
s/{{ PORT }}/\"${PORT}\"/
" $1 > $2
