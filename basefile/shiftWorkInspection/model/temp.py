#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: temp.py
@time: 2020/3/26 14:33
@desc:
'''
import pymysql

from utils.myLogger import infoLog
from utils.testDBPool import DBPOOL


class ScheduleTemp:

    @classmethod
    def query(cls, cid: str, did: int, date: str):

        conn = DBPOOL.connection()

        all_sql = 'select autoid, cid, applyId, eid, schDay, allWorkTime, type, outId, shiftId, startTime, ' \
                  'endTime, workTime, agthtype, shiftType, create_time, update_time, status, scheme_type,' \
                  ' did from task_schedule'
        count = None
        with conn.cursor() as cursor:
            sql = all_sql
            try:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute(sql)
                result = cursor.fetchall()
                conn.commit()

                infoLog.debug('success, sql: ' + all_sql)
            except Exception as e:
                print(all_sql)
                infoLog.debug(
                    "FAILED, sql: " + all_sql)
                return None
        conn.close()
        return result