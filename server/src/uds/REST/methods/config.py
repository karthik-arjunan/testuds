# -*- coding: utf-8 -*-

#
# Copyright (c) 2014 Virtual Cable S.L.
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

'''
@author: Adolfo Gómez, dkmaster at dkmon dot com
'''
from __future__ import unicode_literals

from uds.core.util.Config import Config as cfgConfig

from uds.REST import Handler, AccessDenied

import logging

logger = logging.getLogger(__name__)

# Enclosed methods under /config path


class Config(Handler):
    needs_admin = True  # By default, staff is lower level needed

    def get(self):
        res = {}
        addCrypt = self.is_admin()

        for cfg in cfgConfig.enumerate():
            if cfg.isCrypted() is True and addCrypt is False:
                continue
            # add section if it do not exists
            if cfg.section() not in res:
                res[cfg.section()] = {}
            res[cfg.section()][cfg.key()] = {
                'value': cfg.get(),
                'crypt': cfg.isCrypted(),
                'longText': cfg.isLongText(),
                'type': cfg.getType(),
                'params': cfg.getParams()
            }
        logger.debug('Configuration: {0}'.format(res))
        return res

    def put(self):
        for section, secDict in self._params.iteritems():
            for key, vals in secDict.iteritems():
                cfgConfig.update(section, key, vals['value'])
        return 'done'
