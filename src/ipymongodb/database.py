# -*- coding: utf-8 -*-
import os
# from datetime import datetime


from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
# from pymongo.cursor import CursorType


from ipylib.idebug import *
# from ipylib.datacls import BaseDataClass



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


def get_db(db_name): return client[db_name]


def print_colunqval(m, cols):
    for c in cols:
        li = m.distinct(c)
        print(c, len(li), li if len(li) < 10 else li[:10])


def validate_collection(m): pp.pprint(db.validate_collection(m.collName))


def collection_names(pat):
    f = {'name':{'$regex':pat, '$options':'i'}}
    # f = {}
    names = db.list_collection_names(filter=f)
    print({'컬렉션Len': len(names)})
    def __view__(name):
        _names = []
        for name in names:
            _name = name.split('_')[0]
            _names.append(_name)
        _names = sorted(set(_names))
        print({'모델명': _names})

    __view__(names)
    return sorted(names)


