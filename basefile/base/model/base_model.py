#!/usr/bin/env python
# encoding: utf-8
"""
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: base_model.py
@time: 2020/3/12 16:36
@desc:
"""
import pymysql

from utils.myLogger import infoLog
from utils.testDBPool import DBPOOL


class BaseModel:

    @classmethod
    def getCid(cls, table: str):
        if table is None or len(table) < 1:
            return []
        conn = DBPOOL.connection()
        param = []
        # allSql = 'SELECT DISTINCT cid FROM {}'.format(table)
        allSql = 'SELECT DISTINCT cid FROM %s'
        param.append(table)
        result = []

        with conn.cursor() as cursor:
            sql = allSql
            try:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute(sql, param)
                result = cursor.fetchall()
                conn.commit()
                infoLog.debug('success, sql: ' + allSql)
            except Exception as e:
                infoLog.warning(
                    "FAILED, sql: " + allSql)
                conn.rollback()
        conn.close()
        return result

    @classmethod
    def getDids(cls, cid: str, table: str):
        # 容错
        if cid is None or len(cid) < 1 or table is None or len(table) < 1:
            return []
        param = []
        conn = DBPOOL.connection()
        # allSql = 'SELECT DISTINCT did FROM {} where cid = {}'.format(table, cid)
        allSql = 'SELECT DISTINCT did FROM %s where cid = %s'
        param.append(table)
        param.append(cid)

        result = []

        with conn.cursor() as cursor:
            sql = allSql
            try:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute(sql, param)
                result = cursor.fetchall()
                conn.commit()
                infoLog.debug('success, sql: ' + allSql)
            except Exception as e:
                infoLog.warning(
                    "FAILED, sql: " + allSql)
                conn.rollback()
        conn.close()
        return result

    @classmethod
    def getEids(cls, cid: str, table: str):
        # 容错
        if cid is None or len(cid) < 1 or table is None or len(table) < 1:
            return []

        conn = DBPOOL.connection()
        param = []
        # allSql = 'SELECT DISTINCT eid FROM {} where cid = {}'.format(table, cid)
        allSql = 'SELECT DISTINCT eid FROM %s where cid = %s'
        param.append(table)
        param.append(cid)
        result = []

        with conn.cursor() as cursor:
            sql = allSql
            try:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute(sql, param)
                result = cursor.fetchall()
                conn.commit()
                infoLog.debug('success, sql: ' + allSql)
            except Exception as e:
                infoLog.warning(
                    "FAILED, sql: " + allSql)
                conn.rollback()
        conn.close()
        return result
