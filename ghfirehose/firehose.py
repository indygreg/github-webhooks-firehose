# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import time
import uuid

from kafka import (
    KafkaClient,
    SimpleConsumer,
    SimpleProducer,
)

def get_client(hostport):
    # So hacky.
    limit = time.time() + 10
    while time.time() < limit:
        try:
            return KafkaClient(hostport)
        except Exception:
            time.sleep(0.250)
        else:
            break

    raise Exception('could not connect to Kafka in time allowed')


class FirehoseProducer(object):
    def __init__(self, kafka_hostport, topic):
        self.kafka = get_client(kafka_hostport)
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

class FirehoseConsumer(object):
    def __init__(self, kafka_hostport, topic, group=None):
        if not group:
            group = str(uuid.uuid4())

        self.kafka = get_client(kafka_hostport)
        self.consumer = SimpleConsumer(self.kafka, group, topic,
            auto_commit=False, max_buffer_size=1048576 * 32)

    def get_event(self):
        data = self.consumer.get_message()
        if not data:
            return None

        when, event, delivery, signature, raw = json.loads(data.message.value)
        payload = json.loads(raw)

        return when, event, delivery, signature, payload
