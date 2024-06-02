# -*- coding: utf-8 -*-

from ipylib.idebug import *


from ipymongodb.client import client 



def get_db(db_name):
    return client[db_name]


def __collection_names__(db_name, pat):
    f = {'name':{'$regex':pat, '$options':'i'}}
    # f = {}
    db = client[db_name]
    return db.list_collection_names(filter=f)


def collection_names(db_name, pat):
    names = __collection_names__(db_name, pat)
    logger.debug({'컬렉션개수': len(names)})
    return sorted(names)


"""데이타모델에 대한 것. 스키마모델은 해당안됨"""
def model_names(db_name, pat):
    names = __collection_names__(db_name, pat)
    models = []
    for name in names:
        _name = name.split('_')[0]
        models.append(_name)
    models = sorted(set(models))

    logger.debug({'모델개수(파생된 컬렉션들은 중복제거)': len(models)})
    return models


