# -*- coding: utf-8 -*-
from ipymongodb import client, database, collection, fileio 

import importlib 

def reload():
    modules = [client, database, collection, fileio]
    for m in modules:
        importlib.reload(m)
        print('Reloaded...', m)
