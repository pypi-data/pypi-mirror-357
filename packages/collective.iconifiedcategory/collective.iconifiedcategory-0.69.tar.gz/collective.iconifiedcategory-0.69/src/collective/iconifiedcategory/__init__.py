# -*- coding: utf-8 -*-

from zope.i18nmessageid import MessageFactory

# enable :json type converter
import imio.helpers.converters  # noqa
import logging


logger = logging.getLogger('collective.iconifiedcategory')

CAT_SEPARATOR = '_-_'
CSS_SEPARATOR = '-'
DEFAULT_FILESIZE_LIMIT = 5000000

_ = MessageFactory('collective.iconifiedcategory')
