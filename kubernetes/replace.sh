#!/bin/bash
HOST=$(kubectl describe services kubernetes | grep Endpoints | cut -f3 | cut -d: -f1)
PORT=$(kubectl describe services squash-bokeh | grep NodePort | cut -f4 | cut -d/ -f1)
sed -e "
s/{{ TAG }}/${TAG}/
s/{{ HOST }}/${HOST}/
s/{{ PORT }}/\"${PORT}\"/
" $1
