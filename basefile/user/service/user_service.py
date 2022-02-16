#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: user_service.py
@time: 2020/3/9 17:03
@desc:
'''
import datetime
import hashlib
import uuid

import jwt

from config.wse import ws
from user.model.user import UserMode
from user.service.user_login_log_service import UserLoginLogService
from utils.myLogger import infoLog

class UserService:

    @classmethod
    def login(self, username: str, password: str, ip: str):

        message = None
        code = 100

        try:
            user = UserMode.query(username)
            if user is None:
                message = '用户不存在'
                code = 101
            # 前端MD5 加密吧
            print(password)
            if not password == user.password:
                message = '用户名或密码错误'
                code = 101
            else:
                payload = {
                    'id': str(user.userId),
                    'username': user.username,
                    'exp': datetime.datetime.utcnow()
                }
                infoLog.info('key:%s' %(ws.ws["secret_key"]))
                token = jwt.encode(payload, ws.ws["secret_key"], algorithm='HS256')
                result = token.decode('utf-8')

        except Exception as e:
            print(e)
            infoLog.error(e)

            code = 101
            message = '用户不正确'

        if code == 101:
            return {"code": code, "result": message}
        username = user.username
        userId = str(user.userId)
        UserLoginLogService.login(username, userId, ip)
        return {"code": code, "result": "登陆成功","data": {
            "login_json": result,
            "userId": userId,
            "userName":username
        }}

    @classmethod
    def register(cls, username: str, name: str, password: str, groupName: str):

        if username is None or password is None or groupName is None:
            return {"code": 101, "result": "注册失败"}
        if len(password) < 6 or len(password) > 32:
            return {"code": 101, "result": "密码长度在6 - 32 位之间"}
        if groupName not in ["喔趣", "滴滴"]:
            return {"code": 101, "result": "groupName 请选择 喔趣或滴滴"}
        user_id = uuid.uuid4()
        password = hashlib.md5("123456".encode(encoding='UTF-8')).hexdigest()
        result = UserMode.insert(username, password, name, user_id, 0, groupName)

        if result:
            return {"code": 100, "result": "注册成功"}

        return {"code": 101, "result": "注册失败"}

    @classmethod
    def logout(cls, userId):


        return {"code": 100, "result": "登出成功"}


if __name__ == '__main__':
    username = 'admin'
    password = hashlib.md5("123456".encode(encoding='UTF-8')).hexdigest()

    token = UserService.login(username, password,'127.0.0.1')
    print(token["data"]["login_json"])
    data = jwt.decode(token["data"]["login_json"], ws.ws["secret_key"], algorithm='HS256')
    print(data)