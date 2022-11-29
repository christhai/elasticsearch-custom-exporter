# Prometheus ElasticSearch custom Exporter

Leverage custom Elasticsearch APIs to fetch some important data & expose them in Prometheus format.

## Usage

This exporter is meant to be run as a docker container.

To run this exporter locally you can use the following commands:

```bash

# Build the container locally
make build

# Run it: granted that you have an Elasticsearch service available on http://localhost:9200 on your workstation
#
# Note: the http://host.docker.internal:9200 endpoint is meant to let the container reach your localhost:9200 socket.
make run-local extra_args='--interval 10 --endpoint http://host.docker.internal:9200'
```
