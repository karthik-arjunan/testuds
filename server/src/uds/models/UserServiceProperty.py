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

# pylint: disable=model-missing-unicode, too-many-public-methods

from __future__ import unicode_literals

__updated__ = '2014-11-25'

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from .UserService import UserService
from uds.models.Util import getSqlDatetime

import logging

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class UserServiceProperty(models.Model):
    """
    Properties for User Service.
    The value field is a Text field, so we can put whatever we want in it
    """
    name = models.CharField(max_length=128, db_index=True)
    value = models.TextField(default='')
    user_service = models.ForeignKey(UserService, on_delete=models.CASCADE, related_name='properties')

    class Meta:
        """
        Meta class to declare default order and unique multiple field index
        """
        db_table = 'uds__user_service_property'
        unique_together = (('name', 'user_service'),)
        app_label = 'uds'

    def __str__(self):
        return "Property of {}. {}={}".format(self.user_service.pk, self.name, self.value)
