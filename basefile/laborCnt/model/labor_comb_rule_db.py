#!/usr/bin/env python
# encoding: utf-8

"""
@author: lishulin
@contact: lishulin_i@didiglobal.com
@file: labor_comb_rule_db.py
@time: 2019-09-09 22:46
@desc:
"""

import pymysql
import logging
from typing import Tuple
from config.db import conf
from utils.dateUtils import DateUtils
from utils.testDBPool import DBPOOL


class LaborCombRule:
    db_config = conf.db['mysql']
    table = 'labor_comb_rule'
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
            cls.conn = DBPOOL.connection()
            return cls.conn
        except pymysql.DatabaseError:
            return None

    @classmethod
    def is_record_exists(cls, cid, bid, did, rule_data) -> Tuple[bool, bool]:
        """
        whether the record exits.
        :param cid:
        :param bid:
        :param did:
        :param rule_data:
        :param status:
        :return:
        """
        exit_flag = False; execute_flag = True
        conn = DBPOOL.connection()
        record_num = 0
        cursor = conn.cursor()
        sql = """
            SELECT * FROM labor_comb_rule 
            WHERE cid = %s and bid = %s and did =%s and rule_data = %s and status = 1
            """
        try:
            record_num = cursor.execute(sql, (str(cid), str(bid), str(did), str(rule_data)))
            conn.commit()
        except Exception:
            conn.rollback()
            execute_flag = False
        conn.close()
        if record_num > 0:
            exit_flag = True
        return exit_flag, execute_flag

    @classmethod
    def insert_record(cls, cid, bid, did, rule_data, status=1) -> bool:
        """
        :param cid: 公司ID
        :param bid: 预测人数业务ID
        :param did: 部门ID
        :param rule_data: 组合规则信息
        :param status: 状态描述 1可用 0不可用
        :return: 是否成功
        """
        now_datetime = DateUtils.get_now_datetime_str()
        flag = True
        is_exit, _ = cls.is_record_exists(cid, bid, did, rule_data)
        if is_exit:
            return flag

        conn = DBPOOL.connection()
        try:
            cursor = conn.cursor()
            sql = "INSERT ignore INTO labor_comb_rule(cid, bid, did, rule_data, status, create_time, update_time) VALUES (%s, %s, %s, %s, %s, %s, %s);"
            cursor.execute(sql, (cid, bid, did, rule_data, status, now_datetime, now_datetime))
            conn.commit()
            logging.debug("success, sql, INSERT INTO labor_comb_rule(cid, bid, did, rule_data, status) VALUES (%s, %s, %s, %s, %s)"
                          %(str(cid), str(bid), str(did), str(rule_data), str(status)))
        except Exception:
            logging.warning("failed, sql, INSERT INTO labor_comb_rule(cid, bid, did, rule_data, status) VALUES (%s, %s, %s, %s, %s)"
                          %(str(cid), str(bid), str(did), str(rule_data), str(status)))
            conn.rollback()
            flag = False

        conn.close()
        return flag

    @classmethod
    def soft_delete_record(cls, cid, bid) -> bool:
        """
        软删除
        :param cid: 公司ID
        :param bid: 预测人数业务ID
        :return: 是否成功
        """
        now_datetime = DateUtils.get_now_datetime_str()
        flag = True
        conn = DBPOOL.connection()
        cursor = conn.cursor()
        sql = "UPDATE labor_comb_rule SET status=0 and update_time=%s WHERE cid=%s AND bid=%s ;"

        try:
            cursor.execute(sql, (now_datetime, str(cid), bid))
            conn.commit()
            logging.debug('success, sql: %s', sql)
        except Exception:
            logging.warning('failed, sql: %s', sql)
            conn.rollback()
            flag = False
        conn.close()
        return flag

    @classmethod
    def update_record(cls, cid, bid, did, rule_data, start=True) -> bool:
        """
        first soft delete records, then insert new records.
        :param cid:
        :param bid:
        :param did:
        :param rule_data:
        :param status:
        :return:
        """
        #if start:
        #    flag = cls.soft_delete_record(cid, bid, did)
        #    if not flag:
        #        logging.warning('软删除失败，将直接插入新记录')
        flag = cls.insert_record(cid, bid, did, rule_data)

        return flag



if __name__ == '__main__':
    json = {'cid': "123456",
            'bid': "201903291241563630561001235g025d",
            'did': 7,
            'ruleData': "201903291241563630561001235g0815"}
    # record = LaborCombRule.is_record_exists(json['cid'], json['bid'], json['did'], json['ruleData'])
    # flag = LaborCombRule.insert_record(json['cid'], json['bid'], json['did'], json['ruleData'])
    flag = LaborCombRule.update_record(json['cid'], json['bid'], json['did'], json['ruleData'])
    # print(record)
