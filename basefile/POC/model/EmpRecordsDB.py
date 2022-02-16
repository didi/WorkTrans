"""
@author: liyabin
@contact: liyabin_i@didiglobal.com
@file: EmpRecordsDB.py
@time: 2019-12-19 13:46
@desc:
"""
import pymysql
from config.db import conf
from utils.dateUtils import DateUtils
from utils.myLogger import infoLog
from utils.testDBPool import DBPOOL

class EmpRecordsDB:
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
            cls.connection = DBPOOL.connection()
            return cls.connection
        except pymysql.DatabaseError:
            return None

    @classmethod
    def read_workTime(cls,cid:str,eid:str,startDate:str,endDate:str,applyId:str,scheme_type:str):
        '''
        select cid,applyId,eid,type,sum(workTime) from task_schedule
            where
            status=1
            and cid=%s
            and eid=%s
            and schDay>=%s and schDay<%s
            and applyId=(SELECT max(applyId) FROM task_schedule where status=1 and cid=%s and eid=%s and schDay>=%s and schDay<%s and agthtype='lyb')
            and agthtype='lyb'
            group by cid,applyId,eid,type
        :param cid:
        :param eid:
        :param startDate:
        :param endDate:
        :return:
        '''
        result = None
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = '''
            select cid,'999999' as  applyId,eid,type,schDay,sum(workTime) from task_schedule
            where 
            status=1 
            and cid=%s
            and eid=%s
            and schDay>=%s and schDay<%s
            and agthtype='lyb'
            and scheme_type=%s
            group by cid,eid,type,schDay
            order by schDay
            '''

            try:
                cursor.execute(sql,(cid,eid,startDate,endDate,scheme_type))
                result = cursor.fetchall()
                conn.commit()

            except Exception:
                infoLog.warning(
                    'FAILED, sql: %s' % sql)
                conn.rollback()
        conn.close()
        return result

    @classmethod
    def read_schDayNumCon(cls, cid: str, eid: str, startDate: str, endDate: str):
        '''
        机器自动排班，读取记录时没有考虑人为修改，没有读取排班日期后包含在周期内的天数。
        :param cid:
        :param eid:
        :param startDate:
        :param endDate:
        :return:
        '''
        result = None
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = '''
                select cid,max(applyId),eid,schDay,type from task_schedule 
                where 
                status=1 
                and cid=%s
                and eid=%s
                and schDay>=%s and schDay<%s
                and agthtype='lyb'
                group by cid,eid,schDay,type
                '''

            try:
                cursor.execute(sql, (cid, eid, startDate, endDate))
                result = cursor.fetchall()
                conn.commit()

            except Exception:
                infoLog.warning(
                    'FAILED, sql: %s' % sql)
                conn.rollback()
        conn.close()
        return result

    @classmethod
    def read_schDayNumCon_for_cycle(cls, cid: str, eid: str, startDate: str, endDate: str,applyId:str,scheme_type:str):
        '''
        手动删除某一天的排班记录后，可能造成违反连续排班天数规则。
        采取读取整个周期的工作天数。
        :param cid:
        :param eid:
        :param startDate:
        :param endDate:
        :return:
        '''
        result = None
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = '''
                    select cid,max(applyId),eid,schDay,type from task_schedule 
                    where 
                    status=1 
                    and cid=%s
                    and eid=%s
                    and schDay>=%s and schDay<%s
                    and agthtype='lyb'
                    and scheme_type=%s
                    group by cid,eid,schDay,type
                    '''

            try:
                cursor.execute(sql, (cid, eid, startDate, endDate,scheme_type))
                result = cursor.fetchall()
                conn.commit()

            except Exception:
                infoLog.warning(
                    'FAILED, sql: %s' % sql)
                conn.rollback()
        conn.close()
        return result

    @classmethod
    def read_shiftNum(cls, cid: str, eid: str, startDate: str, endDate: str,applyId:str,scheme_type:str):
        result = None
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = '''
                    SELECT cid,'999999' as applyId,eid,schDay,startTime,endTime,workTime FROM task_schedule 
                    where status=1 
                    and agthtype='lyb' 
                    and cid=%s 
                    and eid=%s 
                    and schDay>=%s 
                    and schDay<%s
                    and scheme_type=%s
                    order by schDay,applyId desc;
                    '''

            try:
                cursor.execute(sql, (cid, eid, startDate, endDate,scheme_type))
                result = cursor.fetchall()
                conn.commit()

            except Exception:
                infoLog.warning(
                    'FAILED, sql: %s' % sql)
                conn.rollback()
        conn.close()
        return result

    @classmethod
    def read_schNumSame(cls, cid: str, startDate: str, endDate: str,applyId:str,scheme_type:str):
        '''
        读取员工在周期内的工作记录
        :param cid:
        :param startDate:
        :param endDate:
        :param scheme_type:
        :return:
        '''
        result = None
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = '''
                select t1.cid,t1.applyId,t1.eid,t1.schDay,t1.type,t1.startTime,t1.endTime from 
                (
                    select cid,'999999' as  applyId,eid,schDay,type,startTime,endTime from task_schedule 
                    where status=1
                    and cid=%s and (eid+0)>0 
                    and schDay>=%s and schDay<=%s and agthtype='lyb' 
                    and scheme_type=%s
                    group by cid,eid,schDay,type,startTime,endTime
                    order by cid,eid+0,schDay,startTime
                ) as t1,
                (select cid,eid,'999999' as  as new_applyId from task_schedule
                where status=1
                and cid=%s and (eid+0)>0
                and schDay>=%s and schDay<=%s and agthtype='lyb' 
                and scheme_type=%s
                group by cid,eid,schDay,type
                order by cid,eid+0,schDay,startTime 
                )t2
                where t1.cid=t2.cid and t1.eid=t2.eid and t1.applyId=t2.new_applyId
                '''

            try:
                cursor.execute(sql, (cid, startDate, endDate,scheme_type,cid, startDate, endDate,scheme_type))
                result = cursor.fetchall()
                conn.commit()

            except Exception:
                infoLog.warning(
                    'FAILED, sql: %s' % sql)
                conn.rollback()
        conn.close()
        return result

if __name__ == '__main__':
    info = EmpRecordsDB.read_schNumSame(cid='51000447',startDate='2019-12-01',endDate='2019-12-01',scheme_type='effect')
    print(info)
