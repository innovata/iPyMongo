from importlib import reload


from ipymongodb import database, collection


for module in [database, collection]: reload(module)