# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import, unicode_literals

import ssl
import time
import threading

import irc.bot

from ghfirehose import get_config
from ghfirehose.firehose import get_consumer

def run():
    c = get_config()
    group = c['irc']['kafka_group']

    consumer = get_consumer(c, group=group, auto_commit=False)
    channel = c['irc']['channel']
    if not channel.startswith('#'):
        channel = '#%s' % channel

    bot = IRCBot(c['irc']['host'], int(c['irc']['port']), channel,
        c['irc']['nickname'], is_ssl=c['irc'].get('is_ssl'))

    run = [True]
    thread = BotThread(bot, run)
    thread.start()

    time.sleep(3)

    try:
        while True:
            e = consumer.get_event()
            if not e:
                continue

            when, event, delivery, signature, payload = e

            process_event(when, event, payload, bot)

    finally:
        run[0] = False
        thread.join(2)

def process_event(when, event, p, bot):
    now = time.time()

    # Ignore old events so we don't flood.
    # TODO we should really start replaying from where we left off in the
    # queue.
    if now - when > 15:
        return

    if event == 'ping':
        return

    # TODO handle this.
    if event == 'membership':
        return

    if p['repository']['private']:
        return

    o = p['organization']
    r = p['repository']
    s = p['sender']

    fullname = '%s/%s' % (o['login'], r['name'])

    parts = [
        '\x02\x0312[%s]\x03\x02' % fullname,
    ]

    if event == 'commit_comment':
        parts += [
            s['login'],
            'has commented on a commit:',
            '\x0314%s\x03' % p['comment']['html_url'],
        ]
    elif event == 'create':
        parts += [
            '\x0303%s\x03' % s['login'],
            'created',
            p['ref_type'],
            p['ref'] or '',
        ]
    elif event == 'delete':
        parts += [
            '\x0303%s\x03' % s['login'],
            'deleted',
            p['ref_type'],
            p['ref'],
        ]
    elif event == 'deployment':
        parts += [
            'a deployment started',
        ]
    elif event == 'deployment_status':
        parts += [
            'deployment',
            p['state'],
        ]
    elif event == 'download':
        # Should no longer occur.
        pass
    elif event == 'follow':
        # Should no longer occur.
        pass
    elif event == 'fork':
        parts += [
            'forked to',
            '\x02\x0312%s\x03\x02' % p['forkee']['full_name'],
            '(%d total forks)' % r['forks'],
        ]
    elif event == 'fork_apply':
        # Should no longer occur.
        pass
    elif event == 'gist':
        # Should no longer occur.
        pass
    elif event == 'gollum':
        parts += [
            '\x0303%s\x03' % s['login'],
            'updated %d wiki pages' % len(p['pages']),
        ]
    elif event == 'issue_comment':
        parts += [
            '\x0303%s\x03' % s['login'],
            'commented on an issue:',
            '\x0314%s\x03' % p['comment']['html_url'],
        ]
    elif event == 'issues':
        parts += [
            '\x0303%s\x03' % s['login'],
            p['action'],
            'an issue',
            '\x0314%s\x03' % p['issue']['html_url'],
        ]
    elif event == 'member':
        parts += [
            '\x0303%s\x03' % s['login'],
            'added ',
            s['member']['login'],
            'as a collaborator',
        ]
    elif event == 'membership':
        parts += [
            '\x0303%s\x03' % s['login'],
            p['action'],
            'from' if p['action'] == 'removed' else 'to',
            'team',
            p['team']['name'],
        ]
    elif event == 'page_build':
        parts += [
            'page build',
        ]
    elif event == 'public':
        parts += [
            'repository is now public!',
        ]
    elif event == 'pull_request':
        parts += [
            '\x0303%s\x03' % s['login'],
            p['action'],
            'a pull request:',
            '\x0314%s\x03' % p['pull_request']['html_url'],
        ]
    elif event == 'pull_request_review_comment':
        parts += [
            '\x0303%s\x03' % s['login'],
            'commented on a pull request:',
            '\x0314%s\x03' % p['comment']['html_url'],
        ]
    elif event == 'push':
        parts += [
            '\x0303%s\x03' % s['login'],
            'pushed %d commits to %s' % (len(p['commits']), p['ref']),
        ]
    elif event == 'release':
        parts += [
            '\x0303%s\x03' % s['login'],
            'published a release:',
            '\x0314%s\x03' % s['release']['html_url'],
        ]
    elif event == 'repository':
        parts += [
            'repository has been created!',
        ]
    elif event == 'status':
        parts += [
            '\x0308[commit %s]\x03' % p['sha'][0:7],
            p['description'],
        ]
    elif event == 'team_add':
        parts += [
            p['team']['name'],
            'team was added',
        ]
    elif event == 'watch':
        parts += [
            '\x0303%s\x03' % s['login'],
            'started watching',
        ]
    else:
        parts += [
            'unhandled event:',
            event,
        ]

    msg = ' '.join(parts)
    bot.connection.privmsg(bot.channel, ' '.join(parts))
    time.sleep(1.1)

class IRCBot(irc.bot.SingleServerIRCBot):
    def __init__(self, server, port, channel, nickname, is_ssl=False):
        connect_params = {}
        if is_ssl:
            factory = irc.connection.Factory(wrapper=ssl.wrap_socket)
            connect_params['connect_factory'] = factory

        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)],
            nickname, nickname, **connect_params)

        self.channel = channel

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        self.connection.notice(e.source.nick,
            'I do not respond to private messages yet')

    def on_pubmsg(self, c, e):
        self.connection.send_raw('I do not respond to messages yet')

class BotThread(threading.Thread):
    def __init__(self, bot, alive):
        self.bot = bot
        self.bot_alive = alive
        threading.Thread.__init__(self)

    def run(self):
        self.bot._connect()

        while self.bot_alive[0]:
            self.bot.reactor.process_once(1.0)
