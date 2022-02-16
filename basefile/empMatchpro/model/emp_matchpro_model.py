#!/usr/bin/env python
# encoding: utf-8
"""
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: emp_matchpro_model.py
@time: 2020/3/19 11:20
@desc:
"""
import pymysql

from utils.myLogger import infoLog
from utils.testDBPool import DBPOOL


class EmpMatchproModel:

    @classmethod
    def query(cls, cid: str, did: int, page: int, size: int):
        if cid is None or len(cid) < 1 or did is None:
            return None
        has_page = False
        if (page is not None and page > -1) and (size is not None and size > 0):
            has_page = True
        conn = DBPOOL.connection()
        param = []
        fmt = "%Y-%m-%d %H:%i:%s"
        param.append(fmt)
        param.append(fmt)
        # where = 'cid = "{}" and did = "{}" and status = 1'.format(cid, did)
        where = 'cid = %s and did = %d and status = 1'
        param.append(cid)
        param.append(did)
        count_sql = 'select count(auto_id) from emp_matchpro where {}'.format(where)
        count_par = param[2:]
        if has_page:
            # page 重0 开始
            limit_start = page * size
            limit_end = size
            # where = where + (" limit {},{}".format(limit_start, limit_end))
            where = where + " limit %d,%d"
            param.append(limit_start)
            param.append(limit_end)

        all_sql = 'select auto_id, cid, bid, did, opt, weight, ruleGroup, ruleDesc, ruleCpType, ruletag, ruleCpNum,' \
                  'date_format(create_time, %s) as create_time, ' \
                  'date_format(update_time, %s) as update_time, status from emp_matchpro where {}'.format(where)
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
                infoLog.debug(
                    "FAILED, sql: " + all_sql)
                return None
        conn.close()
        return {"data": result, "count": count}
