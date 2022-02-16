#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: sch_compliance_model.py
@time: 2020/3/19 10:46
@desc:
'''
import pymysql

from utils.myLogger import infoLog
from utils.testDBPool import DBPOOL


class SchComplianceModel:

    @classmethod
    def query(cls, cid: str, did: int, page: str, size: str):
        if cid is None or len(cid) < 1 or did is None:
            return None
        hasPage = False
        if (page is not None and page > -1) and (size is not None and size > 0):
            hasPage = True
        conn = DBPOOL.connection()
        param=[]
        param.append("%Y-%m-%d")
        fmt="%Y-%m-%d %H:%i:%s"
        param.append(fmt)
        param.append(fmt)
        #where = 'cid = "{}" and did = "{}" and status = 1'.format(cid, did)
        where = 'cid = %s and did = %d and status = 1'
        param.append(cid)
        param.append(did)

        countSql = 'select count(auto_id) from sch_compliance where {}'.format(
            where)
        count_par=param[3:]
        if hasPage:
            # page 重0 开始
            limitStart = page * size
            limitEnd = size
            #where = where + (" limit {},{}".format(limitStart, limitEnd))
            where = where + " limit %d,%d"
            param.append(limitStart)
            param.append(limitEnd)

        allSql = 'select auto_id ,cid, bid, opt, ptype, eid, did, ruleType, ruleCpType, ruletag, ruleCpNum, ' \
                 'dayFusion, cycle, shiftId, cret, timeRange, date_format(startDate, %s) as startDate, ' \
                 'caution,' \
                 'date_format(create_time, %s) as create_time, ' \
                 'date_format(update_time, %s) as update_time, status from sch_compliance ' \
                 'where {}'.format(
            where)
        count = None
        with conn.cursor() as cursor:
            sql = allSql
            try:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute(sql,param)
                result = cursor.fetchall()
                conn.commit()
                if hasPage:
                    cursor.execute(countSql,count_par)
                    count = cursor.fetchall()[0]["count(auto_id)"]
                    conn.commit()
                infoLog.debug('success, sql: ' + allSql)
            except Exception as e:
                print(allSql)
                infoLog.debug(
                    "FAILED, sql: " + allSql)
                return None
        conn.close()
        return {"data": result, "count": count}

    @classmethod
    def select(cls, cid, bidArr):
        if cid is None or len(cid) < 1:
            return None

        conn = DBPOOL.connection()
        bidWhere = None
        if bidArr is not None and len(bidArr) > 0:
            bidWhere = 'and bid in {}'.format("({})".format(bidArr[0]) if len(bidArr) == 1 else tuple(bidArr))
        where = 'cid = "{}" {} and status = 1'.format(cid, "" if bidWhere is None else bidWhere)

        allSql = 'select auto_id ,cid, bid, opt, ptype, eid, did, ruleType, ruleCpType, ruletag, ruleCpNum, ' \
                 'dayFusion, cycle, shiftId, cret, timeRange, date_format(startDate, "%Y-%m-%d") as startDate, ' \
                 'caution,' \
                 'date_format(create_time, "%Y-%m-%d %H:%i:%s") as create_time, ' \
                 'date_format(update_time, "%Y-%m-%d %H:%i:%s") as update_time, status from sch_compliance ' \
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

