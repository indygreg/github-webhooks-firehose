========================
GitHub Webhooks Firehose
========================

This project aims to consume a stream of events received from the
GitHub webhooks service.

How It Works
============

GitHub notifies your HTTP server when events occur and the server
writes out these events to Kafka.

That's all it does right now. We may add processing. But if you want
to deploy a webhook right now that records everything that's going
on so you can analyze the firehose later, this project is for you.

Running
=======

::

   virtualenv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python setup.py develop

   <edit your config.ini>

   GHFIREHOSE_CONFIG=config.ini PATH=/path/to/kafka/bin:$PATH circusd config.ini
