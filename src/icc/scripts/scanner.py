#!/usr/bin/env python
from configparser import ConfigParser, ExtendedInterpolation
from zope.configuration.xmlconfig import xmlconfig
from pkg_resources import resource_filename, resource_stream
from zope.component import getGlobalSiteManager, getUtility
from zope.interface import Interface
from icc.contentstorage.interfaces import IContentStorage
from icc.contentstorage import splitdigest, hexdigest
import os
import os.path
import pprint

import logging
logger = logging.getLogger('icc.cellula')

package = __name__

ini_file = resource_filename("icc.contentstorage", "../../../icc.cellula.ini")

if ini_file is None:
    raise ValueError('.ini file not found')

_config = ini_file
config_utility = ConfigParser(
    defaults=os.environ, interpolation=ExtendedInterpolation())
config_utility.read(_config)
GSM = getGlobalSiteManager()
GSM.registerUtility(config_utility, Interface, name="configuration")

xmlconfig(resource_stream("icc.cellula", "scanning.zcml"))

storage = getUtility(IContentStorage, name="content")


def callback(phase, filename, count, new):
    if phase == "start":
        print(count, filename, end="")
    else:
        print()

if __name__ == "__main__":
    storage.scan_directories(cb=callback)
