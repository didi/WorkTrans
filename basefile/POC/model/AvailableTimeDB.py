"""
@author: liyabin
@contact: liyabin_i@didiglobal.com
@file: AvailableTimeDB.py
@time: 2019-10-9 15:00
@desc:
"""
import pymysql

from config.db import conf
from utils.dateUtils import DateUtils
from utils.myLogger import infoLog
from utils.testDBPool import DBPOOL

class AvailableTimeDB:
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
    def insert_record(cls,cid:str,eid:str,opt:str,type:str,day:str,start:str,end:str):
        res_flag = False
        sql = ""
        now_datetime = DateUtils.get_now_datetime_str()
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            if start=="NULL" and end == "NULL":
                sql = """
                                        INSERT INTO sch_available_time(cid,eid,opt,type,day,create_time, update_time, status) VALUES (%s, %s, %s, %s, %s, %s, %s,%s);
                                        """
            else:

                sql = """
                            INSERT INTO sch_available_time(cid,eid,opt,type,day,start,end,create_time, update_time, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                            """
            try:

                if start == "NULL" and end == "NULL":
                    res_flag = cursor.execute(sql, (
                        cid, eid, opt, type, day,
                        now_datetime, now_datetime, '1'))
                else:
                    res_flag = cursor.execute(sql, (
                    cid,eid,opt,type,day,start,end,
                    now_datetime, now_datetime, '1'))


                conn.commit()
                infoLog.debug(
                    'success, sql:  %s' % sql)
            except Exception:
                infoLog.error(
                    'FAILED, sql:  %s' % sql)
                conn.rollback()
                res_flag = False
        conn.close()
        return res_flag

    @classmethod
    def delete_record(cls,cid:str,eid:str,day:str) -> bool:
        '''
        软删除 按cid、eid、day删除
        :param cid:
        :param eid:
        :param day:
        :return:
        '''
        res_flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = """
                    UPDATE sch_available_time SET opt='delete',status=0 WHERE cid=%s AND eid=%s AND day=%s AND status=1;
                    """
            try:
                cursor.execute(sql, (cid, eid, day))
                conn.commit()
                infoLog.debug('success, sql: %s' % sql)
            except Exception:
                infoLog.error('FAILED, sql: %s' % sql)
                conn.rollback()
                res_flag = False
        conn.close()
        return res_flag

    @classmethod
    def delete_record_by_start_end(cls, cid:str,eid:str,type:str,day:str,start:str,end:str) -> bool:
        '''
        软删除 按start、end删除
        :param cid:
        :param eid:
        :param day:
        :return:
        '''
        res_flag = True
        sql = ""
        now_datetime = DateUtils.get_now_datetime_str()
        conn = cls.get_connection()
        with conn.cursor() as cursor:

            if start=="NULL" and end=="NULL":
                sql = """
                                            UPDATE sch_available_time SET opt='delete',status=0,update_time=%s WHERE cid=%s AND eid=%s AND type=%s AND day=%s AND start is NULL AND end is NULL AND status=1;
                                            """
            else:
                sql = """
                            UPDATE sch_available_time SET opt='delete',status=0,update_time=%s WHERE cid=%s AND eid=%s AND type=%s AND day=%s AND start=%s AND end=%s AND status=1;
                            """
            try:
                if start == "NULL" and end == "NULL":
                    cursor.execute(sql, (now_datetime, cid, eid, type, day))
                else:
                    cursor.execute(sql, (now_datetime, cid, eid, type,day,start,end))
                conn.commit()
                infoLog.debug(
                    'success, sql: UPDATE sch_available_time SET opt="delete",status=0,update_time=%s WHERE cid=%s AND eid=%s AND type=%s AND day=%s AND start=%s AND end=%s AND status=1;', \
                    now_datetime, cid, eid, type,day,start,end)
            except Exception:
                infoLog.warning(
                    'FAILED, sql: UPDATE sch_available_time SET opt="delete",status=0,update_time=%s WHERE cid=%s AND eid=%s AND type=%s AND day=%s AND start=%s AND end=%s AND status=1;', \
                    now_datetime, cid, eid, type,day,start,end)
                conn.rollback()
                res_flag = False
        conn.close()
        return res_flag

    @classmethod
    def select_record_exist(cls,cid:str,eid:str,opt:str,type:str,day:str,start:str,end:str) -> bool:
        row_flag = 0
        sql = ""
        conn = cls.get_connection()
        with conn.cursor() as cursor:

            if start=="NULL" and end=="NULL":
                sql = """
                                            SELECT cid,eid,day from sch_available_time WHERE cid=%s AND eid=%s AND type=%s AND day=%s AND start is NULL AND end is NULL AND status=1;
                                            """

            else:
                sql = """
                                SELECT cid,eid,day from sch_available_time WHERE cid=%s AND eid=%s AND type=%s AND day=%s AND start=%s AND end =%s AND status=1;
                                """
            try:

                if start == "NULL" and end == "NULL":
                    row_flag = cursor.execute(sql, (cid,eid,type,day))
                else:
                    row_flag = cursor.execute(sql, (cid, eid, type, day, start, end))
                conn.commit()
                infoLog.debug(
                    'success, sql: SELECT cid,eid,day from sch_available_time WHERE cid=%s AND eid=%s AND type=%s AND day=%s AND start=%s AND end =%s;',
                     cid,eid,type,day,start,end)
            except Exception:
                infoLog.warning(
                    'FAILED, sql: SELECT cid,eid,day from sch_available_time WHERE cid=%s AND eid=%s AND type=%s AND day=%s AND start=%s AND end =%s;',
                     cid,eid,type,day,start,end)
                conn.rollback()
        conn.close()
        return row_flag

    @classmethod
    def update_record(cls,cid:str,eid:str,opt:str,type:str,day:str,start:str,end:str) -> bool:
        '''
        软删除
        :param cid:
        :param eid:
        :param opt:
        :param type:
        :param day:
        :param start:
        :param end:
        :return:
        '''
        # res_flag = False
        # res_select =  cls.select_record_exist(cid, eid, opt, type, day,start,end)
        # if res_select:
        #     res_flag = cls.delete_record_by_start_end(cid,eid,type,day,start,end)
        #     if not res_flag:
        #         infoLog.warning('Update操作时，软删除失败，将直接插入新记录。')
        #     res_flag = cls.insert_record(cid,eid,opt,type,day,start,end)
        #
        # else:
        #     res_flag = cls.insert_record(cid,eid,opt,type,day,start,end)
        # return res_flag

        res_flag = False
        res_flag = cls.insert_record(cid, eid, opt, type, day, start, end)
        return res_flag

