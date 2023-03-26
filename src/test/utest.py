# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.join('C:\\', 'pypjts', 'PyMongoDB', 'src'))


import innomongo
innomongo.NAME = 'PyMongoDB'
print(innomongo.Client['PyMongoDB'])
m = innomongo.Collection('TestTable')
print(m)
print(m.name)
