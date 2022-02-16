#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: collectionUtils.py
@time: 2020/3/26 17:30
@desc:
'''


class CollectionUtils:

    @staticmethod
    def group(scheduleData, key):
        if scheduleData is None:
            return None
        result = {}
        for item in scheduleData:
            _kv = item.get(key, None)
            if _kv is None:
                continue
            items = result.get(_kv, [])
            items.append(item)
            result[_kv] = items
        return result
