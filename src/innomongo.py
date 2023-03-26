# -*- coding: utf-8 -*-
import os
import sys
import re
from itertools import product
import json
import math
from datetime import datetime


from pymongo import collection, MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure
from pymongo.cursor import CursorType

import pandas as pd


from ipylib.idebug import *
from ipylib.idatetime import DatetimeParser
from ipylib.iparser import *
from ipylib.datacls import BaseDataClass
from ipylib.ifile import FileReader, FileWriter



class Database:
    host = 'localhost'
    port = 27017
    document_class = dict
    tz_aware = True
    connect = True
    maxPoolSize = None
    minPoolSize = 100
    connectTimeoutMS = 60000
    waitQueueMultiple = None
    retryWrites = True

    @classmethod
    def params(self):
        li = ['host','port','document_class','tz_aware','connect','maxPoolSize','minPoolSize',
        'connectTimeoutMS','waitQueueMultiple','retryWrites']
        return {a:getattr(self, a) for a in li}


try:
    Client = MongoClient(**Database.params())
    # The ismaster command is cheap and does not require auth.
    Client.admin.command('ismaster')
except ConnectionFailure:
    logger.error(['ConnectionFailure:', ConnectionFailure])
    raise

NAME = None


class Collection(collection.Collection):

    def __init__(self, name, create=False, **kw):
        super().__init__(Client[NAME], name, create, **kw)
    @property
    def name(self): return self._Collection__name
    def select(self, f, type='dcls'):
        try:
            c = self.find(f, limit=1)
            d = list(c)[0]
        except Exception as e: return None
        else:
            if type == 'dcls': return BaseDataClass(**d)
            elif type == 'dict': return d


class SchemaModel(Collection):
    # column: 컬럼명
    # dtype: 데이터 타입
    # role: 역할
    # desc: 설명
    SchemaStructure = ['seq','column','dtype','role','desc']
    SchemaKeyField = 'column'
    modelType = 'SchemaModel'

    def __init__(self, modelName):
        try:
            self.modelName = modelName
            super().__init__(f"_Schema_{modelName}")

            def get_cols(f={}): return self.distinct('column', f)
            self.schema = get_cols()
            self.keycols = get_cols({'role':{'$regex':'key'}})
            self.numcols = get_cols({'dtype':{'$regex':'int|int_abs|float|pct'}})
            self.intcols = get_cols({'dtype':{'$regex':'int|int_abs'}})
            self.flcols = get_cols({'dtype':{'$regex':'float'}})
            self.pctcols = get_cols({'dtype':{'$regex':'pct'}})
            self.dtcols = get_cols({'dtype':{'$regex':'time|date|datetime'}})
            self.strcols = get_cols({'dtype':'str'})

            try:
                c = self.find({}, {'column':1}, sort=[('seq',1)])
                df = pd.DataFrame(list(c))
                self.colseq = list(df.column)
            except Exception as e:
                self.colseq = None
        except Exception as e:
            logger.error([self, self.__init__, e])
            raise

    @property
    def DtypeDict(self):
        cursor = self.find(None, {'_id':0, 'column':1, 'dtype':1})
        return {d['column']:d['dtype'] for d in list(cursor)}
    @property
    def inputFormat(self):
        fmt = {}
        cursor = self.find(None, {'_id':0})
        for d in list(cursor):
            c = d['column']
            dtype = d['dtype']
            if dtype == 'bool': v = True
            elif dtype == 'str': v = None
            elif dtype == 'int': v = 0
            elif dtype == 'datetime': v = datetime.today().isoformat()[:10]
            elif dtype == 'list': v = []
            elif dtype == 'dict': v = {}
            else: raise
            fmt.update({c: v})
        return fmt

    """CSV파일 --> DB"""
    @ctracer
    def create(self, schemaName=None):
        schemaName = self.modelName if schemaName is None else schemaName
        file = os.path.join(conf.SCHEMA_FILE_PATH, f'{schemaName}.csv')
        data = FileReader.read_csv(file)
        if data is None: pass
        else:
            # 컬럼 순서를 정해준다
            for i,d in enumerate(data): d['seq'] = i
            self.drop()
            self.insert_data(data)
    """DB --> CSV파일"""
    @ctracer
    def backup(self):
        cursor = self.find(None, {'_id':0})
        data = list(cursor)
        if len(data) == 0: pass
        else:
            file = os.path.join(DATA_PATH, 'SchemaCSV', schemaName)
            FileWriter.write_csv(file)
    def define_schemaStructure(self, li):
        if isinstance(li, list): self.SchemaStructure = li
        else: raise
    def add_schema(self, input):
        if isinstance(input, list) or isinstance(input, tuple):
            doc = {}
            for k, v in zip(self.SchemaStructure, input):
                if k == self.SchemaKeyField: filter = {k: v}
                doc.update({k: v})
            self.update_one(filter, {'$set':doc}, True)
        elif isinstance(input, dict):
            self.update_one(input, {'$set':input}, True)
        else: raise

    def parse_value(self, field, value):
        # 'field'를 이용하여 dtype을 가져온다
        ddict = self.DtypeDict.copy()
        if field in ddict:
            dtype = ddict[field]
            return DtypeParser(value, dtype)
        else:
            return value
    def parse_data(self, data):
        if isinstance(data, dict): type, data = 'dict', [data]
        elif isinstance(data, list): type, data = 'list', data
        else: raise

        ddict = self.DtypeDict.copy()
        for d in data:
            for k,v in d.items():
                if k in ddict:
                    dtype = ddict[k]
                    if dtype in [None,'None']:
                        pass
                    else:
                        d[k] = DtypeParser(v, dtype)
        return data[0] if type == 'dict' else data
    def astimezone(self, data):
        dtcols = self.dtcols
        for d in data:
            for c in dtcols:
                if c in d:
                    d[c] = DatetimeParser(d[c])
        return data
    def view(self, f=None, p={'_id':0}, sort=[('dtype',1), ('column',1)], **kw):
        cursor = self.find(f, p, sort=sort, **kw)
        df = pd.DataFrame(list(cursor))
        return df.reindex(columns=['column','dtype','role','desc']).fillna('_')


class DataModel(Collection):
    modelType = 'DataModel'

    def __init__(self, modelName=None, extParam=None):
        modelName = self.__class__.__name__ if modelName is None else modelName
        self._modelExtParam = extParam
        collName = modelName if extParam is None else modelName + '_' + extParam

        super().__init__(collName)
        self.modelName = modelName
        self.schema = SchemaModel(modelName)

    @property
    def is_extended(self): return True if hasattr(self, '_modelExtParam') else False
    @property
    def last_dt(self): return self._get_ultimo_dt()
    def _get_ultimo_dt(self, filter=None, colName='dt'):
        cursor = self.find(filter, {colName:1}, sort=[(colName, DESCENDING)], limit=1)
        try:
            d = list(cursor)[0]
            return DatetimeParser(d[colName])
        except Exception as e:
            logger.info(e)
    """JSON파일 --> DB"""
    def create(self):
        # 쌩데이타 로딩
        file = ifile.search_file(f"{self.modelName}.json")
        data = FileReader.read_json(file)
        if data is None: pass
        else:
            # 데이타 파싱: 스키마적용
            data = self.schema.parse_data(data)
            # DB저장
            self.drop()
            self.insert_data(data)
    """DB --> JSON파일"""
    def backup(self, _dir=None, f=None, p=None, s=None, id=False):
        _dir = conf.BACKUP_PATH if _dir is None else _dir
        file = os.path.join(_dir, f"{self.modelName}.json")
        data = self.load(f, p, sort=s)
        for d in data:
            if id: d.update({'_id':str(d['_id'])})
            else: del d['_id']
        FileWriter.write_json(file, data)

    def load(self, f=None, p={'_id':0}, sort=[('dt',-1)], **kw):
        cursor = self.find(f, p, sort=sort, **kw)
        return self.schema.astimezone(list(cursor))
    def upsert_data(self, data):
        keycols = self.schema.keycols
        for d in data:
            if len(keycols) > 0:
                filter = {k:v for k,v in d.items() if k in keycols}
            else:
                filter = d.copy()
            self.update_one(filter, {'$set':d}, True)
    def parse_data(self, data): return self.schema.parse_data(data)
    def dedup(self, subset=None):
        subset = self.schema.distinct('column', {'role':{'$in':['key']}}) if subset is None else subset
        data = self.load()
        df = pd.DataFrame(data)
        cols = list(df.columns)
        subset = [e for e in subset if e in cols]
        TF = df.duplicated(subset=subset, keep='first')
        dup_ids = list(df[TF]._id)
        self.delete_many({'_id':{'$in':dup_ids}})
        logger.info('Done.')
    def insert_document(self, input):
        if isinstance(input, list) or isinstance(input, tuple):
            doc = {}
            for k, v in zip(self.schema.SchemaStructure, input):
                doc.update({k: v})
            self.update_one(filter, {'$set':doc}, True)
        else: raise
    def view(self, f=None, p={'_id':0}, sort=[('dt',-1)], **kw):
        data = self.load(f, p, sort=sort, **kw)
        return pd.DataFrame(data)
