# -*- coding: utf-8 -*-
#
# Copyright (c) 2012 Virtual Cable S.L.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#    * Neither the name of Virtual Cable S.L. nor the names of its contributors
#      may be used to endorse or promote products derived from this software
#      without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
.. moduleauthor:: Adolfo Gómez, dkmaster at dkmon dot com
"""

from __future__ import unicode_literals

__updated__ = '2017-01-31'

from django.db import models

from uds.models.UUIDModel import UUIDModel
from uds.models.Tag import TaggingMixin

import requests
import json
import logging

logger = logging.getLogger(__name__)


class Proxy(UUIDModel, TaggingMixin):
    """
    Proxy DB model
    """
    name = models.CharField(max_length=128, unique=False, db_index=True)
    comments = models.CharField(max_length=256)

    host = models.CharField(max_length=256)
    port = models.PositiveIntegerField(default=9090)
    ssl = models.BooleanField(default=True)
    check_cert = models.BooleanField(default=False)

    class Meta:
        """
        Meta class to declare the name of the table at database
        """
        db_table = 'uds_proxies'
        app_label = 'uds'

    @property
    def url(self):
        return 'http{}://{}:{}'.format('s' if self.ssl is True else '', self.host, self.port)

    @property
    def proxyRequestUrl(self):
        return self.url + "/proxyRequest"

    @property
    def testServerUrl(self):
        return self.url + "/testServer"

    def doProxyRequest(self, url, data=None, timeout=5):
        d = {
            'url': url
        }
        if data is not None:
            d['data'] = data

        return requests.post(
            self.proxyRequestUrl,
            data=json.dumps(d),
            headers={'content-type': 'application/json'},
            verify=self.check_cert,
            timeout=timeout
        )

    def doTestServer(self, ip, port, timeout=5):
        try:
            url = self.testServerUrl + '?host={}&port={}&timeout={}'.format(ip, port, timeout)
            r = requests.get(
                url,
                verify=self.check_cert,
                timeout=timeout
            )
            if r.status_code == 302:  # Proxy returns "Found" for a success test
                return True
            # Else returns 404
        except Exception:
            logger.exception("Getting service state through proxy")

        return False

    def __unicode__(self):
        return 'Proxy {} on {}:{} '.format(self.name, self.host, self.port)
