# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import unicode_literals

import logging

from cornice import Service
from pyramid.config import Configurator

from ghfirehose import get_config
from ghfirehose.firehose import FirehoseProducer

webhooks = Service(name='webhooks', path='/webhook',
    description='Ingest GitHub webhooks')

logger = logging.getLogger('ghfirehose')

@webhooks.post()
def post_webhooks(request):
    # TODO validate source IP is from GitHub by comparing against IP block
    # published by GitHub.

    event = request.headers.get('X-GitHub-Event')
    signature = request.headers.get('X-Hub-Signature', None)
    delivery = request.headers.get('X-Github-Delivery')

    logger.info('got %s' % event)

    request.firehose().write_event(event, delivery, signature, request.body)

    return 'OK'

def main(*args, **settings):
    c = get_config()

    host = c['kafka']['host_name']
    port = c['kafka']['port']
    hostport = '%s:%s' % (host, port)

    topic = c['kafka']['topic'].encode('utf-8')
    producer = FirehoseProducer(hostport, topic)

    def firehose(request):
        if not hasattr(request, '_firehose'):
            request._firehose = producer

        return request._firehose

    config = Configurator()
    config.add_request_method(firehose)
    config.include('cornice')
    config.scan()

    return config.make_wsgi_app()

application = main()
