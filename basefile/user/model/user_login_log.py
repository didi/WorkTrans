#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: user_login_log.py
@time: 2020/3/11 11:07
@desc:
'''

from utils.dictToObj import Dict2Obj
from utils.testDBPool import DBPOOL
from utils.myLogger import infoLog
import pymysql


class userLog:

    def __init__(self, id, login_user, login_user_id, insert_time, ip, login_time):
        self.id = id
        self.loginUser = login_user
        self.loginUserId = login_user_id
        self.insertTime = insert_time
        self.ip = ip
        self.loginTime = login_time


class UserLogMode:

    @classmethod
    def query(cls, userName: str, userId: str, start: str, end: str, page: str, size: str):
        if start is None or end is None:
            return None
        hasPage = False
        if (page is not None and page > -1) and (size is not None and size > 0):
            hasPage = True
        conn = DBPOOL.connection()

        where = 'insert_time >= "{}" and insert_time < "{}"'.format(start, end)

        if userName is not None:
            where = where + (" and login_user like '%{}%' ".format(userName))

        if userId is not None:
            where = where + (" and login_user_id = '{}'".format(userId))

        countSql = 'select count(id) from user_login_log where {}'.format(
            where)
        print(countSql)
        if hasPage:
            # page 重0 开始
            limitStart = page * size
            limitEnd = size
            where = where + (" limit {},{}".format(limitStart, limitEnd))

        allSql = 'select id, login_user, login_user_id, date_format(insert_time, "%Y-%m-%d %H:%i:%s") as ' \
                 'insert_time, ip, login_time from user_login_log where {}'.format(where)
        count = 0
        with conn.cursor() as cursor:
            sql = allSql
            try:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute(sql)
                result = cursor.fetchall()
                conn.commit()
                if hasPage:
                    cursor.execute(countSql)
                    count = cursor.fetchall()[0]["count(id)"]
                    conn.commit()
                else:
                    count = None
                infoLog.debug('success, sql: ' + allSql)
            except Exception as e:
                print(allSql)
                infoLog.debug(
                    "FAILED, sql: " + allSql)
                return None
        conn.close()
        return {"data": result, "count": count}

    @classmethod
    def findOneNewLonginByUserId(cls, userId):

        if userId is None or len(userId) < 1:
            return None

        conn = DBPOOL.connection()

        allSql = 'select * from user_login_log where login_user_id = "{}" ORDER BY insert_time desc limit 0, 1 '.format(
            userId)
        with conn.cursor() as cursor:
            sql = allSql
            try:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute(sql)
                result = cursor.fetchall()
                conn.commit()
                infoLog.debug('success, sql: ' + allSql)
            except Exception as e:
                print(allSql)
                infoLog.debug(
                    "FAILED, sql: " + allSql)
                return None
        conn.close()
        if result is None or len(result) < 1:
            return None
        _userLog = Dict2Obj(result[0])
        return userLog(_userLog.id, _userLog.login_user, _userLog.login_user_id, _userLog.insert_time, _userLog.ip,
                       _userLog.login_time)

    @classmethod
    def insert(cls, login_user: str, login_user_id: str, ip: str, login_time: int) -> bool:

        if login_user_id is None or len(login_user_id) < 1 or login_time < 1:
            return False

        conn = DBPOOL.connection()

        allSql = 'insert into user_login_log (`login_user`, `login_user_id`, `insert_time`, `ip`, `login_time`) value' \
                 '("{}", "{}", now(), "{}", {})'.format(login_user, login_user_id, ip, login_time)
        with conn.cursor() as cursor:
            sql = allSql
            try:
                cursor.execute(sql)
                conn.commit()
                infoLog.debug('success, sql: ' + allSql)
            except Exception as e:
                print(allSql)
                infoLog.debug(
                    "FAILED, sql: " + allSql)
                return False
        conn.close()
        return True
