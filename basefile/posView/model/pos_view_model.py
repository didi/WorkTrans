#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: pos_view_model.py
@time: 2020/4/13 11:37
@desc:
'''
import pymysql

from utils.testDBPool import DBPOOL
from utils.myLogger import infoLog


class PosViewModel:

    @classmethod
    def select(cls, cid, didArr, startTime, endTime):
        if cid is None or len(cid) < 1 or didArr is None or len(didArr) < 1 or startTime is None or endTime is None:
            return None

        conn = DBPOOL.connection()
        didWhere = ",".join('"{}"'.format(i) for i in didArr)
        # FIXME 注意这张表 status = 0

        where = 'cid = "{}" and did in ({}) and shike >= "{}" and shike < "{}" and status = 0'.format(cid, didWhere, startTime, endTime)

        allSql = 'select cid, date_format(shike, "%Y-%m-%d %H:%i:%s") as shike, did, trueGMV ,predictGMV ,' \
                 'adjustGMV ,trueOrders ,predictOrders ,adjustOrders,' \
                 ' truePeoples ,predictPeoples ,adjustPeoples from view_pos_info_df ' \
                 'where {}'.format(where)
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

        return [] if result is None else result
