#!/usr/bin/env python
# encoding: utf-8
"""
@author: pengyd
@file: schedule_view_model.py
@time: 2020/3/25 13:43
@desc:
"""

import pymysql

from utils.myLogger import infoLog
from utils.testDBPool import DBPOOL


class ScheduleViewModel:

    @classmethod
    def query(cls, cid: str, did: int, date: str, apply_id: str, scheme_type: str, page: str, size: str):
        has_page = False
        if (page is not None and page > -1) and (size is not None and size > 0):
            has_page = True
        conn = DBPOOL.connection()
        param=[]
        fmt="%H:%i:%s"
        param.append(fmt)
        param.append(fmt)
        #where = ' cid = "{}" and did = "{}" and status = 1 '.format(cid, did)
        where = ' cid = %s and did = %d and status = 1 '
        param.append(cid)
        param.append(did)
        if date is not None:
            #where = where + ' and schDay = "{}" '.format(date)
            where = where + ' and schDay = %s '
            param.append(date)

        if apply_id is not None:
            #where = where + ' and applyId = "{}" '.format(apply_id)
            where = where + ' and applyId = %s '
            param.append(apply_id)

        if scheme_type is not None:
            #where = where + ' and scheme_type = "{}" '.format(scheme_type)
            where = where + ' and scheme_type = %s '
            param.append(scheme_type)

        count_sql = 'select count(autoid) from task_schedule where {} '.format(where)
        count_par=param[2:]
        if has_page:
            # page 重0 开始
            limit_start = page * size
            limit_end = size
            #where = where + (" limit {},{}".format(limit_start, limit_end))
            where = where + " limit %d,%d"
            param.append(limit_start)
            param.append(limit_end)
        all_sql = '''
            select autoid,cid,applyId,eid,schDay,allWorkTime,scheme_type,did,
            outId as task_id,date_format(startTime, %s) as startTime,
            date_format(endTime, %s) as endTime,workTime from task_schedule where {}
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
                    cursor.execute(count_sql,count_par)
                    count = cursor.fetchall()[0]["count(autoid)"]
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
    def getApplyId(cls, cid, did):
        conn = DBPOOL.connection()
        where = " cid = {} and did = {} and status = 1".format(cid, did)


        allSql = 'SELECT DISTINCT applyId FROM task_schedule where {}'.format(where)

        result = []

        with conn.cursor() as cursor:
            sql = allSql
            try:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute(sql)
                result = cursor.fetchall()
                conn.commit()
                infoLog.debug('success, sql: ' + allSql)
            except Exception as e:
                infoLog.warning(
                    "FAILED, sql: " + allSql)
                conn.rollback()
        conn.close()
        return result
