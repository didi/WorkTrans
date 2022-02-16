"""
POC第四阶段-接口二-员工技能修改
by lyy
2019-10-09 14:28

"""

import pymysql

from config.db import conf
from utils.dateUtils import DateUtils
from utils.myLogger import infoLog
from utils.testDBPool import DBPOOL

class EmpSkillDB:
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
    def delete_record(cls, cid, eid):
        res_flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn = cls.get_connection()
        cursor = conn.cursor()
        sql = "UPDATE emp_skill SET status=0,opt=%s,update_time=%s WHERE cid=%s AND eid=%s;"
        try:
            cursor.execute(sql,('delete',now_datetime,cid,eid))
            conn.commit()
            infoLog.debug(
            'success, sql: UPDATE emp_skill SET status=0,update_time=%s WHERE cid=%s AND eid=%s;',
                now_datetime, cid, eid)

        except Exception:
            infoLog.warning('FAILED, sql: UPDATE emp_skill SET status=0,update_time=%s WHERE cid=%s AND eid=%s;',
                    now_datetime, cid, eid)
            conn.rollback()
            res_flag = False

        conn.close()
        return res_flag

    @classmethod
    def update_delete_record(cls, cid, eid):
        res_flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn = cls.get_connection()
        cursor = conn.cursor()
        sql = "UPDATE emp_skill SET status=0,opt=%s,update_time=%s WHERE cid=%s AND eid=%s;"
        try:
            cursor.execute(sql, ('update', now_datetime, cid, eid))
            conn.commit()
            infoLog.debug(
                'success, sql: UPDATE emp_skill SET status=0,update_time=%s WHERE cid=%s AND eid=%s;',
                now_datetime, cid, eid)

        except Exception:
            infoLog.warning('FAILED, sql: UPDATE emp_skill SET status=0,update_time=%s WHERE cid=%s AND eid=%s;',
                            now_datetime, cid, eid)
            conn.rollback()
            res_flag = False

        conn.close()
        return res_flag

    @classmethod
    def insert_record(cls,cid, eid,skillid, skillNum):
        res_flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn = cls.get_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO emp_skill(cid,eid,skill,skillNum,opt,create_time,update_time,status) VALUES " \
              "(%s,%s,%s,%s,%s,%s,%s,%s);"
        try:
            cursor.execute(sql, (cid, eid, skillid,skillNum,'update',now_datetime,now_datetime,1))
            conn.commit()
            infoLog.debug(
                'success, sql: INSERT INTO emp_skill(cid,eid,skill,skillNum,opt,create_time,update_time,status) VALUES " \
              "(%s,%s,%s,%s,%s,%s,%s,%s);',
                cid, eid, skillid,skillNum,'update',now_datetime,now_datetime,1)

        except Exception as ex:
            infoLog.warning(
                'FAILED, sql: INSERT INTO emp_skill(cid,eid,skill,skillNum,opt,create_time,update_time,status) VALUES " \
              "(%s,%s,%s,%s,%s,%s,%s,%s);%s',
                cid, eid, skillid,skillNum,'update',now_datetime,now_datetime,1,ex)
            conn.rollback()
            res_flag = False

        conn.close()
        return res_flag

