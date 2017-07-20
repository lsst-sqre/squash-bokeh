# squash-bokeh
SQuaSH bokeh microservice

## The squash-bokeh microservice


### Kubernetes deployment

You can provision a Kubernetes cluster in GKE, clone this repo and deploy the `squash-bokeh` microservice using:


```
TAG=latest make deployment
```


and get the external IP address for the service with:
```
kubectl get service squash-bokeh
```

NOTE: if using `minikube` open the service with:

```
minikube service --https squash-bokeh
```

### Deployment steps

#### Build a docker image and push it to docker hub

```
make build push
```

#### Create secrets


NOTE: The [https-nginx](https://github.com/kubernetes/kubernetes/issues/14017)
example from the [secure-the-service](https://kubernetes.io/docs/concepts/services-networking/connect-applications-service/#securing-the-service) session in the kubernetes user guide seems to be out of date.

This is based on kubernetes [TLS Certificates](https://github.com/kubernetes/ingress/blob/master/examples/PREREQUISITES.md#tls-certificates) -
first generate a self signed rsa key and certificate that the server can use for TLS. 

```
make keys
```

Create the `tls-certs` secret used in the deployment configuration. 

```
make secret
```

#### Nginx configuration

Create a config map for the nginx configuration:

```
make configmap 
```

#### Create a deployment

Create a deployment and expose the service:
```
make deployment
```

#### View logs

Use the `kubectl logs` command to view the logs of the `nginx` and `bokeh` containers:

```
kubectl logs deployment/squash-bokeh nginx
kubectl logs deployment/squash-bokeh bokeh
```

#### Run an interactive shell inside a container

Use tab completion or `kubectl get pods` command to find the pod's name and then `kubectl exec` command to run an interactive shell inside the `nginx` or `bokeh` containers:

```
kubectl exec <TAB>  --stdin --tty -c bokeh /bin/sh
```

### Rolling out updates 

```
kubectl rollout history deployment squash-bokeh
```

Modify the `squash-bokeh` image and apply the new configuration using:
  
```
export TAG=<new tag>
make build push update
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

Use the kubectl scale command to scale the `squash-bokeh` deployment:

```
kubectl scale deployments squash-bokeh --replicas=3
```

or change the `squash-bokeh-deployment.yaml` configuration file apply the new configuration:

```
kubectl apply -f squash-bokeh-deployment.yaml
```

Check the deployment changes:

```
kubectl describe deployments squash-bokeh
kubectl get pods
kubectl get replicasets
```


