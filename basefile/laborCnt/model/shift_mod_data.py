#!/usr/bin/env python
# encoding: utf-8

"""
@author: sunsong
@contact: sunsong@didiglobal.com
@file: shift_mod_data.py
@time: 2019/9/9 5:18 下午
@desc:
"""

from utils.testDBPool import DBPOOL
import pymysql

from config.db import conf
from utils.dateUtils import DateUtils
from utils.myLogger import infoLog


class ShiftModData:

    db_config = conf.db['mysql']
    table = 'shift_mod_Data'
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
            return cls.connection
        except pymysql.DatabaseError:
            return None

    @classmethod
    def insert_record(cls, cid: str, bid: str, did: str, shiftbid: str, shift_start: str, shift_end: str,
                      is_cross_day: bool) -> bool:
        """
        插入记录
        :param cid:
        :param bid:
        :param did:
        :param shiftbid:
        :param shift_start:
        :param shift_end:
        :param is_cross_day:
        :return:
        """
        if is_cross_day:
            flag = '1'
        else:
            flag = '0'
        res_flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO shift_mod_data (cid, bid, did, shiftbid, shift_start, shift_end, is_cross_day, create_time, 
            update_time, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            try:
                cursor.execute(sql, (cid, bid, did, shiftbid, shift_start, shift_end, flag, now_datetime,
                                     now_datetime, '1'))
                conn.commit()
                infoLog.debug('success, sql: INSERT INTO shift_mod_data (cid, bid, did, shiftbid, shift_start, '
                              'shift_end, is_cross_day, create_time, update_time, status) VALUES (%s, %s, %s, %s, %s, '
                              '%s, %s, %s, %s, %s);', cid, bid, did, shiftbid, shift_start, shift_end, flag,
                              now_datetime, now_datetime, '1')
            except Exception:
                infoLog.warning('FAILED, sql: INSERT INTO shift_mod_data (cid, bid, did, shiftbid, shift_start, '
                                'shift_end, is_cross_day, create_time, update_time, status) VALUES (%s, %s, %s, %s, '
                                '%s, %s, %s, %s, %s, %s);', cid, bid, did, shiftbid, shift_start, shift_end, flag,
                                now_datetime, now_datetime, '1')
                conn.rollback()
                res_flag = False
        conn.close()
        return res_flag

    @classmethod
    def soft_delete_record_level_first(cls, bid: str, cid: str, did: str) -> bool:
        """
        软删除 等级1
        :param bid:
        :param cid:
        :param did:
        :return:
        """
        flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = """
            UPDATE shift_mod_data SET status=0, update_time=%s WHERE bid=%s AND cid=%s AND did=%s;
            """
            try:
                cursor.execute(sql, (now_datetime, bid, cid, did))
                conn.commit()
                infoLog.debug('success, sql: UPDATE shift_mod_data SET status=0, update_time=%s WHERE bid=%s AND '
                              'cid=%s AND did=%s;', now_datetime, bid, cid, did)
            except Exception:
                infoLog.warning('FAILED, sql: UPDATE shift_mod_data SET status=0, update_time=%s WHERE bid=%s AND '
                                'cid=%s AND did=%s;', now_datetime, bid, cid, did)
                conn.rollback()
                flag = False
        conn.close()
        return flag

    @classmethod
    def soft_delete_record_level_second(cls, bid: str, cid: str, did: str, shiftbid: str) -> bool:
        """
        软删除 等级2
        :param bid:
        :param cid:
        :param did:
        :param shiftbid:
        :param shift_start:
        :param shift_end:
        :return:
        """
        flag = True
        conn = cls.get_connection()
        now_datetime = DateUtils.get_now_datetime_str()
        with conn.cursor() as cursor:
            sql = """
                    UPDATE shift_mod_data SET status=0, update_time=%s WHERE bid=%s AND cid=%s AND did=%s AND 
                    shiftbid=%s;
                    """
            try:
                cursor.execute(sql, (now_datetime, bid, cid, did, shiftbid))
                conn.commit()
                infoLog.debug('success, sql: UPDATE shift_mod_data SET status=0, update_time=%s WHERE bid=%s AND '
                              'cid=%s AND did=%s AND shiftbid=%s;', now_datetime, bid, cid, did, shiftbid)
            except Exception:
                infoLog.warning('FAILED, sql: UPDATE shift_mod_data SET status=0, update_time=%s WHERE bid=%s AND '
                                'cid=%s AND did=%s AND shiftbid=%s;', now_datetime, bid, cid, did, shiftbid)
                conn.rollback()
                flag = False
        conn.close()
        return flag

    @classmethod
    def update_record(cls, bid: str, cid: str, did: str, shiftbid: str, shift_start: str, shift_end: str,
                      is_cross_day: bool) -> bool:
        """
        更新记录
        :param bid:
        :param cid:
        :param did:
        :param shiftbid:
        :param shift_start:
        :param shift_end:
        :param is_cross_day:
        :return:
        """
        res = cls.soft_delete_record_level_second(bid, cid, did, shiftbid)
        if not res:
            infoLog.warning('Update操作时，软删除失败，将直接插入新记录。')
        res = cls.insert_record(cid, bid, did, shiftbid, shift_start, shift_end, is_cross_day)
        return res
