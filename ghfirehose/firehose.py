# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import time

from kafka import (
    KafkaClient,
    SimpleProducer,
)

class FirehoseProducer(object):
    def __init__(self, kafka_hostport, topic):
        # So hacky.
        limit = time.time() + 10
        while time.time() < limit:
            try:
                self.kafka = KafkaClient(kafka_hostport)
            except Exception:
                time.sleep(0.250)
            else:
                break

        self.kafka.ensure_topic_exists(topic)
        self.producer = SimpleProducer(self.kafka)
        self.topic = topic

    def write_event(self, event, delivery, signature, raw):
        """Write a GitHub webhook event to the firehose."""
        o = [time.time(), event, delivery, signature, raw]
        msg = json.dumps(o)

        self.producer.send_messages(self.topic, msg)

    def close(self):
        self.kafka.close()
