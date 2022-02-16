#!/usr/bin/env python
# encoding: utf-8
"""
@author: pengyd
@file: task_view_model.py
@time: 2020/3/13 13:43
@desc:
"""
from typing import List

import pymysql

from utils.myLogger import infoLog
from utils.testDBPool import DBPOOL


class TaskViewModel:

    @classmethod
    def query(cls, cid: str, did: int, date: str, t_type: str, page: str, size: str):
        has_page = False
        if (page is not None and page > -1) and (size is not None and size > 0):
            has_page = True
        conn = DBPOOL.connection()
        param = []
        #where = ' cid = "{}" and did = "{}" and forecast_date = "{}" and type = "{}" and status = 1 '\
        #    .format(cid, did, date, t_type)
        where = ' cid = %s and did = %d and forecast_date = %s and type = %s and status = 1 '
        param.append(cid)
        param.append(did)
        param.append(date)
        param.append(t_type)
        count_sql = 'select count(auto_id) from task_matrix_ss where {}'.format(
            where)
        if has_page:
            # page 重0 开始
            limit_start = page * size
            limit_end = size
            #where = where + (" limit {},{}".format(limit_start, limit_end))
            where = where + " limit %d,%d"
            param.append(limit_start)
            param.append(limit_end)

        all_sql = '''
            SELECT t.auto_id, t.cid, t.did, t.forecast_date, 
            t.start_time, t.end_time, t.task_matrix, t.STATUS FROM task_matrix_ss t where {}
            '''.format(where)
        count = None
        with conn.cursor() as cursor:
            sql = all_sql
            try:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute(sql,param)
                result = cursor.fetchall()
                conn.commit()
                if has_page:
                    cursor.execute(count_sql,param)
                    count = cursor.fetchall()[0]["count(auto_id)"]
                    conn.commit()
                infoLog.debug('success, sql: ' + all_sql)
            except Exception as e:
                print(all_sql)
                infoLog.debug(
                    "FAILED, sql: " + all_sql)
                return None
        conn.close()
        return {"data": result, "count": count}

    @classmethod
    def slelect(cls, cid, didArr, forecastType, startDate, endDate):
        if cid is None or len(cid) < 1 or didArr is None or len(didArr) < 1 \
                or startDate is None or endDate is None or forecastType is None:
            return None

        conn = DBPOOL.connection()
        didWhere =','.join(list(map(lambda x: "'" + str(x) + "'", didArr)))  # ",".join('"{}"'.format(i) for i in didArr)
        param=[]
        # where = 'cid = "{}" and did in ({}) and forecast_date >= "{}" and forecast_date <= "{}" ' \
        #         'and status = 1 and forecastType = {} and type = "full"'.format(cid, didWhere, startDate, endDate, forecastType)
        where = 'cid = %s and did in ('+didWhere+') and forecast_date >= %s and forecast_date <= %s ' \
                'and status = 1 and forecastType = %s and type = "full"'#.format(cid, didWhere, startDate, endDate, forecastType)
        param.append(cid)
        param.append(startDate)
        param.append(endDate)
        param.append(forecastType)
        allSql = 'select auto_id, cid, did, forecast_date, start_time, end_time, task_matrix, status ' \
                 'FROM task_matrix_ss t where {}'.format(where)


        print(allSql,param)
        with conn.cursor() as cursor:
            sql = allSql
            try:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute(sql,param)
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
