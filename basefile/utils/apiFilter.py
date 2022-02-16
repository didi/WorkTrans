#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: apiFilter.py
@time: 2020/4/1 15:57
@desc:
'''
import json
import traceback
from functools import wraps
from datetime import datetime

from utils.md5Token import Token
from utils.myLogger import infoLog


def apiFilter(group = 'woqu'):
    """
    :param group:  根据不同接口不同的验证方式
    :return:
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            print("123445")
            try:
                req = json.loads(self.request.body.decode('utf-8'))
            except json.JSONDecodeError:
                res_format = {"code": 405, 'result': "json 解析失败"}
                self.set_status(405)
                self.finish(res_format)

            time_str = req.get('timestr', None)
            token = req.get('token', None)
            if time_str is None or token is None:
                code = 405
                result = '非法请求'
                res_format = {"code": code, 'result': result}
                self.set_status(code)
                self.finish(res_format)

            server_token = Token().getToken(time_str)

            client_time = datetime.strptime(str(time_str), "%Y-%m-%d %H:%M:%S.%f")
            server_time = datetime.now()

            gap = server_time - client_time if server_time >= client_time else client_time - server_time
            time_check = gap.seconds

            if time_check >= 1800 or time_check <= -1800:
                code = 405
                result = '非法请求'
            elif token != server_token:
                code = 408
                result = 'token校验失败，非法请求'
            else:
                code = None
                result = None
            if code:
                res_format = {"code": code, 'result': result}
                self.set_status(code)
                self.finish(res_format)
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                infoLog.error(traceback.format_exc())
                self.set_status(400)
                self.finish({"code": 400, 'result': "系统异常"})

        return wrapper
    return decorator
