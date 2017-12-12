# This is a template
# Saved as .py for easier editing
from __future__ import unicode_literals

# pylint: disable=import-error, no-name-in-module, too-many-format-args, undefined-variable

import win32crypt  # @UnresolvedImport
import os
import subprocess
from uds.forward import forward  # @UnresolvedImport
from uds.log import logger  # @UnresolvedImport

from uds import tools  # @UnresolvedImport

import six

forwardThread, port = forward(sp['tunHost'], sp['tunPort'], sp['tunUser'], sp['tunPass'], sp['ip'], 3389, waitTime=sp['tunWait'])  # @UndefinedVariable

if forwardThread.status == 2:
    raise Exception('Unable to open tunnel')

tools.addTaskToWait(forwardThread)

thePass = six.binary_type('{m.password}'.encode('UTF-16LE'))
try:
    password = win32crypt.CryptProtectData(thePass, None, None, None, None, 0x01).encode('hex')
except Exception:
    # Cannot encrypt for user, trying for machine
    password = win32crypt.CryptProtectData(thePass, None, None, None, None, 0x05).encode('hex')

# The password must be encoded, to be included in a .rdp file, as 'UTF-16LE' before protecting (CtrpyProtectData) it in order to work with mstsc
theFile = sp['as_file'].format(# @UndefinedVariable
    password=password,
    address='127.0.0.1:{}'.format(port)
)

filename = tools.saveTempFile(theFile)
executable = tools.findApp('mstsc.exe')
if executable is None:
    raise Exception('Unable to find mstsc.exe')

subprocess.Popen([executable, filename])
tools.addFileToUnlink(filename)
