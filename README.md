# squash-bokeh

The SQuaSH Bokeh serves the squash-bokeh apps, we use the Bokeh plotting library for rich interactive visualizations. You can learn more about SQuaSH at [SQR-009](https://sqr-009.lsst.io).

[![Build Status](https://travis-ci.org/lsst-sqre/squash-bokeh.svg?branch=master)](https://travis-ci.org/lsst-sqre/squash-bokeh)

## Requirements 

`squash-bokeh` requires the [squash-restful-api](https://github.com/lsst-sqre/squash-restful-api) microservice.

### Kubernetes deployment

Assuming you have kubectl configured to access your GCE cluster, you can deploy `squash-bokeh` using:

```
TAG=latest make deployment
```

NOTE: the bokeh apps to be deployed can be configured by setting the following variable:
```
export SQUASH_BOKEH_APPS="code_changes AMx"
```
the default is to deploy all the bokeh apps in the `/app` folder.

Also, it must be consistent with the bokeh apps configured in the [squash](https://github.com/lsst-sqre/squash) deployment.


### Debugging

You can inspect the deployment using:

```
kubectl describe deployment squash-bokeh
```

and view the container logs using:

```
kubectl logs deployment/squash-bokeh nginx
kubectl logs deployment/squash-bokeh bokeh
```

Run an interactive shell inside the `bokeh` container with:

```
kubectl exec -it <TAB> -c bokeh /bin/bash
```

### Rolling out updates

Check the update history with:

```
kubectl rollout history deployment squash-bokeh
```

Modify the `squash-bokeh` image and then apply the new configuration for the kubernetes deployment:

```
TAG=latest make build push update
```

Check the deployment changes:

```
kubectl describe deployments squash-bokeh
```

### Scaling up the squash-bokeh microservice

Use the `kubectl get replicasets` command to view the current set of replicas.

```
kubectl get replicasets
```

Use the `kubectl scale` command to scale the `squash-bokeh` deployment:

```
kubectl scale deployments squash-bokeh --replicas=3
```

or change the `squash-bokeh-deployment.yaml` configuration file and apply the new configuration:

```
kubectl apply -f squash-bokeh-deployment.yaml
```

Check the deployment changes:

```
kubectl describe deployments squash-bokeh
kubectl get pods
kubectl get replicasets
```

## Development workflow


You can install the dependencies and run `squash-bokeh` locally for development

1. Install the software dependencies
```
git clone  https://github.com/lsst-sqre/squash-bokeh.git

cd squash-bokeh

virtualenv env -p python3
source env/bin/activate
pip install -r requirements.txt
```

2. Run the `squash-bokeh`

```
export SQUASH_API_URL=<squash-api url>  # e.g the one from squash-api deployment
bokeh serve --log-level debug --allow-websocket-origin=localhost:5006 app/<name of the bokeh app you want to run>
```

The `squash-bokeh` will run at `http://localhost:5006`.
