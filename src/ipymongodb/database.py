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



def __collection_names__(db_name, pat):
    f = {'name':{'$regex':pat, '$options':'i'}}
    # f = {}
    db = client[db_name]
    return db.list_collection_names(filter=f)


def collection_names(db_name, pat):
    names = __collection_names__(db_name, pat)
    logger.info({'컬렉션개수': len(names)})
    return sorted(names)


"""데이타모델에 대한 것. 스키마모델은 해당안됨"""
def model_names(db_name, pat):
    names = __collection_names__(db_name, pat)
    models = []
    for name in names:
        _name = name.split('_')[0]
        models.append(_name)
    models = sorted(set(models))

    logger.info({'모델개수(파생된 컬렉션들은 중복제거)': len(models)})
    return models


