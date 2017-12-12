from uds.core import auths
from uds.core.ui.UserInterface import gui
from django.utils.translation import ugettext_noop ass translatable

import logging

logger = logging.getLogger(__name__)

class SampleAuth(auths.Authenticator):
    '''
    This is a sample authenticator
    
    As this, it will provide:
    3 Groups, 'Mortals', 'Gods', 'Daemons'.
    plus groups that we enter at authenticator form, from 
    admin interface
    The required form description for administration interface, so admins can create new authenticators of this kind.

    In this sample, we will provide standard athh, with owner
    drawn login form that will simply show users that has
    been created and allow web user to select one of them.


    for this class to get visible at administration client as    as a authenticator type, we MUST register it at package 
    __init__

    :note: At class level, 
    '''
    typeName = traslatable('Sample Authenticator')
    typeType = 'SampleAuthenticator'
    
    #Description shown at administration level for this 
    #authenticator. 
    #This String will be translated when provided to admin
    #interface
    #using ugettext, so you can mark it as 'translatable' at
    typeDescription = translatable('Sample dummy authenticator')
    iconFile = 'auth.png'
    userNameLabel = translatable('Fake User')
    groupNameLabel = translatable('Fake Group')
    groups = gui.EditableList(label=translatable
