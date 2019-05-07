# -*- coding: utf-8 -*-
'''
Proxy module for managing HP MFD and Printers

:codeauthor: J Matlock
:maturity:   new
:platform:   any

Usage
=====

.. note::

    Models supported...


Pillar
------

Pillar notes go here!

Proxy Pillar Example
--------------------

.. code-block:: yaml

    proxy:
      proxytype: hp_mfd
      host: 10.10.10.10
'''
from __future__ import absolute_import, print_function, unicode_literals

# Import python stdlib
import copy
import logging


# Import Salt modules
from salt.exceptions import SaltException
import salt.utils.platform
import salt.utils.http

# -----------------------------------------------------------------------------
# proxy properties
# -----------------------------------------------------------------------------

__proxyenabled__ = ['hp_mfd']
# proxy name

# -----------------------------------------------------------------------------
# globals
# -----------------------------------------------------------------------------

__virtualname__ = 'hp_mfd'
log = logging.getLogger(__name__)
hp_mfd_device = {}

# -----------------------------------------------------------------------------
# property functions
# -----------------------------------------------------------------------------


def __virtual__():
    '''
    Only work on proxy
    '''
    try:
        if salt.utils.platform.is_proxy() and \
           __opts__['proxy']['proxytype'] == 'hp_mfd':
            return __virtualname__
    except KeyError:
        pass

    return False
# -----------------------------------------------------------------------------
# proxy functions
# -----------------------------------------------------------------------------


def init(opts):
    '''
    Open the connection to the HP MFD (Printer) via HTTPS.
    '''
    proxy_dict = opts.get('proxy', {})
    conn_args = copy.deepcopy(proxy_dict)
    conn_args.pop('proxytype', None)
    opts['multiprocessing'] = conn_args.pop('multiprocessing', True)
    # This is not a SSH-based proxy, so it should be safe to enable
    # multiprocessing.
    host = conn_args.pop('host', None)
    model_type = conn_args.pop('model_type', None)

    if model_type.lower() == 'mfd'.lower():
        try:
            # Try retrieving data from HP Printer
            response = salt.utils.http.query(
                'https://%s/hp/device/DeviceStatus/Index' % host,
                method='GET',
                verify_ssl=False,
                status=True,
                backend='tornado'
            )
            status = response.get('status')
            if status == 200:
                hp_mfd_device['conn_args'] = conn_args
                hp_mfd_device['initialized'] = True
                hp_mfd_device['up'] = True
        except SaltException:
            log.error('Unable to connect to %s', conn_args['host'], exc_info=True)
            raise
        return True
    elif model_type.lower() == 'printer'.lower():
        try:
            # Try retrieving data from HP Printer
            response = salt.utils.http.query(
                'https://%s/hp/device/this.LCDispatcher?nav=hp.DeviceStatus' % host,
                method='GET',
                verify_ssl=False,
                status=True,
                backend='tornado'
            )
            status = response.get('status')
            if status == 200:
                hp_mfd_device['conn_args'] = conn_args
                hp_mfd_device['initialized'] = True
                hp_mfd_device['up'] = True
        except SaltException:
            log.error('Unable to connect to %s', conn_args['host'], exc_info=True)
            raise
        return True


def ping():
    '''
    Connection open successfully?
    '''
    return hp_mfd_device.get('up', False)


def initialized():
    '''
    Connection finished initializing?
    '''
    return hp_mfd_device.get('initialized', False)


def shutdown(opts):
    '''
    Closes connection with the device.
    '''
    log.debug('Shutting down the hp_mfd Proxy Minion %s', opts['id'])

# -----------------------------------------------------------------------------
# callable functions
# -----------------------------------------------------------------------------

'''
def get_conn_args():

    conn_args = copy.deepcopy(hp_mfd['conn_args'])
    return conn_args
'''