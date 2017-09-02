# Docker image for squash-bokeh microservice
FROM python:3.6-slim
LABEL maintainer "afausti@lsst.org"
WORKDIR /opt
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5006
# http://bokeh.pydata.org/en/latest/docs/user_guide/server.html#reverse-proxying-with-nginx-and-ssl

# If running with minikube set a hostname with a proper domain name so that SSL works
CMD if [ ! -z "$SQUASH_MINIKUBE_IP" ]; then echo "$SQUASH_MINIKUBE_IP squash-local.lsst.codes"; fi >> /etc/hosts; bokeh serve --use-xheaders --allow-websocket-origin=$SQUASH_BOKEH_HOST:$SQUASH_BOKEH_PORT app/AMx

