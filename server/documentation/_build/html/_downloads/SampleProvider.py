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
Created on Jun 22, 2012

.. moduleauthor:: Adolfo Gómez, dkmaster at dkmon dot com
'''

from django.utils.translation import ugettext_noop as translatable, ugettext as _
from uds.core.services import ServiceProvider
from SampleService import ServiceOne, ServiceTwo
from uds.core.ui import gui

import logging

logger = logging.getLogger(__name__)


class Provider(ServiceProvider):
    '''
    This class represents the sample services provider
    
    In this class we provide:
       * The Provider functionality
       * The basic configuration parameters for the provider
       * The form fields needed by administrators to configure this provider
       
       :note: At class level, the translation must be simply marked as so
       using ugettext_noop. This is so cause we will translate the string when
       sent to the administration client.
       
    For this class to get visible at administration client as a provider type,
    we MUST register it at package __init__.
    
    '''
    #: What kind of services we offer, this are classes inherited from Service
    offers = [ServiceOne, ServiceTwo]
    #: Name to show the administrator. This string will be translated BEFORE
    #: sending it to administration interface, so don't forget to
    #: mark it as translatable (using ugettext_noop)
    typeName = translatable('Sample Provider') 
    #: Type used internally to identify this provider
    typeType = 'SampleProvider'
    #: Description shown at administration interface for this provider
    typeDescription = translatable('Sample (and dummy) service provider')
    #: Icon file used as icon for this provider. This string will be translated 
    #: BEFORE sending it to administration interface, so don't forget to
    #: mark it as translatable (using ugettext_noop)
    iconFile = 'provider.png'
    
    # now comes the form fields
    # There is always two fields that are requested to the admin, that are:
    # Service Name, that is a name that the admin uses to name this provider
    # Description, that is a short description that the admin gives to this provider
    # Now we are going to add a few fields that we need to use this provider
    # Remember that these are "dummy" fields, that in fact are not required
    # but used for sample purposes
    # If we don't indicate an order, the output order of fields will be
    # "random"
    
    #: Remote host. Here core will translate label and tooltip, remember to
    #: mark them as translatable using ugettext_noop.
    remoteHost = gui.TextField(oder=1,
                     length = 64,  
                     label = translatable('Remote host'),
                     tooltip = translatable('This fields contains a remote host'),
                     required = True,
                 )
    #: Name of your pet (sample, not really needed :-) )
    petName = gui.TextField(order=2,
                  length = 32,  
                  label = translatable('Your pet\'s name'),
                  tooltip = translatable('If you like, write the name of your pet'),
                  requred = False,
                  defvalue = 'Tux' #: This will not get translated
              )
    #: Age of Methuselah (matusalén in spanish)
    #: in Spain there is a well-known to say that something is very old, 
    #: "Tiene mas años que matusalén"(is older than Methuselah)
    methAge = gui.NumericField(order = 3,
                  length = 4, # That is, max allowed value is 9999  
                  label = translatable('Age of Methuselah'),
                  tooltip = translatable('If you know it, please, tell me!!!'),
                  required = True, #: Numeric fields have always a value, so this not really needed
                  defvalue = '4500'
              )
     
    #: Is Methuselah istill alive?
    methAlive = gui.CheckBoxField(order = 4,
                    label = translatable('Is Methuselah still alive?'),
                    tooltip = translatable('If you fail, this will not get saved :-)'),
                    required = True, #: Also means nothing. Check boxes has always a value
                    defvalue = gui.TRUE #: By default, at new item, check this
                ) 
    
    # There is more fields type, but not here the best place to cover it
    def initialize(self, values = None):
        '''
        We will use the "autosave" feature for form fields, that is more than
        enought for most providers. (We simply need to store data provided by user
        and, maybe, initialize some kind of connection with this values).
        
        Normally provider values are rally used at sevice level, cause we never
        instantiate nothing except a service from a provider.
        '''
        
        # If you say meth is alive, you are wrong!!! (i guess..)
        # values are only passed from administration client. Internals 
        # instantiations are always empty.
        if values is not None and self.methAlive.isTrue():
            raise ServiceProvider.ValidationException(_('Methuselah is not alive!!! :-)'))

    # Marshal and unmarshal are defaults ones, also enought
    
    # As we use "autosave" fields feature, dictValues is also provided by
    # base class so we don't have to mess with all those things...
    
    @staticmethod
    def test(env, data):
        '''
        Create your test method here so the admin can push the "check" button
        and this gets executed.
        Args:
            env: environment passed for testing (temporal environment passed)
            
            data: data passed for testing (data obtained from the form 
            definition)
            
        Returns: 
            Array of two elements, first is True of False, depending on test 
            (True is all right, false is error),
            second is an String with error, preferably internacionalizated..
        
        In this case, wi well do nothing more that use the provider params
        
        Note also that this is an static method, that will be invoked using
        the admin user provided data via administration client, and a temporary
        environment that will be erased after invoking this method
        '''
        try:
            # We instantiate the provider, but this may fail...
            instance = Provider(env, data)
            logger.debug('Methuselah has {0} years and is {1} :-)'
                         .format(instance.methAge.value, instance.methAlive.value))
        except ServiceProvider.ValidationException as e:
            # If we say that meth is alive, instantiation will 
            return [False, str(e)]
        except Exception as e:
            logger.exception("Exception caugth!!!")
            return [False, str(e)]
        return [True, _('Nothing tested, but all went fine..')]

    # Congratulations!!!, the needed part of your first simple provider is done!
    # Now you can go to administration panel, and check it
    #
    # From now onwards, we implement our own methods, that will be used by, 
    # for example, services derived from this provider
    def host(self):
        '''
        Sample method, in fact in this we just return 
        the value of host field, that is an string
        '''
        return self.remoteHost.value
    
    
    def methYears(self):
        '''
        Another sample return, it will in fact return the Methuselah years
        '''
