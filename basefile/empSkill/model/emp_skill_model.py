#!/usr/bin/env python
# encoding: utf-8
"""
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: emp_skill_model.py
@time: 2020/3/20 11:47
@desc:
"""
import pymysql

from utils.myLogger import infoLog
from utils.testDBPool import DBPOOL


class EmpSkillModel:

    @classmethod
    def query(cls, cid: str, eid: int, page: int, size: int):
        param = []
        fmt = "%Y-%m-%d %H:%i:%s"
        param.append(fmt)
        param.append(fmt)

        if cid is None or len(cid) < 1:
            return None
        has_page = False
        if (page is not None and page > -1) and (size is not None and size > 0):
            has_page = True
        conn = DBPOOL.connection()

        # where = 'cid = "{}" and status = 1'.format(cid, eid)
        where = 'cid = %s and status = 1'
        param.append(cid)
        if eid is not None:
            # where += ' and eid = {}'.format(eid)
            where += ' and eid = %d'
            param.append(eid)
        count_sql = 'select count(auto_id) from emp_skill where {}'.format(
            where)
        count_par = param

        if has_page:
            # page 重0 开始
            limit_start = page * size
            limit_end = size
            # where = where + (" limit {},{}".format(limit_start, limit_end))
            where = where + " limit %d,%d"
            param.append(limit_start)
            param.append(limit_end)
        all_sql = 'select auto_id, cid, eid, skill, skillNum, opt,' \
                  'date_format(create_time, %s) as create_time, ' \
                  'date_format(update_time, %s) as update_time, status from emp_skill ' \
                  'where {}'.format(where)
        count = None
        with conn.cursor() as cursor:
            sql = all_sql
            try:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute(sql, param)
                result = cursor.fetchall()
                conn.commit()
                if has_page:
                    cursor.execute(count_sql, count_par)
                    count = cursor.fetchall()[0]["count(auto_id)"]
                    conn.commit()
                infoLog.debug('success, sql: ' + all_sql)
            except Exception:
                infoLog.debug("FAILED, sql: " + all_sql)
                return None
        conn.close()
        return {"data": result, "count": count}

    @classmethod
    def select(cls, cid, eid_arr):
        param = []
        if cid is None or len(cid) < 1 or eid_arr is None or len(eid_arr) < 1:
            return None

        fmt = "%Y-%m-%d %H:%i:%s"

        conn = DBPOOL.connection()
        placeholders = ','.join(list(map(lambda x: "'" + str(x) + "'", eid_arr)))  # ",".join(str(i) for i in eid_arr)
        where = 'cid = %s and eid in (' + placeholders + ') and status = 1'
        param.append(fmt)
        param.append(fmt)
        param.append(cid)
        # param.append(placeholders)
        all_sql = 'select auto_id, cid, eid, skill, skillNum, opt, date_format(create_time, %s) as create_time, ' \
                 'date_format(update_time, %s) as update_time, status from emp_skill ' \
                 'where {}'.format(where)

        with conn.cursor() as cursor:
            sql = all_sql
            try:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute(sql, param)
                result = cursor.fetchall()
                conn.commit()
                infoLog.debug('success, sql: ' + all_sql)
            except Exception:
                infoLog.debug(
                    "FAILED, sql: " + all_sql)
                return None
        conn.close()

        return [] if result is None else result
