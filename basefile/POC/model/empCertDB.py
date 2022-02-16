"""
@author: shenzh
@contact: shenzihan_i@didichuxing.com
@file: empCertDB.py
@time: 2019-10-09 14:48
@desc:
"""
import pymysql


from config.db import conf
from utils.dateUtils import DateUtils
from utils.myLogger import infoLog
from utils.testDBPool import DBPOOL

class empCertDB:
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
            # cls.connection = pymysql.Connection(
            #     host=cls.host,
            #     database=cls.database,
            #     user=cls.user,
            #     password=cls.pwd,
            #     charset='utf8'
            # )
            return cls.connection
        except pymysql.DatabaseError:
            return None

    @classmethod
    def insert_record(cls, cid:str, eid:str,  opt:str,
                      certname:str, closingdate:str):
        res_flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = """
                        INSERT INTO employee_certificate(cid,eid,opt,certname,closingdate,create_time,update_time,status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                        """
            try:
                cursor.execute(sql, (cid, eid, opt, certname, closingdate, now_datetime, now_datetime, '1'))

                conn.commit()
                infoLog.debug(
                    'success, sql: INSERT INTO employee_certificate (cid,eid,opt,certname,closingdate,create_time,update_time, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);',
                    cid,eid,opt,certname,closingdate,now_datetime, now_datetime, '1')
            except Exception:
                infoLog.warning(
                    'FAILED, sql: INSERT INTO employee_certificate (cid,eid,opt,certname,closingdate, create_time,update_time,status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);',
                    cid,eid,opt,certname,closingdate,now_datetime, now_datetime, '1')
                conn.rollback()
                res_flag = False
        conn.close()
        return res_flag


    @classmethod
    def delete_record(cls,cid:str,eid:str):
        res_flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = """
                    UPDATE employee_certificate SET opt='delete',status=0, update_time=%s WHERE cid=%s AND eid=%s AND status=1;
                    """
            try:
                cursor.execute(sql, (now_datetime, cid, eid))
                conn.commit()
                infoLog.debug('success, sql: UPDATE employee_certificate SET status=0,update_time=%s WHERE cid=%s AND eid=%s;', now_datetime, cid , eid)
            except Exception:
                infoLog.warning('FAILED, sql: UPDATE employee_certificate SET status=0,update_time=%s WHERE cid=%s AND eid=%s;', now_datetime, cid , eid)
                conn.rollback()
                res_flag = False
        conn.close()
        return res_flag

    @classmethod
    def select_record_exist(cls,cid:str,eid:str):
        row_flag = 0
        now_datetime = DateUtils.get_now_datetime_str()
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = """
                        SELECT cid,eid from employee_certificate WHERE cid=%s AND eid=%s AND status=1;
                  """
            try:
                row_flag = cursor.execute(sql, (cid, eid))
                conn.commit()
                infoLog.debug(
                    'success, sql: UPDATE labor_task SET status=0 WHERE cid=%s AND eid=%s ;',
                    cid, eid)
            except Exception:
                infoLog.warning(
                    'FAILED, sql: UPDATE labor_task SET status=0 WHERE cid=%s AND eid=%s ;',
                    cid, eid)
                conn.rollback()
        conn.close()
        return row_flag

    @classmethod
    def update_record(cls,cid:str,eid:str,opt:str,certname:str,closingdate:str):

        res_flag = False
        print('e')
        row_influenced = cls.select_record_exist(cid,eid)
        print('s')
        if row_influenced:
            res_flag = cls.delete_record(cid,eid)
            if not res_flag:
                infoLog.warning('Update操作时，软删除失败，将直接插入新记录。')
            res_flag = cls.insert_record(cid,eid,opt,certname,closingdate)
        else:
            res_flag = cls.insert_record(cid,eid,opt,certname,closingdate)
        return res_flag

