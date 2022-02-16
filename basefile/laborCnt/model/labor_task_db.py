"""
@author: liyabin
@contact: liyabin_i@didiglobal.com
@file: ManPowerCls.py
@time: 2019-09-16 14:26
@desc:
"""
import pymysql

from config.db import conf
from utils.dateUtils import DateUtils
from utils.myLogger import infoLog
from utils.testDBPool import DBPOOL


class LaborTaskDB:
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
            # cls.connection = pymysql.Connection(
            #     host=cls.host,
            #     database=cls.database,
            #     user=cls.user,
            #     password=cls.pwd,
            #     charset='utf8'
            # )
            cls.connection = DBPOOL.connection()
            return cls.connection
        except pymysql.DatabaseError:
            return None

    @classmethod
    def insert_record(cls, cid: str, did: str, bid: str,
                      taskName: str, abCode: str, taskType: str, opt: str,
                      worktimeType: str, worktimeStart: str, worktimeEnd: str,
                      taskSkillBid: str, skillNum: str, cert: str,
                      fillCoefficient: str, discard: int, taskMinWorkTime: str, taskMaxWorkTime: str):
        res_flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = """
                        INSERT INTO labor_task(cid,did,bid,taskName,abCode,taskType,opt,worktimeType,worktimeStart,worktimeEnd,taskSkillBid,skillNum,cert,fillCoefficient,discard,taskMinWorkTime,taskMaxWorkTime, 
                        create_time, update_time, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s,%s, %s);
                """
            try:
                cursor.execute(sql, (
                    cid, did, bid, taskName, abCode, taskType, opt, worktimeType, worktimeStart, worktimeEnd,
                    taskSkillBid, skillNum, cert, fillCoefficient, discard, taskMinWorkTime, taskMaxWorkTime,
                    now_datetime, now_datetime, '1'))
                conn.commit()
                infoLog.debug(
                    'success, sql: %s' % sql)
            except Exception:
                infoLog.warning(
                    'FAILED, sql: %s' % sql)
                conn.rollback()
                res_flag = False
        conn.close()
        return res_flag

    @classmethod
    def insert_record_for_noCerts(cls, cid: str, did: str, bid: str,
                                  taskName: str, abCode: str, taskType: str, opt: str,
                                  worktimeType: str, worktimeStart: str, worktimeEnd: str,
                                  taskSkillBid: str, skillNum: str, fillCoefficient: str,
                                  discard: int, taskMinWorkTime: str, taskMaxWorkTime: str):
        res_flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = None
            if abCode:
                sql = """
                        INSERT INTO labor_task(cid,did,bid,taskName,abCode,taskType,opt,worktimeType,worktimeStart,worktimeEnd,taskSkillBid,skillNum,fillCoefficient,discard,taskMinWorkTime,taskMaxWorkTime,
                        create_time, update_time, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """
            else:
                sql = """
                        INSERT INTO labor_task(cid,did,bid,taskName,taskType,opt,worktimeType,worktimeStart,worktimeEnd,taskSkillBid,skillNum,fillCoefficient,discard,taskMinWorkTime,taskMaxWorkTime,
                        create_time, update_time, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """
            try:
                if abCode:
                    cursor.execute(sql, (
                        cid, did, bid, taskName, abCode, taskType, opt, worktimeType, worktimeStart, worktimeEnd,
                        taskSkillBid, skillNum, fillCoefficient, discard, taskMinWorkTime, taskMaxWorkTime,
                        now_datetime, now_datetime, '1'))
                else:
                    cursor.execute(sql, (
                        cid, did, bid, taskName, taskType, opt, worktimeType, worktimeStart, worktimeEnd,
                        taskSkillBid, skillNum, fillCoefficient, discard, taskMinWorkTime, taskMaxWorkTime,
                        now_datetime, now_datetime, '1'))
                conn.commit()
            except Exception:
                infoLog.warning(
                    'FAILED, sql: %s' % sql)
                conn.rollback()
                res_flag = False
        conn.close()
        return res_flag

    @classmethod
    def delete_record(cls, cid: str, bid: str, did: str):
        res_flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = """
                    UPDATE labor_task SET status=0, update_time=%s WHERE cid=%s AND bid=%s and did=%s and status=1;
                """
            try:
                cursor.execute(sql, (now_datetime, cid, bid, did))
                conn.commit()
            except Exception:
                conn.rollback()
                res_flag = False
        conn.close()
        return res_flag

    @classmethod
    def delete_laborrecord(cls, cid: str, bid: str):
        res_flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = """
                    UPDATE labor_task SET status=0, update_time=%s WHERE cid=%s AND bid=%s;
                """
            try:
                cursor.execute(sql, (now_datetime, cid, bid))
                conn.commit()
            except Exception:
                conn.rollback()
                res_flag = False
        conn.close()
        return res_flag

    @classmethod
    def select_record_exist(cls, cid: str, bid: str, did: str):
        row_flag = 0
        now_datetime = DateUtils.get_now_datetime_str()
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = """
                    SELECT cid,bid,did,taskSkillBid from labor_task WHERE cid=%s AND bid=%s AND did=%s AND status=1;
                """
            try:
                row_flag = cursor.execute(sql, (cid, bid, did))
                conn.commit()
            except Exception:
                conn.rollback()
        conn.close()
        return row_flag

    @classmethod
    def update_record(cls, cid: str, did: str, bid: str,
                      taskName: str, abCode: str, taskType: str, opt: str,
                      worktimeType: str, worktimeStart: str, worktimeEnd: str,
                      taskSkillBid: str, skillNum: str, cert: str, fillCoefficient: str, discard: int,
                      taskMinWorkTime: str, taskMaxWorkTime: str):

        res_flag = False
        res_flag = cls.insert_record(cid, did, bid,
                                     taskName, abCode, taskType, opt,
                                     worktimeType, worktimeStart, worktimeEnd,
                                     taskSkillBid, skillNum, cert,
                                     fillCoefficient, discard, taskMinWorkTime, taskMaxWorkTime)
        return res_flag

    @classmethod
    def update_record_for_noCerts(cls, cid: str, did: str, bid: str,
                                  taskName: str, abCode: str, taskType: str, opt: str,
                                  worktimeType: str, worktimeStart: str, worktimeEnd: str,
                                  taskSkillBid: str, skillNum: str, fillCoefficient: str,
                                  discard: int, taskMinWorkTime: str, taskMaxWorkTime: str):
        '''
        不传证书
        :param cid:
        :param did:
        :param bid:
        :param taskName:
        :param abCode:
        :param taskType:
        :param opt:
        :param worktimeType:
        :param worktimeStart:
        :param worktimeEnd:
        :param taskSkillBid:
        :param skillNum:
        :return:
        '''

        res_flag = False
        res_flag = cls.insert_record_for_noCerts(cid, did, bid,
                                                 taskName, abCode, taskType, opt,
                                                 worktimeType, worktimeStart, worktimeEnd,
                                                 taskSkillBid, skillNum, fillCoefficient,
                                                 discard, taskMinWorkTime, taskMaxWorkTime)
        return res_flag


if __name__ == '__main__':
    LaborTaskDB.insert_record_for_noCerts(cid='123456', did='7', bid='2345432', taskName=" ", abCode=None,
                                          taskType='223', opt='1234', worktimeType='333', worktimeStart='234',
                                          worktimeEnd='23454', taskSkillBid='1334445', skillNum='80')
    # LaborTaskDB.delete_record(cid='123456',did='7',bid='2345432')
    # a = LaborTaskDB.delete_laborrecord(cid='123456',did='7',bid='2345432')
    # a = LaborTaskDB.select_record_exist(cid='123456',did='7',bid='2345432')
    # print(a)
