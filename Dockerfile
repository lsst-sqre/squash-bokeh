# Docker image for squash-bokeh microservice
FROM python:3.6-slim
LABEL maintainer "afausti@lsst.org"
WORKDIR /opt
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5006
# http://bokeh.pydata.org/en/latest/docs/user_guide/server.html#reverse-proxying-with-nginx-and-ssl
CMD  bokeh serve --use-xheaders --allow-websocket-origin=$SQUASH_BOKEH_SERVICE_HOST:$SQUASH_BOKEH_SERVICE_PORT app/AMx

