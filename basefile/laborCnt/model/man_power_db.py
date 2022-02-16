"""
@author: liyabin
@contact: liyabin_i@didiglobal.com
@file: man_power_db.py
@time: 2019-09-12 12:41
@desc:
"""
import pymysql as MySQLdb

from config.db import conf
from utils.dateUtils import DateUtils
from utils.myLogger import infoLog
from utils.testDBPool import DBPOOL

class ManPowerDB:
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
            # cls.connection = MySQLdb.Connection(
            #     host=cls.host,
            #     database=cls.database,
            #     user=cls.user,
            #     password=cls.pwd,
            #     charset='utf8'
            # )
            cls.connection = DBPOOL.connection()
            return cls.connection
        except MySQLdb.DatabaseError:
            return None

    @classmethod
    def delete_man_power_record(cls,cid:str,bid:str,forecast_date:str,combiRule:str):
        '''
        软删除
        :param cid:
        :param bid:
        :return:
        '''
        flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = """
                    UPDATE labor_man_power SET status=0, update_time=%s WHERE cid=%s AND bid=%s AND forecast_date=%s AND combiRule=%s;
                    """
            try:
                cursor.execute(sql, (now_datetime, cid, bid,forecast_date,combiRule))
                conn.commit()
                infoLog.debug('success, sql: UPDATE labor_man_power SET status=0, update_time=%s WHERE cid=%s AND bid=%s AND forecast_date=%s AND combiRule=%s;', now_datetime, cid, bid,forecast_date,combiRule)
            except Exception:
                infoLog.warning('FAILED, sql: UPDATE labor_man_power SET status=0, update_time=%s WHERE cid=%s AND bid=%s AND forecast_date=%s AND combiRule=%s;', now_datetime, cid, bid,forecast_date,combiRule)
                conn.rollback()
                flag = False
        conn.close()
        return flag

    @classmethod
    def update_man_power_record(cls,cid:str,bid:str,forecast_date:str,combiRule:str,combiRuleNewVal:str,combiRuleOldVal:str):
        res = cls.delete_man_power_record(cid,bid,forecast_date,combiRule)
        if not res:
            infoLog.warning('Update操作时，软删除失败')
        res = cls.insert_man_power_record(cid, bid, forecast_date,combiRule, combiRuleNewVal, combiRuleOldVal)
        return res

    @classmethod
    def insert_man_power_record(cls,cid:str,bid:str,forecast_date:str,combiRule:str,combiRuleNewVal:str,combiRuleOldVal:str):
        flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = """
                        INSERT INTO labor_man_power (cid, bid, forecast_date,combiRule, combiRuleNewVal, combiRuleOldVal,create_time, 
                        update_time,status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                        """
            try:
                cursor.execute(sql, (cid, bid,forecast_date, combiRule, combiRuleNewVal, combiRuleOldVal, now_datetime,
                                     now_datetime, '1'))
                conn.commit()
                infoLog.debug('success, sql: INSERT INTO labor_man_power (cid, bid, forecast_date,combiRule, combiRuleNewVal, combiRuleOldVal,create_time, update_time,status) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s);',
                              cid, bid, forecast_date,combiRule, combiRuleNewVal, combiRuleOldVal, now_datetime,
                              now_datetime, '1')
            except Exception:
                infoLog.warning('FAILED, sql: INSERT INTO labor_man_power (cid, bid, forecast_date,combiRule, combiRuleNewVal, combiRuleOldVal,create_time, update_time,status) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s);',
                              cid, bid, forecast_date,combiRule, combiRuleNewVal, combiRuleOldVal, now_datetime,
                              now_datetime, '1').rollback()
                flag= False
        conn.close()
        return flag

if __name__ == '__main__':
    record = {"cid": "123456", "bid": "201903291241563630561001235f0258",
              "combiRuleData":
                  [
                      {"combiRule": "20190605101543145043101404020054,20190605101543145043101404020053",
                       "combiRuleNewVal": "3-5",
                       "combiRuleOldVal": "3-4"
                       }
                  ]
              }
    cid = record['cid']
    bid = record['bid']
    combiRule = record['combiRuleData'][0]['combiRule']
    combiRuleNewVal = record['combiRuleData'][0]['combiRuleNewVal']
    combiRuleOldVal = record['combiRuleData'][0]['combiRuleOldVal']
    res = ManPowerDB.update_man_power_record(cid, bid, combiRule, combiRuleNewVal, combiRuleOldVal)
    print(res)
