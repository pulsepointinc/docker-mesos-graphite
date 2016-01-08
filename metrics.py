#!/usr/bin/env python

from __future__ import print_function
import os
import socket
import sys
import time

import requests


mesos_host = os.environ['MESOS_HOST'] if 'MESOS_HOST' in os.environ else 'localhost'
mesos_port = os.environ['MESOS_PORT'] if 'MESOS_PORT' in os.environ else 5050
graphite_host = os.environ['GRAPHITE_HOST'] if 'GRAPHITE_HOST' in os.environ else 'localhost'
graphite_port = os.environ['GRAPHITE_PORT'] if 'GRAPHITE_PORT' in os.environ else 2003
graphite_timeout = os.environ['GRAPHITE_TIMEOUT'] if 'GRAPHITE_TIMEOUT' in os.environ else 60
interval = os.environ['INTERVAL'] if 'INTERVAL' in os.environ else 60

host = mesos_host.split('.')[0]
prefix = '.'.join([os.environ['GRAPHITE_PREFIX'].rstrip('.'), host]) if 'GRAPHITE_PREFIX' in os.environ else host

mesos_url = "http://{mesos_host}:{mesos_port}/metrics/snapshot".format(
    mesos_host=mesos_host,
    mesos_port=mesos_port,
    )

while True:

    ts = int(time.time())
    snapshot = requests.get(mesos_url).json()

    metrics = [
        "{prefix}.{key} {value} {ts}".format(
            prefix=prefix,
            key=key.replace('/', '.'),
            value=str(value),
            ts=str(ts),
            ) for key, value in snapshot.iteritems()
        ]

    payload = '\n'.join(metrics)+'\n'
    print(payload, file=sys.stderr)

    if 'DRYRUN' in os.environ:
        sys.exit(0)

    sock = socket.socket()
    sock.settimeout(int(graphite_timeout))
    sock.connect((graphite_host, int(graphite_port)))
    sock.sendall(payload)
    sock.close()
    time.sleep(interval)
