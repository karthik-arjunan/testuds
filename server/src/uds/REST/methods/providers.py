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
@author: Adolfo Gómez, dkmaster at dkmon dot com
"""
from __future__ import unicode_literals

from django.utils.translation import ugettext, ugettext_lazy as _
from uds.models import Provider, Service, UserService
from uds.core import services
from uds.core.util.State import State
from uds.core.util import permissions
from uds.core.util.model import processUuid

from .services import Services as DetailServices
from .services_usage import ServicesUsage

from uds.REST import NotFound, RequestError
from uds.REST.model import ModelHandler

import logging

logger = logging.getLogger(__name__)

class Providers(ModelHandler):
    """
    Providers REST handler
    """
    model = Provider
    detail = {
        'services': DetailServices,
        'usage': ServicesUsage
    }

    custom_methods = [('allservices', False), ('service', False), ('maintenance', True)]

    save_fields = ['name', 'comments', 'tags']

    table_title = _('Service providers')

    # Table info fields
    table_fields = [
        {'name': {'title': _('Name'), 'type': 'iconType'}},
        {'comments': {'title': _('Comments')}},
        {'maintenance_state': {'title': _('Status')}},
        {'services_count': {'title': _('Services'), 'type': 'numeric'}},
        {'user_services_count': {'title': _('User Services'), 'type': 'numeric'}},  # , 'width': '132px'
        {'tags': {'title': _('tags'), 'visible': False}},
    ]
    # Field from where to get "class" and prefix for that class, so this will generate "row-state-A, row-state-X, ....
    table_row_style = {'field': 'maintenance_mode', 'prefix': 'row-maintenance-'}

    def item_as_dict(self, provider):
        type_ = provider.getType()

        # Icon can have a lot of data (1-2 Kbytes), but it's not expected to have a lot of services providers, and even so, this will work fine
        offers = [{
            'name': ugettext(t.name()),
            'type': t.type(),
            'description': ugettext(t.description()),
            'icon': t.icon().replace('\n', '')} for t in type_.getServicesTypes()]

        return {
            'id': provider.uuid,
            'name': provider.name,
            'tags': [tag.vtag for tag in provider.tags.all()],
            'services_count': provider.services.count(),
            'user_services_count': UserService.objects.filter(deployed_service__service__provider=provider).exclude(state__in=(State.REMOVED, State.ERROR)).count(),
            'maintenance_mode': provider.maintenance_mode,
            'offers': offers,
            'type': type_.type(),
            'comments': provider.comments,
            'permission': permissions.getEffectivePermission(self._user, provider)
        }

    def checkDelete(self, item):
        if item.services.count() > 0:
            raise RequestError('Can\'t delete providers with services already associated')

    # Types related
    def enum_types(self):
        return services.factory().providers().values()

    # Gui related
    def getGui(self, type_):
        try:
            return self.addDefaultFields(services.factory().lookup(type_).guiDescription(), ['name', 'comments', 'tags'])
        except Exception:
            raise NotFound('type not found')

    def allservices(self):
        """
        Custom method that returns "all existing services", no mater who's his daddy :)
        """
        for s in Service.objects.all():
            try:
                perm = permissions.getEffectivePermission(self._user, s)
                if perm >= permissions.PERMISSION_READ:
                    yield DetailServices.serviceToDict(s, perm, True)
            except Exception:
                logger.exception('Passed service cause type is unknown')

    def service(self):
        """
        Custom method that returns a service by its uuid, no matter who's his daddy
        """
        try:
            service = Service.objects.get(uuid=self._args[1])
            perm = self.ensureAccess(service, permissions.PERMISSION_READ)  # Ensures that we can read this item
            return DetailServices.serviceToDict(service, perm, True)
        except Exception:
            raise RequestError(ugettext('Service not found'))

    def maintenance(self, item):
        """
        Custom method that swaps maintenance mode state for a provider
        :param item:
        """
        self.ensureAccess(item, permissions.PERMISSION_MANAGEMENT)
        item.maintenance_mode = not item.maintenance_mode
        item.save()
        return self.item_as_dict(item)

    def test(self, type_):
        from uds.core.Environment import Environment

        logger.debug('Type: {}'.format(type_))
        spType = services.factory().lookup(type_)

        self.ensureAccess(spType, permissions.PERMISSION_MANAGEMENT, root=True)

        logger.debug('spType: {}'.format(spType))

        dct = self._params.copy()
        dct['_request'] = self._request
        res = spType.test(Environment.getTempEnv(), dct)
        if res[0]:
            return 'ok'
        else:
            return res[1]
