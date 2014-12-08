========================
GitHub Webhooks Firehose
========================

This project aims to consume a stream of events received from the
GitHub webhooks service.

How It Works
============

GitHub notifies your HTTP server when events occur and the server
writes out these events to Kafka.

Running
=======

.. code-block: shell

   virtualenv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python setup.py develop

   <edit your config.ini>

   GHFIREHOSE_CONFIG=config PATH=/path/to/kafka/bin:$PATH circusd config.ini
