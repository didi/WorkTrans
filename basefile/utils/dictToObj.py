#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: dictToObj.py
@time: 2020/3/9 17:49
@desc:
'''

class Dict2Obj(dict):
    def __init__(self, *args, **kwargs):
        super(Dict2Obj, self).__init__(*args, **kwargs)

    def __getattr__(self, key):
        value = self[key]
        if isinstance(value, dict):
            value = Dict2Obj(value)
        return value