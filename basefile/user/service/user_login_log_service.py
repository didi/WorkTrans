#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: user_login_log_service.py
@time: 2020/3/10 17:54
@desc:
'''

import datetime
import json

from user.model.user import UserMode
from user.model.user_login_log import UserLogMode
from utils.dateUtils import DateUtils


class UserLoginLogService:

    @classmethod
    def login(self, loginUser: str, loginUserId: str, ip: str):
        if loginUser is None or loginUserId is None:
            return {"code": 101, "message": "日志添加失败"}

        userlog = UserLogMode.findOneNewLonginByUserId(loginUserId)
        loginTime = 1
        if userlog is not None:
            loginTime = userlog.loginTime + 1

        return UserLogMode.insert(loginUser, loginUserId, ip, loginTime)

    @classmethod
    def list(cls, userName: str, userId: str, start: str, end: str, page: int, size: int):
        if page is None or page < 0:
            page = 0
        if size is None or size < 1:
            size = 5
        startDate = None
        endDate = None
        if start is not None and end is not None and len(start) > 1 and len(end) > 1:
            startDate = DateUtils.transTime(start, "%Y-%m-%d")
            endDate = DateUtils.transTime(end, "%Y-%m-%d")

        if startDate is None or endDate is None:
            return {"code": 101, "result": "开始或结束格式不正确"}
        userLos = UserLogMode.query(userName, userId, start, end, page, size)
        if userLos is None:
            return {"code": 101, "result":"暂无数据"}
        data = userLos["data"]
        count = userLos["count"]
        print({"code": 100, "result": "查询成功",  "count": count, "data": data})
        return {"code": 100, "result": "查询成功",  "count": count, "data": data}

    @classmethod
    def logout(cls, userId):
        # FIXME 记录日志
        #  退出登陆 理论上不会不成功的， 所以返回状态 100
        # if userId is None:
        #     return {"code": 100, "result": "传递参数不正确"}
        # FIXME 记录日志
        # user = UserMode.queryUserId(userId)
        # if user is None:
        #     return {"code": 100, "result": "登出员工不存在"}
        # username = user.username
        #  FIXME 目前退出登陆前端删除 jwt, 后端不理会。 如果需要后端也要处理，则新创建一张表 黑名单 储存jwt


        return {"code": 100, "result": "登出成功"}


if __name__ == '__main__':
 pass