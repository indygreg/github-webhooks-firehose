# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import unicode_literals

import os
import sys
import tempfile
import time

from pkg_resources import Requirement, resource_string

import which

from ghfirehose import get_config

def start_zookeeper():
    config = get_config()

    p = which.which('zookeeper-server-start.sh')

    template = resource_string(Requirement.parse('github-firehose'),
        'zookeeper.properties.in')

    template = template.replace('{datadir}', config['zookeeper']['datadir'])

    with tempfile.NamedTemporaryFile() as fh:
        fh.write(template)
        fh.flush()

        os.execl(p, p, fh.name)

def start_kafka():
    config = get_config()

    p = which.which('kafka-server-start.sh')

    template = resource_string(Requirement.parse('github-firehose'),
        'kafka.properties.in')

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
