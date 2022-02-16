#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: labor_task.py
@time: 2020/3/13 13:43
@desc:
'''
from typing import List

import pymysql

from utils.myLogger import infoLog
from utils.testDBPool import DBPOOL


class LaborTaskModel:

    @classmethod
    def query(cls, cid: str, did: int, page: str, size: str):
        if cid is None or len(cid) < 1 or did is None:
            return None
        hasPage = False
        if (page is not None and page > -1) and (size is not None and size > 0):
            hasPage = True
        conn = DBPOOL.connection()
        param=[]
        fmt="%H:%i:%s"
        param.append(fmt)
        param.append(fmt)
        fmt="%Y-%m-%d %H:%i:%s"
        param.append(fmt)
        param.append(fmt)
        #where = 'cid = "{}" and did = "{}" and status = 1'.format(cid, did)
        where = 'cid = %s and did = %d and status = 1'
        param.append(cid)
        param.append(did)

        countSql = 'select count(auto_id) from labor_task where {}'.format(
            where)
        count_par=param[4:]
        if hasPage:
            # page 重0 开始
            limitStart = page * size
            limitEnd = size
            #where = where + (" limit {},{}".format(limitStart, limitEnd))
            where = where + " limit %d,%d"
            param.append(limitStart)
            param.append(limitEnd)

        allSql = 'select auto_id ,bid , cid ,did , taskName, abCode, taskType, opt, worktimeType, ' \
                 'date_format(worktimeStart, %s) as worktimeStart, ' \
                 'date_format(worktimeEnd, %s) as worktimeEnd, taskSkillBid, skillNum, cert,fillCoefficient,' \
                 'date_format(create_time, %s) as create_time, ' \
                 'date_format(update_time, %s) as update_time, status from labor_task ' \
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
    def listForBids(cls, cid: str, bids: List):

        if cid is None or len(cid) < 1 or bids is None or len(bids) < 1:
            return None

        conn = DBPOOL.connection()

        where = 'cid = "{}" and bid in {} and status = 1'.format(cid, tuple(bids))

        allSql = 'select auto_id ,bid , cid ,did , taskName, abCode, taskType, opt, worktimeType, worktimeStart, ' \
                 'worktimeEnd, taskSkillBid, skillNum, cert,fillCoefficient,' \
                 'date_format(create_time, "%Y-%m-%d %H:%i:%s") as create_time, ' \
                 'date_format(update_time, "%Y-%m-%d %H:%i:%s") as update_time, status from labor_task ' \
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
        return result

    @classmethod
    def select(cls, cid, did, bidArr):
        if cid is None or did is None:
            return None

        conn = DBPOOL.connection()

        where = 'cid = "{}" and did = {}  and status = 1'.format(cid, did)

        if bidArr is not None and len(bidArr) > 0:
            placeholders = ",".join('"{}"'.format(i) for i in bidArr)
            where += ' and bid in ({})'.format(placeholders)

        allSql = 'select auto_id ,bid , cid ,did , taskName, abCode, taskType, opt,' \
                 'taskMinWorkTime, taskMaxWorkTime, discard, ' \
                 ' worktimeType, date_format(worktimeStart, "%H:%i") as worktimeStart, ' \
                 ' date_format(worktimeEnd, "%H:%i") as worktimeEnd, taskSkillBid, skillNum, cert, fillCoefficient,' \
                 'date_format(create_time, "%Y-%m-%d %H:%i:%s") as create_time, ' \
                 'date_format(update_time, "%Y-%m-%d %H:%i:%s") as update_time, status from labor_task ' \
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