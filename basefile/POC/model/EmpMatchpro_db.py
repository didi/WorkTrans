"""
POC第四阶段-接口5-员工属性匹配
by lyy
2019-10-10 20:24

"""

import pymysql

from config.db import conf
from utils.dateUtils import DateUtils
from utils.myLogger import infoLog
from utils.testDBPool import DBPOOL

class EmpMatchproDB:
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
    def delete_record_deleteBids(cls, deleteBids, cid):
        """
        批量删除deleteBids
        """
        res_flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn = cls.get_connection()
        cursor = conn.cursor()
        for bid in deleteBids:
            sql = "UPDATE emp_matchpro SET status=0,opt=%s,update_time=%s WHERE bid=%s AND cid=%s"
            try:
                cursor.execute(sql, ('delete', now_datetime, str(bid), str(cid)))
                conn.commit()

            except Exception:
                infoLog.warning(
                    'FAILED, sql: UPDATE emp_matchpro SET status=0,opt=%s,update_time=%s WHERE bid =%s AND cid=%s;',
                    'delete', now_datetime, str(bid), str(cid))
                conn.rollback()
                res_flag = False

        conn.close()
        return res_flag

    @classmethod
    def delete_record(cls, cid, bid, did):
        res_flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn = cls.get_connection()
        cursor = conn.cursor()
        sql = "UPDATE emp_matchpro SET status=0,opt=%s,update_time=%s WHERE cid=%s AND bid=%s AND did=%s;"
        try:
            cursor.execute(sql, ('delete', now_datetime, cid, bid, did))
            conn.commit()

        except Exception:
            infoLog.warning(
                'FAILED, sql: UPDATE emp_matchpro SET status=0,opt=%s,update_time=%s WHERE cid=%s AND bid=%s AND did=%s;',
                'delete', now_datetime, cid, bid, did)
            conn.rollback()
            res_flag = False

        conn.close()
        return res_flag

    @classmethod
    def insert_record(cls, cid, bid, did,weight,ruleGroup,ruleDesc,ruleCpType,ruletag,ruleCpNum):
        res_flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn = cls.get_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO emp_matchpro(cid, bid, did,weight,ruleGroup,ruleDesc,ruleCpType,ruletag,ruleCpNum,opt,create_time,update_time,status) VALUES " \
              "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        try:
            cursor.execute(sql, (cid, bid, did,weight,ruleGroup,ruleDesc,ruleCpType,ruletag,ruleCpNum, 'update', now_datetime, now_datetime, 1))
            conn.commit()

        except Exception:
            infoLog.warning(
                'FAILED, sql: INSERT INTO emp_matchpro(cid, bid, did,weight,ruleGroup,ruleDesc,ruleCpType,ruletag,ruleCpNum,opt,create_time,update_time,status) VALUES " \
              "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);',
            cid, bid, did,weight,ruleGroup,ruleDesc,ruleCpType,ruletag,ruleCpNum, 'update', now_datetime, now_datetime, 1)
            conn.rollback()
            res_flag = False

        conn.close()
        return res_flag

if __name__ == '__main__':
    # a = EmpMatchproDB.insert_record(cid='666666', bid='20191120134929213029154739362222', did='2', weight='2',ruleGroup='worktime',ruleDesc='',ruleCpType='le',ruletag='weekWt',ruleCpNum='26')
    # print(a)
    # b =EmpMatchproDB.delete_record_deleteBids(deleteBids=['20191120134929213029154739362222'], cid='666666', did='2')
    # print(b)
    c = EmpMatchproDB.delete_record(cid='666666', bid='20191120134929213029154739362222', did='2')
    print(c)