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

'''
.. moduleauthor:: Adolfo Gómez, dkmaster at dkmon dot com
'''

from django.utils.translation import ugettext as _
from uds.core.services import Publication
from uds.core.util.State import State
from datetime import datetime

import six

import logging


__updated__ = '2016-03-09'


logger = logging.getLogger(__name__)


class LivePublication(Publication):
    '''
    This class provides the publication of a oVirtLinkedService
    '''
    _name = ''
    _reason = ''
    _templateId = ''
    _state = 'r'
    _destroyAfter = 'n'

    suggestedTime = 20  # : Suggested recheck time if publication is unfinished in seconds

    def initialize(self):
        '''
        This method will be invoked by default __init__ of base class, so it gives
        us the oportunity to initialize whataver we need here.

        In our case, we setup a few attributes..
        '''

        # We do not check anything at marshal method, so we ensure that
        # default values are correctly handled by marshal.
        self._name = ''
        self._reason = ''
        self._templateId = ''
        self._state = 'r'
        self._destroyAfter = 'n'

    def marshal(self):
        '''
        returns data from an instance of Sample Publication serialized
        '''
        return '\t'.join(['v1', self._name, self._reason, self._templateId, self._state, self._destroyAfter])

    def unmarshal(self, data):
        '''
        deserializes the data and loads it inside instance.
        '''
        logger.debug('Data: {0}'.format(data))
        vals = data.split('\t')
        if vals[0] == 'v1':
            self._name, self._reason, self._templateId, self._state, self._destroyAfter = vals[1:]

    def publish(self):
        '''
        Realizes the publication of the service
        '''
        self._name = self.service().sanitizeVmName('UDSP ' + self.dsName() + "-" + str(self.revision()))
        self._reason = ''  # No error, no reason for it
        self._destroyAfter = 'n'

        try:
            res = self.service().makeTemplate(self._name)
            logger.debug('Result: {}'.format(res))
            self._templateId = res['id']
            self._state = res['status']
        except Exception as e:
            self._state = 'error'
            self._reason = 'Got error {}'.format(e)
            return State.ERROR

        return State.RUNNING

    def checkState(self):
        '''
        Checks state of publication creation
        '''
        if self._state == 'error':
            return State.ERROR

        if self._state == 'available':
            return State.FINISHED

        self._state = self.service().getTemplate(self._templateId)['status']  # For next check

        if self._destroyAfter == 'y' and self._state == 'available':
            return self.destroy()

        return State.RUNNING

    def finish(self):
        '''
        In our case, finish does nothing
        '''
        pass

    def reasonOfError(self):
        '''
        If a publication produces an error, here we must notify the reason why
        it happened. This will be called just after publish or checkState
        if they return State.ERROR

        Returns an string, in our case, set at checkState
        '''
        return self._reason

    def destroy(self):
        '''
        This is called once a publication is no more needed.

        This method do whatever needed to clean up things, such as
        removing created "external" data (environment gets cleaned by core),
        etc..

        The retunred value is the same as when publishing, State.RUNNING,
        State.FINISHED or State.ERROR.
        '''
        # We do not do anything else to destroy this instance of publication
        if self._state == 'error':
            return  # Nothing to cancel

        if self._state == 'creating':
            self._destroyAfter = 'y'
            return State.RUNNING

        try:
            self.service().removeTemplate(self._templateId)
        except Exception as e:
            self._state = 'error'
            self._reason = six.text_type(e)
            return State.ERROR

        return State.FINISHED

    def cancel(self):
        '''
        Do same thing as destroy
        '''
        return self.destroy()

    # Here ends the publication needed methods.
    # Methods provided below are specific for this publication
    # and will be used by user deployments that uses this kind of publication

    def getTemplateId(self):
        '''
        Returns the template id associated with the publication
        '''
        return self._templateId
