from setuptools import setup

setup(
    name='github-firehose',
    version='0.1',
    description='Consume GitHub webhooks to a data firehose',
    author='Gregory Szorc',
    author_email='gps@mozilla.com',
    license='MPL 2.0 and GPL',
    packages=['ghfirehose'],
    entry_points={
        'console_scripts': [
            'start-kafka = ghfirehose.cli:start_kafka',
            'start-zookeeper = ghfirehose.cli:start_zookeeper',
            'github-event-counts = ghfirehose.cli:github_event_counts',
        ],
    },
    package_data={
        'ghfirehose': [
            'kafka.properties.in',
            'zookeeper.properties.in',
        ],
    }
)

