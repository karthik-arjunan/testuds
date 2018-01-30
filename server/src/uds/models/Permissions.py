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

__updated__ = '2015-03-05'

from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext as _
from django.db import models
from django.db.models import Q

from uds.models.UUIDModel import UUIDModel
from uds.models.User import User
from uds.models.Group import Group
from uds.models.Util import getSqlDatetime

import logging

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class Permissions(UUIDModel):
    """
    An OS Manager represents a manager for responding requests for agents inside services.
    """
    # pylint: disable=model-missing-unicode
    # Allowed permissions
    PERMISSION_NONE = 0
    PERMISSION_READ = 32
    PERMISSION_MANAGEMENT = 64
    PERMISSION_ALL = 96

    created = models.DateTimeField(db_index=True)
    ends = models.DateTimeField(db_index=True, null=True, blank=True, default=None)  # Future "permisions ends at this moment", not assigned right now

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permissions', null=True, blank=True, default=None)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='permissions', null=True, blank=True, default=None)

    object_type = models.SmallIntegerField(default=-1, db_index=True)
    object_id = models.IntegerField(default=None, db_index=True, null=True, blank=True)

    permission = models.SmallIntegerField(default=PERMISSION_NONE, db_index=True)

    @staticmethod
    def permissionAsString(perm):
        return {
            Permissions.PERMISSION_NONE: _('None'),
            Permissions.PERMISSION_READ: _('Read'),
            Permissions.PERMISSION_MANAGEMENT: _('Management'),
            Permissions.PERMISSION_ALL: _('All')
        }.get(perm, _('None'))

    @staticmethod
    def addPermission(**kwargs):
        """
        Adds a permission to an object and an user or group
        """
        user = kwargs.get('user', None)
        group = kwargs.get('group', None)

        if user is not None and group is not None:
            raise Exception('Use only user or group, but not both')

        if user is None and group is None:
            raise Exception('Must at least indicate user or group')

        object_type = kwargs.get('object_type', None)

        if object_type is None:
            raise Exception('At least an object type is required')

        object_id = kwargs.get('object_id', None)

        permission = kwargs.get('permission', Permissions.PERMISSION_NONE)

        if user is not None:
            q = Q(user=user)
        else:
            q = Q(group=group)

        try:
            existing = Permissions.objects.filter(q, object_type=object_type, object_id=object_id)[0]
            existing.permission = permission
            existing.save()
            return existing
        except Exception:  # Does not exists
            return Permissions.objects.create(created=getSqlDatetime(), ends=None, user=user, group=group,
                                              object_type=object_type, object_id=object_id, permission=permission)

    @staticmethod
    def getPermissions(**kwargs):
        """
        Retrieves the permission for a given object
        It's mandatory to include at least object_type param

        @param object_type: Required
        @param object_id: Optional
        @param user: Optional, User (db object)
        @param groups: Optional List of db groups
        """
        object_type = kwargs.get('object_type', None)
        if object_type is None:
            raise Exception('Needs at least the object_type field')

        object_id = kwargs.get('object_id', None)

        user = kwargs.get('user', None)
        groups = kwargs.get('groups', [])

        if user is None and len(groups) == 0:
            q = Q()
        else:
            q = Q(user=user) | Q(group__in=groups)

        try:
            perm = Permissions.objects.filter(
                Q(object_type=object_type),
                Q(object_id=None) | Q(object_id=object_id),
                q
            ).order_by('-permission')[0]
            logger.debug('Got permission {}'.format(perm))
            return perm.permission
        except Exception:  # DoesNotExists
            return Permissions.PERMISSION_NONE

    @staticmethod
    def enumeratePermissions(object_type, object_id):
        """
        Get users permissions over object
        """
        return Permissions.objects.filter(object_type=object_type, object_id=object_id)

    @staticmethod
    def cleanPermissions(object_type, object_id):
        Permissions.objects.filter(object_type=object_type, object_id=object_id).delete()

    @staticmethod
    def cleanUserPermissions(user):
        Permissions.objects.filter(user=user).delete()

    @staticmethod
    def cleanGroupPermissions(group):
        Permissions.objects.filter(group=group).delete()

    @property
    def permission_as_string(self):
        return Permissions.permissionAsString(self.permission)

    def __str__(self):
        return 'Permission {}, user {} group {} object_type {} object_id {} permission {}'.format(
            self.uuid, self.user, self.group, self.object_type, self.object_id, Permissions.permissionAsString(self.permission)
        )
