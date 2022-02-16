#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: labor_cacl_value.py
@time: 2020/3/16 10:17
@desc:
'''
import pymysql

from utils.dateUtils import DateUtils
from utils.myLogger import infoLog
from utils.testDBPool import DBPOOL


class LaborCaclValueModel:

    @classmethod
    def query(cls, cid: str, did: int, laborStandardBid: str, day: str, taskBid: str, time: str, page: str, size: str):

        if cid is None or len(cid) < 1 or did is None :
            return None
        hasPage = False
        if (page is not None and page > -1) and (size is not None and size > 0):
            hasPage = True
        conn = DBPOOL.connection()
        param=[]
        fmt="%Y-%m-%d %H:%i:%s"
        param.append(fmt)
        param.append(fmt)
        #where = 'cid = "{}" and did = {}  and status = 1'.format(cid, did, laborStandardBid)
        where = 'cid = %s and did = %d  and status = 1'
        param.append(cid)
        param.append(did)
        if laborStandardBid is not None and len(laborStandardBid) > 0:
            #where = where + ' and laborStandardBid = "{}"'.format(laborStandardBid)
            where = where + ' and laborStandardBid = %s'
            param.append(laborStandardBid)
        if day is not None and len(day) > 0:
            #where = where + ' and dayStr = "{}"'.format(day)
            where = where + ' and dayStr = %s'
            param.append(day)
        if taskBid is not None and len(taskBid) > 0:
            #where = where + ' and taskBid = "{}"'.format(taskBid)
            where = where + ' and taskBid = %s'
            param.append(taskBid)
        if time is not None and len(time) > 0:
            # 所在得小时 都要查寻出来
            hourorMin = DateUtils.get_new_time_60_minute(time + ":00")
            if hourorMin is not None:
                _hour = hourorMin[0]
                hour = DateUtils.trfHourAndMin(_hour)
                startTime = hour + ":00"
                endTime = hour + ":59"
                #where = where + ' and startTimeStr >= "{}" and startTimeStr < "{}"'.format(startTime, endTime)
                where = where + ' and startTimeStr >= %s and startTimeStr < %s'
                param.append(startTime)
                param.append(endTime)

            else:
                return None

        countSql = 'select count(auto_id) from labor_cacl_value where {}'.format(
            where)
        count_par=param[2:]
        if hasPage:
            # page 重0 开始
            limitStart = page * size
            limitEnd = size
            #where = where + (" limit {},{}".format(limitStart, limitEnd))
            where = where + " limit %d,%d"
            param.append(limitStart)
            param.append(limitEnd)
        allSql = 'select auto_id  , cid ,did ,forecastType, forecastStandard, dayStr, startTimeStr, endTimeStr, ' \
                 'taskBid, laborStandardBid, caclValue, forecastValue, editValue, min_caclValue, max_caclValue, ' \
                 'date_format(inserttime, %s) as inserttime, ' \
                 'date_format(updatetime, %s) as updatetime, status from labor_cacl_value ' \
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
    def getlaborStandardBid(cls, cid: str, did: int):

        if cid is None or len(cid) < 1 or did is None:
            return None

        conn = DBPOOL.connection()
        allSql = 'SELECT DISTINCT laborStandardBid FROM labor_cacl_value where cid = "{}" and did = {} and' \
                 ' status = 1'.format(cid, did)

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

    @classmethod
    def getTaskBid(cls, cid: str, did: int, laborStandardBid: str):

        if cid is None or len(cid) < 1 or did is None:
            return None
        conn = DBPOOL.connection()
        allSql = 'SELECT DISTINCT taskBid FROM labor_cacl_value where cid = "{}" and did = {} and ' \
                 ' status = 1'.format(cid, did, laborStandardBid)

        if laborStandardBid is not None:
            allSql = allSql + ' and laborStandardBid = "{}"'.format(laborStandardBid)

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

    @classmethod
    def select(cls, cid, didArr, taskBidArr, dayArr):
        if cid is None or len(cid) < 1 or didArr is None or len(didArr) < 1:
           return None

        conn = DBPOOL.connection()
        didWhere = ",".join('"{}"'.format(i) for i in didArr)

        where = 'cid = "{}" and did in ({}) and status = 1'.format(cid, didWhere)

        if taskBidArr is not None and len(taskBidArr) > 0:
            temptaskWhere = ",".join('"{}"'.format(i) for i in taskBidArr)
            where += ' and taskBid in ({})'.format(temptaskWhere)

        if dayArr is not None and len(dayArr) > 0:
            tempDayArrWhere = ",".json('"{}"'.format(i) for i in dayArr)
            where += ' and dayStr in ({})'.format(tempDayArrWhere)

        allSql = 'select auto_id  , cid ,did ,forecastType, forecastStandard, dayStr, startTimeStr, endTimeStr, ' \
                 'taskBid, laborStandardBid, caclValue, forecastValue, editValue, min_caclValue, max_caclValue, ' \
                 'date_format(inserttime, "%Y-%m-%d %H:%i:%s") as inserttime, ' \
                 'date_format(updatetime, "%Y-%m-%d %H:%i:%s") as updatetime, status from labor_cacl_value ' \
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
