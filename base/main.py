#!/usr/bin/env python3

"""Prometheus elastic custom exporter

Usage:
  prometheus-elastic-custom-exporter [-v | --verbose] [--port=<port>] [--interval=<seconds>] --endpoint=<elasticsearch> 
  prometheus-elastic-custom-exporter (-h | --help)

Options:
  --endpoint=<elasticsearch>       HTTP endpoint of the Elasticsearch cluster to monitor.
  --interval=<seconds>          Time interval in seconds between elasticsearch checks [default: 60]
  --port=<port>                 Listening port of the exporter. [default: 9210]
  -v, --verbose                 Set log level to DEBUG (much more logs).
  -h, --help                    Show this screen.
"""

import json
from pythonjsonlogger import jsonlogger
import logging
import requests
import time
from prometheus_client import start_http_server, Gauge
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from datetime import datetime
from docopt import docopt

"""
Setup logging & global variables
"""

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter("%(message)%(levelname)%(name)%(asctime)")
logHandler.setFormatter(formatter)
logging.root.addHandler(logHandler)

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


"""
Requests HTTP helpers
"""
ADAPTER = HTTPAdapter(
    max_retries=Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "OPTIONS"],
    )
)
HTTP = requests.Session()
HTTP.mount("https://", ADAPTER)
HTTP.mount("http://", ADAPTER)


"""
Classes
"""


class NodeCPUStatsMetric:
    """Handle metrics related to Elaticsearch Nodes CPU Credits"""

    def __init__(self, endpoint: str):
        """__init__

        Args:
            endpoint (str): Elaticsearch Elasticsearch endpoint
        """
        self.endpoint = endpoint
        self.explain_gauge = Gauge(
            name="elastic_node_cpu_stats",
            documentation="Details got from elastic nodes CPU Stats",
            labelnames=[
                "node",
                "cfs_quota_micros",
                "cfs_period_micros",
            ],
        )

    def fetch_metrics(self):
        """fetch_metrics Fetch all metrics related to EC nodes CPU Stats."""

        self.get_node_cpu_stats()

    def get_node_cpu_stats(self):

        explain_request = HTTP.get(f"{self.endpoint}/_nodes/stats/os", verify=False)
        for id, details in explain_request.json()["nodes"].items():
            try:
                self.explain_gauge.labels(
                    node=details["name"],
                    cfs_quota_micros=details["os"]["cgroup"]["cpu"]["cfs_quota_micros"],
                    cfs_period_micros=details["os"]["cgroup"]["cpu"]["cfs_period_micros"],
                ).set(1.0)
            except KeyError as e:
                LOG.info(
                    "Reason: missing %s from Node stats call",
                    id,
                    e,
                )


"""
Functions
"""


def main():
    """
    CLI entry point
    """

    arguments = docopt(__doc__)

    if arguments["--verbose"]:
        LOG.setLevel(logging.DEBUG)

    # Fetch CLI arguments
    interval = int(arguments["--interval"])
    endpoint = arguments["--endpoint"]
    listening_port = int(arguments["--port"])

    LOG.info("Prometheus Elastic Custom Exporter")
    LOG.info("Elasticsearch endpoint: %s", endpoint)
    LOG.info("Interval between Elasticsearch calls: %s", interval)
    LOG.info("Initialization done")

    res = NodeCPUStatsMetric(endpoint)

    start_http_server(listening_port)
    LOG.info("Listening for Prometheus requests on port %i", listening_port)

    while True:

        res.fetch_metrics()

        time.sleep(interval)


if __name__ == "__main__":
    main()
