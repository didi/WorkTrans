#!/usr/bin/env python
# encoding: utf-8

"""
@author: pyd
@contact:
@file: special_event_scope_model.py
@time: 2020/2/25
@desc:
"""

import ast
from utils.testDBPool import DBPOOL
from utils.dateUtils import DateUtils
from utils.myLogger import infoLog


class SpecialEventScopeModel:

    @classmethod
    def insert_record(cls, bid: str, cid: str, event_bid: str, goods_bids: str, did_arr: str,
                      start_time: str, end_time: str) -> bool:
        """
        插入记录
        :param bid:
        :param cid:
        :param event_bid:
        :param goods_bids:
        :param did_arr:
        :param start_time:
        :param end_time:
        :return:
        """
        res_flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn = DBPOOL.connection()
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO special_event_scope_data (bid, cid, event_bid, goods_arr, did_arr, start_time, end_time,
             create_time, update_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            try:
                cursor.execute(sql, (bid, cid, event_bid, str(goods_bids), str(did_arr), start_time, end_time,
                                     now_datetime, now_datetime))
                conn.commit()
                infoLog.debug('success, sql: INSERT INTO special_event_scope_data (bid, cid, event_bid, goods_arr, '
                              'did_arr, start_time, end_time, create_time, update_time) '
                              'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);',
                              bid, cid, event_bid, str(goods_bids), str(did_arr), start_time, end_time,
                              now_datetime, now_datetime)
            except Exception:
                infoLog.warning('FAILED, sql: INSERT INTO special_event_scope_data (bid, cid, event_bid, goods_arr, '
                                'did_arr, start_time, end_time, create_time, update_time) '
                                'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);',
                                bid, cid, event_bid, str(goods_bids), str(did_arr), start_time, end_time,
                                now_datetime, now_datetime)
                conn.rollback()
                res_flag = False
        conn.close()
        return res_flag

    @classmethod
    def update_record(cls, bid: str, cid: str, event_bid: str, goods_bids: str, did_arr: str,
                      start_time: str, end_time: str) -> bool:
        """
        更新记录
        :param bid:
        :param cid:
        :param event_bid:
        :param goods_bids:
        :param did_arr:
        :param start_time:
        :param end_time:
        :return:
        """
        flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn = DBPOOL.connection()
        with conn.cursor() as cursor:
            sql = """
            UPDATE special_event_scope_data SET update_time=%s, event_bid=%s, 
            goods_arr=%s, did_arr=%s, start_time=%s, end_time=%s
            WHERE bid=%s AND cid=%s;
            """
            try:
                cursor.execute(sql,
                               (now_datetime, event_bid, str(goods_bids), str(did_arr), start_time, end_time, bid, cid))
                conn.commit()
                infoLog.debug('success, sql: UPDATE special_event_scope_data SET update_time=%s, event_bid=%s, '
                              'goods_arr=%s, did_arr=%s, start_time=%s, end_time=%s WHERE bid=%s AND cid=%s;',
                              now_datetime, event_bid, str(goods_bids), str(did_arr), start_time, end_time, bid, cid)
            except Exception:
                infoLog.warning('FAILED, sql: UPDATE special_event_scope_data SET update_time=%s, event_bid=%s, '
                                'goods_arr=%s, did_arr=%s, start_time=%s, end_time=%s WHERE bid=%s AND cid=%s;',
                                now_datetime, event_bid, str(goods_bids), str(did_arr), start_time, end_time, bid, cid)
                conn.rollback()
                flag = False
        conn.close()
        return flag

    @classmethod
    def delete(cls, bid: str, cid: str) -> bool:
        """
        删除
        :param bid:
        :param cid:
        :return:
        """
        flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn = DBPOOL.connection()
        with conn.cursor() as cursor:
            sql = """
            DELETE FROM special_event_scope_data WHERE bid=%s AND cid=%s;
            """
            try:
                cursor.execute(sql, (bid, cid))
                conn.commit()
                infoLog.debug('success, sql: DELETE FROM special_event_scope_data WHERE bid=%s AND cid=%s;', bid, cid)
            except Exception:
                infoLog.warning('FAILED, sql: DELETE FROM special_event_scope_data WHERE bid=%s AND cid=%s;', bid, cid)
                conn.rollback()
                flag = False
        conn.close()
        return flag

    @classmethod
    def get_count(cls, bid, cid):
        """
        查询条数
        :param bid:
        :param cid:
        :return:
        """
        count = 0
        conn = DBPOOL.connection()
        with conn.cursor() as cursor:
            sql = """
                SELECT COUNT(bid) AS sum_count FROM special_event_scope_data WHERE bid=%s AND cid=%s;
                """
            try:
                cursor.execute(sql, (bid, cid))
                result = cursor.fetchone()
                count = result[0]
            except Exception:
                infoLog.warning('FAILED, sql: SELECT COUNT(bid) AS sum_count '
                                'FROM special_event_scope_data WHERE bid=%s AND cid=%s;', bid, cid)
                conn.rollback()
        conn.close()
        return count

    @classmethod
    def get_goods_ids(cls, cid, did, start_time, end_time):
        """
        根据cid,did,start_time,end_time获取goods_id
        :param cid:
        :param did:
        :param start_time:
        :param end_time:
        :return:
        """
        goods_ids = []
        conn = DBPOOL.connection()
        with conn.cursor() as cursor:
            sql = """
                SELECT did_arr,goods_arr,start_time,end_time FROM special_event_scope_data WHERE cid=%s 
                    AND 
                        ((end_time > %s AND end_time <= %s) 
                        OR 
                        (end_time > %s AND start_time < %s))
                """
            try:
                cursor.execute(sql, (cid, start_time, end_time, end_time, end_time))
                results = cursor.fetchall()

                for result in results:
                    did_arr = ast.literal_eval(result[0])
                    # print(did_arr)
                    for one_did in did_arr:
                        if str(one_did) == str(did):
                            goods_ids.extend(ast.literal_eval(result[1]))
                            break
            except Exception:
                conn.rollback()
        conn.close()
        # 去重
        return list(set(goods_ids))

