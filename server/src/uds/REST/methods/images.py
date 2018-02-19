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

"""
@itemor: Adolfo Gómez, dkmaster at dkmon dot com
"""
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _, ugettext
from uds.models import Image
from uds.core.ui.UserInterface import gui

from uds.REST.model import ModelHandler

import logging

logger = logging.getLogger(__name__)

# Enclosed methods under /item path


class Images(ModelHandler):
    """
    Handles the gallery REST interface
    """
    # needs_admin = True

    path = 'gallery'
    model = Image
    save_fields = ['name', 'data']

    table_title = _('Image Gallery')
    table_fields = [
        {'thumb': {'title': _('Image'), 'visible': True, 'type': 'image', 'width': '96px' }},
        {'name': {'title': _('Name')}},
        {'size': {'title': _('Size')}},
    ]

    def beforeSave(self, fields):
        fields['data'] = Image.prepareForDb(Image.decode64(fields['data']))

    def afterSave(self, item):
        # Updates the thumbnail and re-saves it
        logger.debug('After save: item = {}'.format(item))
        item.updateThumbnail()
        item.save()

    def getGui(self, type_):
        return self.addField(
            self.addDefaultFields([], ['name']), {
                'name': 'data',
                'value': '',
                'label': ugettext('Image'),
                'tooltip': ugettext('Image object'),
                'type': gui.InputField.IMAGECHOICE_TYPE,
                'order': 100,  # At end
            }
        )

    def item_as_dict(self, item):
        return {
            'id': item.uuid,
            'name': item.name,
            'data': item.data64,
        }

    def item_as_dict_overview(self, item):
        return {
            'id': item.uuid,
            'size': '{}x{}, {} bytes (thumb {} bytes)'.format(item.width, item.height, len(item.data), len(item.thumb)),
            'name': item.name,
            'thumb': item.thumb64,
        }
