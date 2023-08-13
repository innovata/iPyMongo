# -*- coding: utf-8 -*-
from ipymongodb_test._testenv import *


from ipymongodb import database, collection 


DATABASE_NAME = 'Kiwoom'


# @unittest.skip("class")
class ipymongodb_database(unittest.TestCase):

    def setUp(self): print('\n\n')

    # @unittest.skip('')
    def test001(self): 
        print(database.client)
        pp.pprint(database.client.__dict__)
    # @unittest.skip('')
    def test002(self): 
        db = database.client[DATABASE_NAME]
        print(db)
        pp.pprint(db.__dict__)
    # @unittest.skip('')
    def test003(self): 
        names = database.collection_names(DATABASE_NAME, pat='^opw')
        pp.pprint(names)
        print('\n\n')
        names = database.model_names(DATABASE_NAME, pat='^opw')
        pp.pprint(names)



# @unittest.skip("class")
class ipymongodb_collection(unittest.TestCase):

    def setUp(self): print('\n\n')
    @property 
    def collection(self): return collection.Collection(DATABASE_NAME, 'opw00018_5063318011')
    @property 
    def schemaModel(self): return collection.SchemaModel(DATABASE_NAME, 'opw00018')
    @property 
    def DataModel(self): return collection.DataModel(DATABASE_NAME, 'opw00018')
    
    # @unittest.skip('Collection')
    def test001(self):
        o = self.collection
        print(o)
        pp.pprint(o.__dict__)
        print(sorted(dir(o)))

        print(o.dbName)
        print(o.collName)

    def test002(self):
        o = self.collection
        o.validate()

        o.print_colunqval(['종목명'])

    def test003(self):
        cursor = self.collection.find(limit=1, sort=[('dt',-1)])
        data = list(cursor)
        pp.pprint(data)

    def test004(self):
        dcls = self.collection.select({'종목명': '현대로템'}, type='dcls')
        pp.pprint(dcls.__dict__)

    # @unittest.skip('SchemaModel')
    def test100(self):
        o = self.schemaModel
        print(o)
        pp.pprint(o.__dict__)

        print(o.dbName)
        print(o.collName)
        for attr in ['schema']:
            print(attr, getattr(o, attr))

    def test101(self):
        v = self.schemaModel.DtypeDict
        pp.pprint(v)
    def test102(self):
        v = self.schemaModel.inputFormat
        pp.pprint(v)
    def test103(self):
        self.schemaModel.create()
    def test104(self):
        self.schemaModel.backup()
    def test105(self):
        self.schemaModel.add_schema()
    def test106(self):
        self.schemaModel.parse_value()
    def test107(self):
        self.schemaModel.parse_data()
    def test108(self):
        df = self.schemaModel.view()
        print(df)

    # @unittest.skip('DataModel')
    def test200(self):
        o = self.DataModel
        print(o)
        pp.pprint(o.__dict__)

        attrs = [
            'dbName',
            'collName',
            'schema',
            'is_extended',
            'last_dt',
        ]
        for attr in attrs: print([attr, getattr(o, attr)])
    def test201(self):
        df = self.DataModel.view(limit=10)
        print(df)
    def test202(self):
        v = self.DataModel._get_ultimo_dt()
        print(v)

    # @unittest.skip('Functions')
    def test300(self):
        v = collection.find_schemaModel(DATABASE_NAME, 'opw00018')
        print(v)
        self.assertTrue(isinstance(v, collection.SchemaModel))

        v = collection.find_schemaModel(DATABASE_NAME, '아무거나')
        print(v)
        self.assertEqual(v, None)






if __name__ == "__main__":
    unittest.main(
        module='__main__',
        argv=None,
        testRunner=None,
        testLoader=unittest.defaultTestLoader,
        verbosity=2,
        failfast=None,
        buffer=None,
        warnings=None
    )

    sys.exit(app.exec())
