#!/usr/bin/env python
# encoding: utf-8

"""
@author: pyd
@contact:
@file: pos_data_model.py
@time: 2020/2/28
@desc:
"""
from typing import List

import pymysql

from utils.testDBPool import DBPOOL
from utils.dateUtils import DateUtils
from utils.myLogger import infoLog


class PosDataModel:

    @classmethod
    def insert_record(cls, cid: str, did: str, gmt_bill: str, gmt_trunover: str, money: str, data_value: str,
                      bill_year: str, bill_month: str, bill_day: str, bill_hour: str, bill_minute: str,
                      peoples: int, order_no: str, singleSales: int, payment: str, deviceCode: str,
                      insertTime: str, updateTime: str, aistatus: int, transaction_num: int,
                      commodity_code: str) -> bool:
        """
        新增pos数据
        :param cid:客户公司id
        :param did:部门或门店id
        :param gmt_bill:【接口】开单时间
        :param gmt_trunover:【接口】营业结算时间
        :param money:【接口】营业额
        :param data_value:【None】
        :param bill_year:日期-年？
        :param bill_month:日期-月？
        :param bill_day:日期-日？
        :param bill_hour:时间-时？
        :param bill_minute:时间-分？
        :param peoples:【接口】人数
        :param order_no:【接口】订单号
        :param singleSales:【接口】销售数量，单品销量
        :param payment:【接口】结算方式
        :param deviceCode:【接口】收银设备号
        :param insertTime:自动生成now_datetime
        :param updateTime:自动生成now_datetime
        :param aistatus:【None】
        :param transaction_num:【接口】交易笔数
        :param commodity_code:【接口】商品编码
        :return:
        """
        res_flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn = DBPOOL.connection()
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO base_pos_df (cid, did, gmt_bill, gmt_trunover, money, data_value,
                      bill_year, bill_month, bill_day, bill_hour, bill_minute,
                      peoples, order_no, singleSales, payment, deviceCode,
                      insertTime, updateTime, aistatus, transaction_num, commodity_code) 
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            try:
                cursor.execute(sql, (cid, did, gmt_bill, gmt_trunover, money, data_value,
                                     bill_year, bill_month, bill_day, bill_hour, bill_minute,
                                     peoples, order_no, singleSales, payment, deviceCode,
                                     insertTime, updateTime, aistatus, transaction_num, commodity_code))
                conn.commit()
            except Exception:
                conn.rollback()
                res_flag = False
        conn.close()
        return res_flag

    @classmethod
    def update_record(cls, cid: str, did: str, gmt_bill: str, gmt_trunover: str, money: str, data_value: str,
                      bill_year: str, bill_month: str, bill_day: str, bill_hour: str, bill_minute: str,
                      peoples: int, order_no: str, singleSales: int, payment: str, deviceCode: str,
                      insertTime: str, updateTime: str, aistatus: int, transaction_num: int,
                      commodity_code: str) -> bool:
        """
        更新pos数据
        :param cid:客户公司id
        :param did:部门或门店id
        :param gmt_bill:【接口】开单时间
        :param gmt_trunover:【接口】营业结算时间
        :param money:【接口】营业额
        :param data_value:【None】
        :param bill_year:日期-年？
        :param bill_month:日期-月？
        :param bill_day:日期-日？
        :param bill_hour:时间-时？
        :param bill_minute:时间-分？
        :param peoples:【接口】人数
        :param order_no:【接口】订单号
        :param singleSales:【接口】销售数量，单品销量
        :param payment:【接口】结算方式
        :param deviceCode:【接口】收银设备号
        :param insertTime:自动生成now_datetime
        :param updateTime:自动生成now_datetime
        :param aistatus:【None】
        :param transaction_num:【接口】交易笔数
        :param commodity_code:【接口】商品编码
        :return:
        """

        flag = True
        conn = DBPOOL.connection()
        with conn.cursor() as cursor:
            sql = 'UPDATE base_pos_df SET updateTime=%s, money=%s, data_value=%s, bill_year=%s, bill_month=%s, ' \
                  'bill_day=%s, bill_hour=%s, bill_minute=%s, peoples=%s, singleSales=%s, payment=%s, ' \
                  'deviceCode=%s, aistatus=%s, transaction_num=%s, commodity_code=%s '
            where_condition = ' WHERE cid=%s AND did=%s AND order_no=%s '
            where_condition_val = order_no
            if order_no is None:
                where_condition = ' WHERE cid=%s AND did=%s AND gmt_bill=%s '
                where_condition_val = gmt_bill
            try:
                cursor.execute(sql + where_condition,
                               (updateTime, money, data_value, bill_year, bill_month, bill_day, bill_hour, bill_minute,
                                peoples, singleSales, payment, deviceCode, aistatus, transaction_num, commodity_code,
                                cid, did, where_condition_val))
                conn.commit()
            except Exception:
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
    def get_count(cls, cid, did, gmt_bill, order_no):
        """
        查询条数
        :param cid:
        :param did:
        :param gmt_bill:
        :param order_no:
        :return:
        """
        count = 0
        pkey = order_no
        sql = """
                SELECT COUNT(cid) AS sum_count FROM base_pos_df WHERE cid=%s AND did=%s AND order_no=%s;
                """
        if order_no is None:
            sql = """
                SELECT COUNT(cid) AS sum_count FROM base_pos_df WHERE cid=%s AND did=%s AND gmt_bill=%s;
                """
            pkey = gmt_bill
        conn = DBPOOL.connection()
        with conn.cursor() as cursor:
            try:
                cursor.execute(sql, (cid, did, pkey))
                result = cursor.fetchone()
                count = result[0]
            except Exception:
                conn.rollback()
        conn.close()
        return count

    @classmethod
    def select(cls, cid: str, did: int, startDateTime: str, endDateTime: str, orderNoArr: List[str]):
        """
        :param
        :param cid:
        :param did:
        :param startDateTime:
        :param endDateTime:
        :param orderNoArr:
        :return:
        """
        if cid is None or len(cid) < 1 :
            return None

        conn = DBPOOL.connection()
        if orderNoArr is not None and len(orderNoArr) > 0:
            _orderNoArr = ','.join('"{}"'.format(i) for i in orderNoArr)
            orderNoArr = "and order_no in ({})".format(_orderNoArr)

        where = 'cid = "{}" and did  = {} and gmt_bill >= "{}" and gmt_bill < "{}" {} and aistatus = 1'\
            .format(cid, did, startDateTime, endDateTime, "" if orderNoArr is None else orderNoArr)
        allSql = 'select id, cid, did, date_format(gmt_bill, "%Y-%m-%d %H:%i:%s") as gmt_bill, ' \
                 'date_format(gmt_trunover, "%Y-%m-%d %H:%i:%s") as gmt_trunover, money, data_value,' \
                 'peoples, order_no, singleSales, ' \
                 'payment, deviceCode, insertTime, updateTime, aistatus, transaction_num, ' \
                 'commodity_code, insertTime, updateTime from base_pos_info_df ' \
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


