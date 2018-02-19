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

from django.utils.translation import ugettext as _


from uds.models.CalendarRule import freqs, CalendarRule
from uds.models.Util import getSqlDatetime

from uds.core.util import log
from uds.core.util import permissions
from uds.core.util.model import processUuid
from uds.core.Environment import Environment
from uds.REST.model import DetailHandler
from uds.REST import NotFound, ResponseError, RequestError
from django.db import IntegrityError

import six
import logging
import datetime

logger = logging.getLogger(__name__)


class CalendarRules(DetailHandler):  # pylint: disable=too-many-public-methods
    '''
    Detail handler for Services, whose parent is a Provider
    '''

    @staticmethod
    def ruleToDict(item, perm):
        '''
        Convert a calRule db item to a dict for a rest response
        :param item: Service item (db)
        :param full: If full is requested, add "extra" fields to complete information
        '''
        retVal = {
            'id': item.uuid,
            'name': item.name,
            'comments': item.comments,
            'start': item.start,
            'end': item.end,
            'frequency': item.frequency,
            'interval': item.interval,
            'duration': item.duration,
            'duration_unit': item.duration_unit,
            'permission': perm
        }

        return retVal

    def getItems(self, parent, item):
        # Check what kind of access do we have to parent provider
        perm = permissions.getEffectivePermission(self._user, parent)
        try:
            if item is None:
                return [CalendarRules.ruleToDict(k, perm) for k in parent.rules.all()]
            else:
                k = parent.rules.get(uuid=processUuid(item))
                return CalendarRules.ruleToDict(k, perm)
        except Exception:
            logger.exception('itemId {}'.format(item))
            self.invalidItemException()

    def getFields(self, parent):
        return [
            {'name': {'title': _('Rule name')}},
            {'start': {'title': _('Starts'), 'type': 'datetime'}},
            {'end': {'title': _('Ends'), 'type': 'date'}},
            {'frequency': {'title': _('Repeats'), 'type': 'dict', 'dict': dict((v[0], six.text_type(v[1])) for v in freqs) }},
            {'interval': {'title': _('Every'), 'type': 'callback'}},
            {'duration': {'title': _('Duration'), 'type': 'callback'}},
            {'comments': {'title': _('Comments')}},
        ]

    def saveItem(self, parent, item):
        # Extract item db fields
        # We need this fields for all
        logger.debug('Saving rule {0} / {1}'.format(parent, item))
        fields = self.readFieldsFromParams(['name', 'comments', 'frequency', 'start', 'end', 'interval', 'duration', 'duration_unit'])

        if int(fields['interval']) < 1:
            self.invalidItemException('Repeat must be greater than zero')

        # Convert timestamps to datetimes
        fields['start'] = datetime.datetime.fromtimestamp(fields['start'])
        if fields['end'] != None:
            fields['end'] = datetime.datetime.fromtimestamp(fields['end'])

        calRule = None
        try:
            if item is None:  # Create new
                calRule = parent.rules.create(**fields)
            else:
                calRule = parent.rules.get(uuid=processUuid(item))
                calRule.__dict__.update(fields)
                calRule.save()
        except CalendarRule.DoesNotExist:
            self.invalidItemException()
        except IntegrityError:  # Duplicate key probably
            raise RequestError(_('Element already exists (duplicate key error)'))
        except Exception as e:
            logger.exception('Saving calendar')
            raise RequestError('incorrect invocation to PUT: {0}'.format(e))

        return self.getItems(parent, calRule.uuid)

    def deleteItem(self, parent, item):
        logger.debug('Deleting rule {} from {}'.format(item, parent))
        try:
            calRule = parent.rules.get(uuid=processUuid(item))
            calRule.calendar.modified = getSqlDatetime()
            calRule.calendar.save()
            calRule.delete()
        except Exception:
            logger.exception('Exception')
            self.invalidItemException()

        return 'deleted'

    def getTitle(self, parent):
        try:
            return _('Rules of {0}').format(parent.name)
        except Exception:
            return _('Current rules')
