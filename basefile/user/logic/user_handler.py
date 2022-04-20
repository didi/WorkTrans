#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: user_handler.py
@time: 2020/3/10 16:55
@desc:
'''


import json

from user.service.user_login_log_service import UserLoginLogService
from user.service.user_service import UserService
from utils.myLogger import infoLog


class UserHandler(RequestHandler):

    def post(self, route, *args, **kwargs):
        infoLog.info('handler name: %s; route: %s; request body: %s' % (
        str("UserHandler"), str(route), str(self.request.body.decode('utf-8')).replace('\n', '')))
        if route == "login":
            self.write(self.login())
        elif route == 'logout':
            self.write(self.logout())
        elif route == 'register':
            self.write(self.register())
        elif route == 'loginLogs':
            try:

                self.write(self.loginLogs())
            except Exception as e:
                print(e)

        else:
            self.write({"code": 404, "result": "请求不存在"})

    def login(self):
        """
         {"username":"admin", "password":"1234567"}
        :return:
        """
        try:
            req = json.loads(self.request.body.decode('utf-8'))
            ip = self.request.remote_ip
            print(ip)
        except json.JSONDecodeError:
            return {"code": 101, "result": "json 解析失败"}
        username = req.get("username", None)
        password = req.get("password", None)
        if username is None or password is None:
            return {"code": 101, "result": "用户名或密码 必传"}
        return UserService.login(username, password, ip)

    def logout(self):

        try:
            req = json.loads(self.request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return {"code": 101, "result": "json 解析失败"}
        user_id = req.get("userId", None)
        return UserService.logout(user_id)

    def register(self):
        """
        {"username": "ceshi", "name": "测试", "password": "123456", "groupName": "喔趣"}
        :return:
        """
        try:
            req = json.loads(self.request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return {"code": 101, "result": "json 解析失败"}

        username = req.get("username", None)
        name = req.get("name", None)
        password = req.get("password", None)
        group_name = req.get("groupName", None)
        return UserService.register( username, name, password, group_name)

    def loginLogs(self):
        try:
            req = json.loads(self.request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return {"code": 101, "result": "json 解析失败"}
        user_name = req.get("userName", None)
        user_id = req.get("userId", None)
        start = req.get("start", None)
        end = req.get("end", None)
        page = req.get("page", None)
        size = req.get("size", None)

        return UserLoginLogService.list(user_name, user_id, start, end,  page, size)

