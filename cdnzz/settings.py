# coding: utf8

"""


* Copyright (C) 2015 GridSafe, Inc.
"""

import sys
import platform

USER_AGENT = "CDNZZ-SDK/3.0; Python%s.%s; %s" % (
    sys.version_info.major, sys.version_info.minor, platform.system())

API_URL = 'https://www.cdnzz.com/apiv3/json'
API_URL = 'http://127.0.0.1:18888/apiv3/json'

INVALID_TOKEN_ERROR = 10260

