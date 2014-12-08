# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import unicode_literals

import os
import sys

from configobj import ConfigObj

def get_config():
    p = os.environ.get('GHFIREHOSE_CONFIG')
    if not p:
        print('GHFIREHOSE_CONFIG env var must be defined')
        sys.exit(1)

    return ConfigObj(infile=p, encoding='utf-8',
        interpolation='ConfigParser')
