# -*- coding: utf-8 -*-

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
# from pymongo.cursor import CursorType


from ipylib.idebug import *



"""몽고DB 클라이언트"""
try:
    CLIENT_PARAMS = {
        'host': 'localhost',
        'port': 27017,
        'document_class': dict,
        'tz_aware': True,
        'connect': True,
        'maxPoolSize': None,
        'minPoolSize': 100,
        'connectTimeoutMS': 60000,
        'waitQueueMultiple': None,
        'retryWrites': True
    }
    client = MongoClient(**CLIENT_PARAMS)
    # The ismaster command is cheap and does not require auth.
    client.admin.command('ismaster')
except ConnectionFailure:
    logger.error(['ConnectionFailure:', ConnectionFailure])
    raise

