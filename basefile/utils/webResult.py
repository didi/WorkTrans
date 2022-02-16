#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: webResult.py
@time: 2020/3/12 16:47
@desc:
'''


class WebResult:

    def __init__(self, code, result, data, count, isSuccess):
        self.code = code
        self.result = result
        self.data = data
        self.isSuccess = isSuccess
        self.isError = not isSuccess
        self.count = count

    @classmethod
    def success(cls):
        return WebResult(100, "操作成功", None, None, True)

    @classmethod
    def successResult(cls, result):
        return WebResult(100, result, None, None, True)

    @classmethod
    def successData(cls, data, count=None):
        result = WebResult(100, "操作成功", data, count, True)
        return result

    @classmethod
    def errorResult(cls, result):

        return cls.errorCode(101, result)

    @classmethod
    def error(cls):
        return cls.errorCode(101, "操作失败")

    @classmethod
    def errorCode(cls, code, result):
        return WebResult(code, result, None, None, False)

    def __str__(self):
        result = {"code": self.code, "result": self.result}
        if self.data is not None:
            result["data"] = self.data
        if self.count is not None:
            result["count"] = self.count
        return result
