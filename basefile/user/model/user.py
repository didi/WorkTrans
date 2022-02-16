#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: user.py
@time: 2020/3/9 17:04
@desc:
'''

from utils.dictToObj import Dict2Obj
from utils.testDBPool import DBPOOL
from utils.myLogger import infoLog
import pymysql


class user:

    def __init__(self, id, username, password, name, userId, isAdmin, groName, status):
        self.id = id
        self.username = username
        self.password = password
        self.name = name
        self.userId = userId
        self.isAdmin = isAdmin
        self.groName = groName
        self.status = status

class UserMode:



    @classmethod
    def query(cls, username: str):
        if username is None or len(username) < 1:
            return None

        conn = DBPOOL.connection()

        allSql = 'select * from user where username = "{}" and status = 1'.format(username)
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
        _user = Dict2Obj(result[0])
        return  user(_user.id, _user.username, _user.password, _user.name, _user.user_id, _user.is_admin, _user.gro_name, _user.status)

    @classmethod
    def queryUserId(cls, user_id):
        if user_id is None or len(user_id) < 1:
            return None

        conn = DBPOOL.connection()

        allSql = 'select * from user where user_id = "{}" and status = 1'.format(user_id)
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
        _user = Dict2Obj(result[0])
        return  user(_user.id, _user.username, _user.password, _user.name, _user.user_id, _user.is_admin, _user.gro_name, _user.status)

    @classmethod
    def insert(cls, username: str, password: str, name: str, user_id: str, is_admin: str, gro_name: str) -> bool:

        if username is None or password is None or gro_name is None:
            return False

        conn = DBPOOL.connection()

        allSql = 'insert into user (`insert_time`, `update_time`, `username`, `password`, `name`, `user_id`, ' \
                 '`is_admin`, `gro_name`, `status`) value(now(), now(), "{}", "{}", "{}", "{}", "{}", "{}", 1)' \
            .format(username, password, name, user_id, is_admin, gro_name)
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