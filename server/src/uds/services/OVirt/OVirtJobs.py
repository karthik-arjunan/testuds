# -*- coding: utf-8 -*-

#
# Copyright (c) 2012-2017 Virtual Cable S.L.
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
@author: Adolfo Gómez, dkmaster at dkmon dot com
"""
from __future__ import unicode_literals

from uds.core import jobs
from uds.core.util import log
from uds.core.util.State import State

from uds.models import Provider, Service, getSqlDatetime


import logging
import time

logger = logging.getLogger(__name__)


class OVirtHouseKeeping(jobs.Job):
    frecuency = 60 * 60 * 24 * 15 + 1  # Once every 15 days
    friendly_name = 'Ovirt house keeping'

    def run(self):
        return


class OVirtDeferredRemoval(jobs.Job):
    frecuency = 60 * 5  # Once every NN minutes
    friendly_name = 'Ovirt removal'
    counter = 0

    @staticmethod
    def remove(providerInstance, vmId):
        logger.debug('Adding {} from {} to defeffed removal process'.format(vmId, providerInstance))
        OVirtDeferredRemoval.counter += 1
        try:
            # Tries to stop machine sync when found, if any error is done, defer removal for a scheduled task
            try:
                # First check state & stop machine if needed
                state = providerInstance.getMachineState(vmId)
                if state in ('up', 'powering_up', 'suspended'):
                    providerInstance.stopMachine(vmId)
                elif state != 'unknown':  # Machine exists, remove it later
                    providerInstance.storage.saveData('tr' + vmId, vmId, attr1='tRm')

            except Exception as e:
                providerInstance.storage.saveData('tr' + vmId, vmId, attr1='tRm')
                logger.info('Machine {} could not be removed right now, queued for later: {}'.format(vmId, e))

        except Exception as e:
            logger.warn('Exception got queuing for Removal: {}'.format(e))

    def run(self):
        from .OVirtProvider import Provider as OVirtProvider

        logger.debug('Looking for deferred vm removals')

        # Look for Providers of type VCServiceProvider
        for provider in Provider.objects.filter(maintenance_mode=False, data_type=OVirtProvider.typeType):
            logger.debug('Provider {} if os type ovirt'.format(provider))

            storage = provider.getEnvironment().storage
            instance = provider.getInstance()

            for i in storage.filter('tRm'):
                vmId = i[1]
                try:
                    logger.debug('Found {} for removal {}'.format(vmId, i))
                    # If machine is powered on, tries to stop it
                    # tries to remove in sync mode
                    state = instance.getMachineState(vmId)
                    if state in ('up', 'powering_up', 'suspended'):
                        instance.stopMachine(vmId)
                        return

                    if state != 'unknown':  # Machine exists, try to remove it now
                        instance.removeMachine(vmId)

                    # It this is reached, remove check
                    storage.remove('tr' + vmId)
                except Exception as e:  # Any other exception wil be threated again
                    instance.doLog('Delayed removal of {} has failed: {}. Will retry later'.format(vmId, e))
                    logger.error('Delayed removal of {} failed: {}'.format(i, e))

        logger.debug('Deferred removal finished')
