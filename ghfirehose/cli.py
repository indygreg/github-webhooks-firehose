# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import unicode_literals

import datetime
import os
import sys
import tempfile
import time

from collections import Counter

from pkg_resources import resource_string

import which

from ghfirehose import get_config
from ghfirehose.firehose import get_consumer

def start_zookeeper():
    config = get_config()

    p = which.which('zookeeper-server-start.sh')

    template = resource_string(__name__, 'zookeeper.properties.in')

    template = template.replace('{datadir}', config['zookeeper']['datadir'])

    with tempfile.NamedTemporaryFile() as fh:
        fh.write(template)
        fh.flush()

        os.execl(p, p, fh.name)

def start_kafka():
    config = get_config()

    p = which.which('kafka-server-start.sh')

    template = resource_string(__name__, 'kafka.properties.in')

    names = {'broker_id', 'log_dirs', 'host_name', 'port'}

    for k in sorted(names):
        template = template.replace('{%s}' % k, config['kafka'][k])

    with tempfile.NamedTemporaryFile() as fh:
        fh.write(template)
        fh.flush()

        os.execl(p, p, fh.name)

# circus hook that prevents zookeeper from shutting down before Kafka
# detaches.
def signal_zookeeper(watcher, arbiter, hook_name, pid, signum, **kwargs):
    # TODO make implementation robust.
    time.sleep(3)

    return True

def github_event_counts():
    c = get_config()
    consumer = get_consumer(c, auto_commit=False)

    dates = {}

    while True:
        e = consumer.get_event()
        if not e:
            break

        when, event, delivery, signature, payload = e
        dt = datetime.datetime.utcfromtimestamp(when)
        date = dt.date()

        if event in ('ping', 'membership'):
            continue

        repo = payload['repository']['name']

        repos = dates.setdefault(date, {})
        events = repos.setdefault(repo, Counter())
        events[event] += 1

    for date, repos in sorted(dates.iteritems()):
        for repo, events in sorted(repos.iteritems()):
            for event, count in sorted(events.iteritems()):
                print('%s\t%s\t%s\t%d' % (date, repo, event, count))

