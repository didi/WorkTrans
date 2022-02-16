"""
@author: shenzihan
@contact: shenzihan_i@didichuxing.com
@file: calDB.py
@time: 2019-09-12 12:41
@desc:
"""
import pymysql as MySQLdb

from config.db import conf
from utils.dateUtils import DateUtils
from utils.myLogger import infoLog
from utils.testDBPool import DBPOOL
from datetime import datetime


class CalDB:
    db_config = conf.db['mysql']
    # table = 'task_schedule'
    host = db_config['host']
    port = db_config['port']
    user = db_config['user']
    pwd = db_config['password']
    database = db_config['database']
    connection = None

    @classmethod
    def __del__(cls):
        if cls.connection:
            cls.close()

    @classmethod
    def close(cls):
        try:
            cls.connection.close()
        except Exception:
            pass

    @classmethod
    def get_connection(cls):
        try:
            cls.connection = DBPOOL.connection()
            # cls.connection = MySQLdb.Connection(
            #     host=cls.host,
            #     database=cls.database,
            #     user=cls.user,
            #     password=cls.pwd,
            #     charset='utf8'
            # )
            return cls.connection
        except MySQLdb.DatabaseError:
            return None

    @classmethod
    def delete_cal_record(cls,items):
        '''
        软删除
        :param cid:
        :param bid:
        :return:
        '''
        flag = True
        now = datetime.now()
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = """
                    UPDATE task_schedule SET status=0, update_time=%s WHERE eid=%s and cid=%s and schDay=%s;
                    """
            # sql = """
            #            delete from task_schedule  WHERE cid=%s AND eid=%s and schDay=%s;
            #        """
            try:
                cursor.executemany(sql, items)
                conn.commit()
                # infoLog.debug('success, sql: UPDATE task_schedule SET status=0, update_time=%s WHERE cid=%s AND eid=%s and schDay=%s;', now_datetime, cid, eid, schDay)
            except Exception:
                # infoLog.warning('FAILED, sql: UPDATE task_schedule SET status=0, update_time=%s WHERE cid=%s AND eid=%s and schDay=%s;', now_datetime, cid, eid, schDay)
                conn.rollback()
                flag = False
        conn.close()
        return flag


    # cid, applyId, eid, schDay, allWorkTime, type, outId, startTime, endTime, workTime
    @classmethod
    def update_cal_record(cls,cid:str,applyId:str,eid:str,schDay:str,allWorkTime:str,type:str,outId:str,startTime:str,endTime:str,workTime:str):
        # res = cls.delete_cal_record(cid,applyId)
        # if not res:
        #     infoLog.warning('Update操作时，软删除失败')
        res = cls.insert_cal_record(cid, applyId, eid, schDay, allWorkTime, type, outId, startTime, endTime, workTime)
        return res

    @classmethod
    def insert_cal_record(cls,cid:str,eid:str, schDay:str, allWorkTime:str, type:str, outId:str, startTime:str, endTime:str, workTime:str):
        flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn=cls.get_connection()
        with conn.cursor() as cursor:
            sql = """
                        INSERT INTO task_schedule(cid, applyId, eid, schDay, allWorkTime, `type`, outId, shiftId, startTime, endTime, workTime, agthtype, shiftType, create_time, 
                        update_time, status, scheme_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """
            try:
                cursor.execute(sql, (cid, '99999999999999999999999999', eid, schDay, allWorkTime, type, outId, '', startTime, endTime, workTime, 'lyb', '', now_datetime, now_datetime, 1, 'emp'))
                cursor.execute(sql, (cid, '99999999999999999999999999', eid, schDay, allWorkTime, type, outId, '', startTime, endTime, workTime, 'lyb', '', now_datetime, now_datetime, 1, 'worktime'))
                cursor.execute(sql, (cid, '99999999999999999999999999', eid, schDay, allWorkTime, type, outId, '', startTime, endTime, workTime, 'lyb', '', now_datetime,now_datetime, 1, 'fillRate'))
                cursor.execute(sql, (cid, '99999999999999999999999999', eid, schDay, allWorkTime, type, outId, '', startTime, endTime, workTime, 'lyb', '', now_datetime, now_datetime, 1, 'effect'))
                cursor.execute(sql, (cid, '99999999999999999999999999', eid, schDay, allWorkTime, type, outId, '', startTime, endTime, workTime, 'lyb', '', now_datetime, now_datetime, 1, 'violation'))
                conn.commit()
            except Exception:
                conn.rollback()
                flag= False
        conn.close()
        return flag

    @classmethod
    def insert_cal_record_bach(cls, items:list):
        flag = True
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = """
                            INSERT INTO task_schedule(cid, applyId, eid, schDay, allWorkTime, `type`, outId, shiftId, startTime, endTime, workTime, agthtype, shiftType, create_time, 
                            update_time, status, scheme_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                        """
            try:
                cursor.executemany(sql, items)
                conn.commit()
            except Exception:
                conn.rollback()
                flag = False
        conn.close()
        return flag


