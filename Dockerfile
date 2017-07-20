# Docker image for squash-bokeh microservice
FROM python:3.6-slim
LABEL maintainer "afausti@lsst.org"
WORKDIR /opt
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5006
CMD  bokeh serve --allow-websocket-origin=$SQUASH_BOKEH_SERVICE_HOST:$SQUASH_BOKEH_SERVICE_PORT app/AMx

