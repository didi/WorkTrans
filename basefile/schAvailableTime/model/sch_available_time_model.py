#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: sch_available_time_model.py
@time: 2020/3/20 16:10
@desc:
'''
import pymysql

from utils.myLogger import infoLog
from utils.testDBPool import DBPOOL


class SchAvailableTimeModel:

    @classmethod
    def query(cls, cid: str, eid: int, page: str, size: str):
        if cid is None or len(cid) < 1:
            return None
        hasPage = False
        if (page is not None and page > -1) and (size is not None and size > 0):
            hasPage = True
        conn = DBPOOL.connection()
        param=[]
        fmt = "%H:%i:%s"
        param.append(fmt)
        param.append(fmt)
        param.append("%Y-%m-%d")
        fmt = "%Y-%m-%d %H:%i:%s"
        param.append(fmt)
        param.append(fmt)

        #where = 'cid = "{}" and status = 1'.format(cid, eid)
        where = 'cid = %s and status = 1'
        param.append(cid)
        if eid is not None:
            #where += ' and eid = {}'.format(eid)
            where += ' and eid = %d'
            param.append(eid)


        countSql = 'select count(auto_id) from sch_available_time where {}'.format(
            where)
        count_par=param[5:]
        if hasPage:
            # page 重0 开始
            limitStart = page * size
            limitEnd = size
            #where = where + (" limit {},{}".format(limitStart, limitEnd))
            where = where + " limit %d,%d"
            param.append(limitStart)
            param.append(limitEnd)

        allSql = 'select auto_id, cid, eid, opt, type, date_format(start, %s) as  start,' \
                 ' date_format(end, %s) as end, date_format(day, %s) as day,' \
                 'date_format(create_time, %s) as create_time, ' \
                 'date_format(update_time, %s) as update_time, status from sch_available_time ' \
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
    def select(cls, cid, eidArr, dayArr):
        if cid is None or len(cid) < 1 or eidArr is None or len(eidArr) < 1:
            return None

        conn = DBPOOL.connection()
        placeholders = ",".join(str(i) for i in eidArr)
        dayStr = None
        if dayArr is not None:
            _dayStr = ','.join('"{}"'.format(i) for i in dayArr)
            dayStr = "and day in ({})".format(_dayStr)

        where = 'cid = "{}" and eid in ({}) {} and status = 1'.format(cid, placeholders, "" if dayStr is None else dayStr)

        allSql = 'select auto_id, cid, eid, opt, type, date_format(start, "%H:%i:%s") as  start,' \
                 ' date_format(end, "%H:%i:%s") as end, date_format(day, "%Y-%m-%d") as day,' \
                 'date_format(create_time, "%Y-%m-%d %H:%i:%s") as create_time, ' \
                 'date_format(update_time, "%Y-%m-%d %H:%i:%s") as update_time, status from sch_available_time ' \
                 'where '+where

        print(where)
        print(allSql)
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

