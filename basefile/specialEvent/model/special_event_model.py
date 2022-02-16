#!/usr/bin/env python
# encoding: utf-8

"""
@author: pyd
@contact:
@file: special_event_model.py
@time: 2020/2/25
@desc:
"""

from utils.testDBPool import DBPOOL
from utils.dateUtils import DateUtils
from utils.myLogger import infoLog


class SpecialEventModel:

    @classmethod
    def insert_record(cls, bid: str, cid: str, did: str, event_start: str, event_end: str,
                      event_name: str) -> bool:
        """
        插入记录
        :param bid:
        :param cid:
        :param did:
        :param event_start:
        :param event_end:
        :param event_name:
        :return:
        """
        res_flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn = DBPOOL.connection()
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO special_event_data (bid, cid, did, event_name, event_start, event_end,
             create_time, update_time, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            try:
                cursor.execute(sql, (bid, cid, did, event_name, event_start, event_end,
                                     now_datetime, now_datetime, 1))
                conn.commit()
                infoLog.debug('success, sql: INSERT INTO special_event_data (bid, cid, did, '
                              'event_name, event_start, event_end, '
                              'create_time, update_time, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);',
                              bid, cid, did, event_name, event_start, event_end,
                              now_datetime, now_datetime, 1)
            except Exception:
                infoLog.warning('FAILED, sql: INSERT INTO special_event_data (bid, cid, did, '
                                'event_name, event_start, event_end, '
                                'create_time, update_time, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);',
                                bid, cid, did, event_name, event_start, event_end,
                                now_datetime, now_datetime, 1)
                conn.rollback()
                res_flag = False
        conn.close()
        return res_flag

    @classmethod
    def soft_delete(cls, bid: str, cid: str, did: str) -> bool:
        """
        删除
        :param bid:
        :param cid:
        :param did:
        :return:
        """
        flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn = DBPOOL.connection()
        with conn.cursor() as cursor:
            sql = """
            UPDATE special_event_data SET status=0, update_time=%s WHERE bid=%s AND cid=%s AND did=%s;
            """
            try:
                cursor.execute(sql, (now_datetime, bid, cid, did))
                conn.commit()
                infoLog.debug('success, sql: UPDATE special_event_data SET status=0, update_time=%s WHERE bid=%s AND '
                              'cid=%s AND did=%s;', now_datetime, bid, cid, did)
            except Exception:
                infoLog.warning('FAILED, sql: UPDATE special_event_data SET status=0, update_time=%s WHERE bid=%s AND '
                                'cid=%s AND did=%s;', now_datetime, bid, cid, did)
                conn.rollback()
                flag = False
        conn.close()
        return flag

    @classmethod
    def update_record(cls, bid: str, cid: str, did: str, event_start: str, event_end: str, event_name: str) -> bool:
        """
        更新记录
        :param bid:
        :param cid:
        :param did:
        :param event_start:
        :param event_end:
        :param event_name:
        :return:
        """
        flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn = DBPOOL.connection()
        with conn.cursor() as cursor:
            sql = """
            UPDATE special_event_data SET status=1, update_time=%s, event_name=%s, event_start=%s, event_end=%s 
            WHERE bid=%s AND cid=%s AND did=%s;
            """
            try:
                cursor.execute(sql, (now_datetime, event_name, event_start, event_end, bid, cid, did))
                conn.commit()
                infoLog.debug('success, sql: UPDATE special_event_data SET status=1, update_time=%s, event_name=%s, '
                              'event_start=%s, event_end=%s WHERE bid=%s AND cid=%s AND did=%s;',
                              now_datetime, event_name, event_start, event_end, bid, cid, did)
            except Exception:
                infoLog.warning('FAILED, sql: UPDATE special_event_data SET status=1, update_time=%s, event_name=%s, '
                                'event_start=%s, event_end=%s WHERE bid=%s AND cid=%s AND did=%s;',
                                now_datetime, event_name, event_start, event_end, bid, cid, did)
                conn.rollback()
                flag = False
        conn.close()
        return flag
