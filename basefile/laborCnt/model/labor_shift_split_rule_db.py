"""
@author: liyabin
@contact: liyabin_i@didiglobal.com
@file:  labor_shift_split_rule_db.py
@time: 2019-09-09 15:37
@desc:
"""

import pymysql
import logging
import datetime
from utils.myLogger import infoLog
from config.db import conf
from typing import  Tuple
from utils.testDBPool import DBPOOL


class LaborShiftSplitRule:
    db_config = conf.db['mysql']
    table = 'labor_shift_split_rule'
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
            # cls.connection = pymysql.connect(
            #     host=cls.host,
            #     port=cls.port,
            #     user=cls.user,
            #     passwd=cls.pwd,
            #     db=cls.database,
            #     as_dict=True
            # )
            cls.connection = DBPOOL.connection()
            return cls.connection
        except pymysql.DatabaseError:
            return None

    @classmethod
    def insert_record(cls,cid:str,bid:str,did:str,opt:str,ruleCalType:str,ruleCpType:str,ruleCpNum:str,dayFusion:bool,status:int) -> bool:
        '''
        插入记录
        :param cid:
        :param bid:
        :param did:
        :param opt:
        :param ruleCalType:
        :param ruleCpType:
        :param ruleCpNum:
        :param dayFusion:
        :return:
        '''
        s = datetime.datetime.now()
        flag = True
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            try:

                sql = """
                INSERT INTO labor_shift_split_rule(cid,bid,did,opt,ruleCalType,ruleCpType,ruleCpNum,dayFusion,create_time,update_time,status) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s,now(),now(), %s);"""

                row = cursor.execute(sql, (cid,bid,did,opt,ruleCalType,ruleCpType,ruleCpNum,dayFusion,status))
                logging.info("Insert 操作影响行数：%s" % row)
                conn.commit()
                logging.debug('execute sql:%s' % sql)
            except Exception:
                flag = False
                logging.warning('execute sql:INSERT INTO labor_shift_split_rule')
                conn.rollback()
        conn.close()
        e = datetime.datetime.now()
        infoLog.info("insert_record操作此次耗时%s" %(e-s))
        return flag

    @classmethod
    def soft_delete_record(cls, cid:str, bid:str) -> bool:
        '''
        软删除
        :param cid:
        :param bid:
        :param did:
        :return:
        '''
        s = datetime.datetime.now()
        flag = True
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = """
               UPDATE labor_shift_split_rule SET status=0,update_time=now() WHERE cid=%s AND bid=%s AND status=1;
               """
            try:
                row = cursor.execute(sql, (str(cid), str(bid)))
                logging.info("Delete 操作影响行数：%s" % row)
                conn.commit()
                logging.debug('success, sql: %s', sql)
            except Exception:
                flag = False
                logging.warning('failed, sql: %s', sql)
                conn.rollback()
        conn.close()
        e = datetime.datetime.now()
        infoLog.info("soft_delete_record操作此次耗时%s" %(e-s))
        return flag

    @classmethod
    def select_record_id_exists(cls,cid, bid, did):
        '''
        查看id是否已存在
        :param cid:
        :param bid:
        :param did:
        :return:
        '''
        s = datetime.datetime.now()
        flag = True
        auto_id = None
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = """
                        SELECT auto_id,cid,bid,did,opt,ruleCalType,ruleCpType,ruleCpNum,dayFusion,status FROM labor_shift_split_rule 
                               WHERE cid = %s and bid = %s and did = %s and status=1
                               """
            try:
                row = cursor.execute(sql, (str(cid), str(bid), str(did)))
                logging.info("select 操作影响行数：%s" % row)
                if not row:
                    # print("空")
                    flag = False
                conn.commit()
                logging.debug('success, sql: %s', sql)
            except Exception:
                logging.warning('failed, sql: %s', sql)
                conn.rollback()
        conn.close()
        e = datetime.datetime.now()
        infoLog.info("select_record_exists操作此时耗时%s" % (e - s))
        return flag


    @classmethod
    def select_record_exists(cls,cid,bid,did,opt,ruleCalType,ruleCpType,ruleCpNum,dayFusion,status) -> Tuple[bool,int]:
        '''
        查询记录是否存在
        :param bid:
        :param did:
        :return:
        '''
        s = datetime.datetime.now()
        flag = True
        auto_id = None
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = """
                SELECT auto_id,cid,bid,did,opt,ruleCalType,ruleCpType,ruleCpNum,dayFusion,status FROM labor_shift_split_rule 
                       WHERE cid = %s and bid = %s and did =%s and opt =%s and ruleCalType =%s and ruleCpType =%s and ruleCpNum =%s and dayFusion =%s and status =%s
                       """
            try:
                row = cursor.execute(sql, (str(cid), str(bid), str(did),str(opt),str(ruleCalType),str(ruleCpType),str(ruleCpNum),int(dayFusion),str(status)))
                logging.info("select 操作影响行数：%s" % row)
                data = cursor.fetchall()
                if data:
                    # 自增主键
                    auto_id = data[0][0]
                else:
                    #print("空")
                    flag = False
                conn.commit()
                logging.debug('success, sql: %s', sql)
            except Exception:
                logging.warning('failed, sql: %s', sql)
                conn.rollback()
        conn.close()
        e = datetime.datetime.now()
        infoLog.info("select_record_exists操作此时耗时%s" %(e-s))
        return flag,auto_id

    @classmethod
    def update_record(cls,cid,bid,did,ruleCalType,ruleCpType,ruleCpNum,dayFusion,auto_id):
        '''
        更新操作
        :param cid:
        :param bid:
        :param did:
        :param ruleCalType:
        :param ruleCpType:
        :param ruleCpNum:
        :param dayFusion:
        :return:
        '''
        s = datetime.datetime.now()
        flag = True
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = """
                UPDATE labor_shift_split_rule SET cid=%(cid)s,bid=%(bid)s,did=%(did)s,ruleCalType=%(ruleCalType)s,ruleCpType =%(ruleCpType)s,ruleCpNum =%(ruleCpNum)s,update_time=now(),dayFusion =%(dayFusion)s
                     WHERE auto_id= %(auto_id)s
                               """
            try:
                info = {}
                info['cid'] = str(cid)
                info['bid'] = str(bid)
                info['did'] = str(did)
                info['ruleCalType'] = str(ruleCalType)
                info['ruleCpType'] = str(ruleCpType)
                info['ruleCpNum'] = str(ruleCpNum)
                info['dayFusion'] = dayFusion
                info['auto_id'] = str(auto_id)


                row = cursor.execute(sql, info)
                logging.info("update 操作影响行数：%s" % row)
                if not row:
                    flag = False
                conn.commit()
                logging.debug('success, sql: %s', sql)
            except Exception:
                logging.warning('failed, sql: %s', sql)
                conn.rollback()
        conn.close()
        e = datetime.datetime.now()
        infoLog.info("update_record操作此次耗时%s" %(e-s))
        return flag

if __name__ == '__main__':
    print(LaborShiftSplitRule.select_record_id_exists(cid='123456',did='6',bid='20190928114043391043147808050002'))

