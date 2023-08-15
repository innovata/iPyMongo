# -*- coding: utf-8 -*-
"""
Collection Level APIs
"""
import os 
from datetime import datetime


from pymongo import collection, ASCENDING, DESCENDING


import pandas as pd


from ipylib.idebug import *
from ipylib import datacls, idatetime, iparser, ifile


from ipymongodb import database




class Collection(collection.Collection):

    def __init__(self, dbName, collName, create=False, **kw):
        db = database.client[dbName]
        self._Database__name = db._Database__name
        super().__init__(db, collName, create, **kw)
    
    @property
    def dbName(self): return self._Database__name
    @property
    def collName(self): return self.name

    def validate(self): 
        db = database.client[self.dbName]
        dic = db.validate_collection(self.collName)
        pp.pprint(dic)
        return dic

    def insert_data(self, data):
        try: self.insert_many(data)
        except Exception as e:
            msg = '빈데이터를 바로 인서트하는 경우는 비일비재하므로, 여기에서 경고처리한다'
            logger.warning([e, msg])
    
    def select(self, f, type='dcls'):
        try:
            c = self.find(f, limit=1)
            d = list(c)[0]
        except Exception as e: return None
        else:
            if type == 'dcls': return datacls.BaseDataClass(**d)
            elif type == 'dict': return d

    def print_colunqval(self, columns): 
        for c in columns:
            li = self.distinct(c)
            print(c, len(li), li if len(li) < 10 else li[:10])


class SchemaModel(Collection):
    # column: 컬럼명
    # dtype: 데이터 타입
    # role: 역할
    # desc: 설명
    SchemaStructure = ['seq','column','dtype','role','desc']
    SchemaKeyField = 'column'
    modelType = 'SchemaModel'

    def __init__(self, dbName, modelName):
        self.modelName = modelName
        collName = f"_Schema_{modelName}"
        super().__init__(dbName, collName)

    def __get_cols__(self, f={}): return self.distinct('column', f)

    def get_cols(self, **kw):
        f = {}
        for k,v in kw.items(): f.update({k: {'$regex': v}})
        return self.distinct('column', f)

    @property
    def schema(self): return self.__get_cols__()
    @property
    def allcols(self): return self.__get_cols__()
    @property
    def keycols(self): return self.__get_cols__({'role':{'$regex':'key'}})
    @property
    def numcols(self): return self.__get_cols__({'dtype':{'$regex':'int|int_abs|float|pct'}})
    @property
    def intcols(self): return self.__get_cols__({'dtype':{'$regex':'int|int_abs'}})
    @property
    def flcols(self): return self.__get_cols__({'dtype':{'$regex':'float'}})
    @property
    def pctcols(self): return self.__get_cols__({'dtype':{'$regex':'pct'}})
    @property
    def dtcols(self): return self.__get_cols__({'dtype':{'$regex':'time|date|datetime'}})
    @property
    def strcols(self): return self.__get_cols__({'dtype':'str'})
    @property
    def colseq(self):
        try:
            c = self.find({}, {'column':1}, sort=[('seq',1)])
            df = pd.DataFrame(list(c))
            return list(df.column)
        except Exception as e:
            pass

    def projection(self, cols, vis=1):
        p = {c: vis for c in cols}
        p.update({'_id':0})
        return p

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
    def create(self, csvFile):
        """SchemaCSV 파일을 읽어들인다"""
        data = ifile.FileReader.read_csv(csvFile)
        if data is None:
            logger.error({'파일': csvFile, 'data': data})
        else:
            # 컬럼 순서를 정해준다
            for i,d in enumerate(data): d['seq'] = i
            self.drop()
            self.insert_data(data)
        
        return pd.DataFrame(data)

    """DB --> CSV파일"""
    @ctracer
    def backup(self, csvFile):
        cursor = self.find(None, {'_id':0})
        data = list(cursor)
        
        if len(data) == 0: 
            logger.error({'파일': csvFile, 'data': data})
        else:
            ifile.FileWriter.write_csv(csvFile, self.colseq, data)

    def add_schema(self, *args, **kwargs):
        _vars = vars()
        if len(args) > 0:
            doc = {}
            columns = self.SchemaStructure.copy()
            columns.remove('seq')
            for k, v in zip(columns, args):
                if k == 'column': f = {k: v}
                doc.update({k: v})
            self.update_one(f, {'$set': doc}, True)
        elif len(kwargs) > 0:
            f = {'column': kwargs.get('column')}
            self.update_one(f, {'$set': kwargs}, True)
        else: 
            logger.error(['스키마정보를 입력하시오.', _vars])

    def parse_value(self, field, value):
        # 'field'를 이용하여 dtype을 가져온다
        ddict = self.DtypeDict.copy()
        if field in ddict:
            dtype = ddict[field]
            return iparser.DtypeParser(value, dtype)
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
                        d[k] = iparser.DtypeParser(v, dtype)
        return data[0] if type == 'dict' else data

    def __view__(self, f, p, sort, **kw):
        cursor = self.find(f, p, sort=sort, **kw)
        df = pd.DataFrame(list(cursor))
        return df.reindex(columns=self.SchemaStructure)
    
    def view(self, f=None, p={'_id':0}, sort=[('dtype',1), ('column',1)], **kw):
        self.delete_many({'column': None})
        df = self.__view__(f, p, sort, **kw)
        return df.fillna('_')


"""스키마모델이 존재하는 체크"""
def find_schemaModel(dbName, modelName):
    collName = f"_Schema_{modelName}"
    names = database.collection_names(dbName, pat=f"^{collName}$")
    if len(names) == 0:
        logger.warning(f"해당모델 '{modelName}'은 스키마가 정의되어 있지 않다")
    elif len(names) == 1:
        return SchemaModel(dbName, modelName)


"""스키마정의없이 사용하는 모델의 datetime컬럼을 파싱"""
def data_astimezone(data, cols):
    for d in data:
        for c in cols:
            try: d.update({c: d[c].astimezone()})
            except Exception as e: pass
    return data


class DataModel(Collection):
    modelType = 'DataModel'

    def __init__(self, dbName, modelName, extParam=None):
        self.modelName = modelName
        self.modelExtParam = extParam
        collName = modelName if extParam is None else modelName + '_' + extParam
        super().__init__(dbName, collName)

    def get_schema(self): return find_schemaModel(self.dbName, self.modelName)
    @property
    def is_extended(self): return True if hasattr(self, 'modelExtParam') else False
    @property
    def last_dt(self): return self._get_ultimo_dt()

    def _get_ultimo_dt(self, filter=None, colName='dt'):
        cursor = self.find(filter, {colName:1}, sort=[(colName, DESCENDING)], limit=1)
        try:
            d = list(cursor)[0]
            return idatetime.DatetimeParser(d[colName])
        except Exception as e:
            logger.info(e)

    """JSON파일 --> DB"""
    def create(self, jsonFile):
        # 쌩데이타 로딩
        data = ifile.FileReader.read_json(jsonFile)
        if data is None: pass
        else:
            # 데이타 파싱: 스키마적용
            schema = self.get_schema()
            if schema is None: 
                pass 
            else:
                data = schema.parse_data(data)
            
            # DB저장
            self.drop()
            self.insert_data(data)

    """DB --> JSON파일"""
    def backup(self, jsonFile, include_ids=False):
        if include_ids:
            data = self.load()
            # _id 를 스트링으로 변환
            for d in data: d.update({'_id': str(d['_id'])})
        else: 
            data = self.load({}, {'_id':0})

        if len(data) > 0:
            ifile.FileWriter.write_json(jsonFile, data)
        else:
            logger.warning('len(data) is 0.')
    
    def load(self, f=None, p={'_id':0}, sort=[('dt',-1)], **kw):
        cursor = self.find(f, p, sort=sort, **kw)
        data = list(cursor)
        logger.debug({'modelName': self.modelName, 'DataLen': len(data)})
        return self.astimezone(data)
    
    def load_frame(self, f=None, p={'_id':0}, sort=[('dt',-1)], **kw):
        data = self.load(f, p, sort, **kw)
        return pd.DataFrame(data)
    
    def __view__(self, f=None, p={'_id':0}, **kw):
        df = self.load_frame(f, p, **kw)
        try:
            return df.reindex(columns=self.viewColumnOrder)
        except Exception as e:
            return df

    def view(self, f=None, p={'_id':0}, sort=[('dt',-1)], **kw):
        return self.__view__(f, p, sort=sort, **kw)
    
    def upsert_data(self, data):
        schema = self.get_schema()
        if schema is None: 
            pass 
        else:
            keycols = schema.keycols
            for d in data:
                if len(keycols) > 0:
                    filter = {k:v for k,v in d.items() if k in keycols}
                else:
                    filter = d.copy()
                self.update_one(filter, {'$set':d}, True)
    
    def parse_data(self, data): 
        schema = self.get_schema()
        if schema is None: 
            return data
        else:
            return schema.parse_data(data)

    """스키마가 없거나, 추가로 특정 컬럼들에 대해 시간대를 조정할 때 사용"""
    def astimezone(self, data, cols=None):
        if cols is None:
            schema = self.get_schema()
            if schema is None: 
                logger.warning(['스키마가 없다면 datetime 컬럼들을 특정해야한다.', self])
                return data 
            else:
                return data_astimezone(data, schema.dtcols)
        else:
            return data_astimezone(data, cols)
    
    """MongoDB 파이프라인을 이용한 중복제거"""
    def __dedup_data__(self, subset):
        fields = [f'${column}' for column in subset]
        pipeline = [
            {
                '$group': {
                    # '_id': '$fieldToCheck',  # Field to check for duplicates
                    '_id': fields,
                    'uniqueIds': {'$addToSet': '$_id'},
                    'count': {'$sum': 1}
                }
            },
            {
                '$match': {
                    'count': {'$gt': 1}
                }
            }
        ]
        # print('\n파이프라인:')
        # pp.pprint(pipeline)

        duplicates = list(self.aggregate(pipeline))
        logger.debug({'DuplicatesLen': len(duplicates)})
        for dup_group in duplicates:
            keep_id, *delete_ids = dup_group['uniqueIds']
            # print([keep_id, len(delete_ids)])
            # df = self.view({'_id': {'$in': delete_ids}}, sort=[('date',1)])
            # print(df)
            # break
            self.delete_many({'_id': {'$in': delete_ids}})
        
    def dedup_data(self, subset=None):
        if subset is None:
            schema = self.get_schema()
            if schema is None: 
                logger.warning([self, '스키마가 없으므로 서브셋을 지정해야 중복작업을 수행할 수 있다'])
            else:
                subset = schema.keycols
                self.__dedup_data__(subset)
        else:
            self.__dedup_data__(subset)

    def insert_document(self, input):
        if isinstance(input, list) or isinstance(input, tuple):
            schema = self.get_schema()
            if schema is None: 
                pass 
            else:
                doc = {}
                for k, v in zip(schema.SchemaStructure, input):
                    doc.update({k: v})
                self.update_one(filter, {'$set':doc}, True)
        else: raise
    
    
    

    


