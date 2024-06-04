# -*- coding: utf-8 -*-

# Data Engineering 과정에서 필요한 INPUT, OUTPUT 파일(TXT, CSV, JSON) 에 대한 처리 함수들.

import os 
from pathlib import WindowsPath 
import json 
import re 


import pandas as pd


from ipylib.idebug import *
from ipylib import ifile 







def find_file(_dir, filename):
    results = []
    for root, dirs, files in os.walk(top=_dir, topdown=True):
        for file in files:
            _file = os.path.basename(file)
            if re.search(filename, _file) is not None:
                results.append(os.path.join(root, file))
    return results


def get_file_list(_dir):
    results = []
    for root, dirs, files in os.walk(top=_dir, topdown=True):
        for file in files:
            _file = os.path.basename(file)
            results.append(os.path.join(root, file))
    return results


def read_file(filepath):
    with open(filepath, mode='r', encoding='utf8') as f:
        text = f.read()
        f.close()
    return text.strip() 


def backup(filepath, data):
    # 파일타입에 따라 경로 자동 재설정
    file = os.path.basename(filepath)
    ext = os.path.splitext(filepath)[1]
    filetype = ext.replace('.', '').lower()
    new_dir = os.path.join(os.path.dirname(filepath), filetype.upper())
    new_filepath = os.path.join(new_dir, file)
    
    # 디렉토리 자동생성
    try:
        os.makedirs(new_dir)
    except OSError:
        pass 

    # 파일쓰기
    if filetype == 'json':
        ifile.FileWriter.write_json(new_filepath, data)
    elif filetype == 'csv':
        # ifile.FileWriter.write_csv(new_filepath, data)
        df = pd.DataFrame(data)
        df.to_csv(new_filepath, index=False)
    logger.info(['백업완료. -->', new_filepath])



