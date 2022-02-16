"""
@author: liyabin
@contact: liyabin_i@didiglobal.com
@file: ComplianceDB.py
@time: 2019-10-11 13:46
@desc:
"""
import pymysql

from config.db import conf
from utils.dateUtils import DateUtils
from utils.myLogger import infoLog
from utils.testDBPool import DBPOOL

class ComplianceDB:
    db_config = conf.db['mysql']
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
    def insert_record(cls,cid:str,opt:str,bid:str,ptype:str,did:str,eid:str,
                      ruleType:str,ruleCpType:str,ruleCpNum:str,dayFusion:bool,
                      ruletag:str,cycle:str,shiftId:str,cret:str,timeRange:str,
                      startDate:str,caution:str):
        res_flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = """
                        INSERT INTO sch_compliance(cid,opt,bid,ptype,did,eid,ruleType,ruleCpType,ruleCpNum,dayFusion,
                        ruletag,cycle,shiftId,cret,timeRange,startDate,caution,create_time, update_time, status) 
                        VALUES (%s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,1);
                        """
            try:
                row = cursor.execute(sql, (
                    cid, opt, bid,ptype, did, eid, ruleType, ruleCpType, ruleCpNum, dayFusion,
                    ruletag, cycle, shiftId, cret, timeRange, startDate, caution,
                    now_datetime, now_datetime))

                conn.commit()
                infoLog.debug(
                    'success, sql: INSERT INTO sch_compliance(cid,opt,bid,ptype,did,eid,ruleType,ruleCpType,ruleCpNum,dayFusion,ruletag,cycle,shiftId,cret,timeRange,startDate,caution,create_time, update_time, status) VALUES (%s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,1);',
                    cid, opt,bid, ptype, did, eid, ruleType, ruleCpType, ruleCpNum, dayFusion,
                    ruletag, cycle, shiftId, cret, timeRange, startDate, caution,
                    now_datetime, now_datetime)
            except Exception:
                infoLog.warning(
                    'FAILED, sql: INSERT INTO sch_compliance(cid,opt,ptype,did,eid,ruleType,ruleCpType,ruleCpNum,dayFusion,ruletag,cycle,shiftId,cret,timeRange,startDate,caution,create_time, update_time, status) VALUES (%s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,1);',
                    cid, opt, ptype, did, eid, ruleType, ruleCpType, ruleCpNum, dayFusion,
                    ruletag, cycle, shiftId, cret, timeRange, startDate, caution,
                    now_datetime, now_datetime)
                conn.rollback()
                res_flag = False
        conn.close()
        return res_flag


    @classmethod
    def delete_record(cls,cid:str,bid:str) -> bool:
        """
        软删除
        :param bid:
        :return:
        """
        res_flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = """
                    UPDATE sch_compliance SET opt='delete',status=0,update_time=%s WHERE cid=%s AND bid=%s AND status=1;
                    """
            try:
                cursor.execute(sql, (now_datetime, cid,bid))
                conn.commit()
                infoLog.debug('success, sql: UPDATE sch_compliance SET opt="delete",status=0,update_time=%s WHERE cid=%s AND bid=%s AND status=1;', \
                              now_datetime, cid,bid)
            except Exception:
                infoLog.warning('FAILED, sql: UPDATE sch_compliance SET opt="delete",status=0,update_time=%s WHERE cid=%s AND bid=%s AND status=1;', \
                                now_datetime, cid,bid)
                conn.rollback()
                res_flag = False
        conn.close()
        return res_flag

    @classmethod
    def update_record(cls,cid:str,opt:str,bid:str,ptype:str,did:str,eid:str,
                      ruleType:str,ruleCpType:str,ruleCpNum:str,dayFusion:bool,
                      ruletag:str,cycle:str,shiftId:str,cret:str,timeRange:str,
                      startDate:str,caution:str) -> bool:

        res_flag = False
        res_flag = cls.insert_record(cid,opt,bid,ptype,did,eid,
                      ruleType,ruleCpType,ruleCpNum,dayFusion,
                      ruletag,cycle,shiftId,cret,timeRange,
                      startDate,caution)

        if not res_flag:
            infoLog.warning('Update操作时，insert操作失败')

        return res_flag

