# iPyMongoDB (innovata-pymongo-database)
 
파이썬 pymongo 패키지 Wrapper

주로 동적 스키마모델을 사용할 수 있고, 데이터모델을 통해 데이터에 대한 dtype을 이용한 파싱 및 데이터 핸들링 기능 제공한다.

pymongo 패키지에서 제공하는 모든 기능을 제공하지 않는다.


## 사용법 

#### Database 레벨

    from ipymongodb import database 
    names = database.collection_names(dbName, 'collectionNameRegex')

#### Collection 레벨

    from ipymongodb import collection
    schema = collection.SchemaModel(dbName, modelName)
    model = collection.DataModel(dbName, modelName)

하나의 모델에 대해 컬렉션을 확장할 때

    model = collection.DataModel(dbName, modelName, extParam='20230101')
    model.collName
    >> modelName_20230101

