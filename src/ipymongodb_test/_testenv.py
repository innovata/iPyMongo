# -*- coding: utf-8 -*-
"""파이썬 모듈 로딩"""
import os
import sys
import unittest
from time import sleep
import re
from datetime import datetime, timedelta
from importlib import reload


import pandas as pd


"""프로젝트&내라이브러리 패키지 경로 설정"""
sys.path.append(os.path.join('C:\pypjts', 'iPyMongo', 'src'))
print()
for p in sorted(sys.path): print(p)


"""써드파티 패키지/모듈 로딩"""
os.environ['LOG_LEVEL'] = '10'
from ipylib.idebug import *
from ipylib import idebug, datacls, idatetime


idebug.platformInfo()


"""OS.ENVIRON 설정값"""
# dbg.dict(os.environ)


"""디버거 환경설정"""

dbg.set_viewEnvType('print')
# dbg.report()


