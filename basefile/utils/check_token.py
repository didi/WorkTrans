#!/usr/bin/env python
# encoding: utf-8

"""
@author: sunsong
@contact: sunsong@didiglobal.com
@file: check_token.py
@time: 2019-08-16 16:47
@desc:
"""

from typing import Tuple
from datetime import datetime

from utils.md5Token import Token


def check_token(token: str, time_str: str) -> Tuple[int, str]:
    """
    验证token
    :param token:
    :param time_str:
    :return: (Code, result) 如果合法请求，code和result都是None
    """
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

    return code, result
