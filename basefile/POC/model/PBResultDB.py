from utils.dateUtils import DateUtils
from utils.myLogger import infoLog
from typing import List, Tuple
from config.db import conf
import pymysql

class PBResultDB:
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
            cls.connection = pymysql.Connection(
                host=cls.host,
                database=cls.database,
                user=cls.user,
                password=cls.pwd,
                charset='utf8'
            )
            return cls.connection
        except pymysql.DatabaseError:
            return None

    @classmethod
    def read_matrix(cls,cid:str,did:str,start_date:str,end_date:str):
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = """
                                    SELECT cid,did,forecast_date,start_time,end_time,task_matrix from task_matrix_ss WHERE cid=%s AND did=%s AND forecast_date>=%s and forecast_date<=%s and status=1;
                                    """
            try:
                cursor.execute(sql, (cid, did, start_date,end_date))
                result = cursor.fetchall()
                conn.commit()

            except Exception:
                conn.rollback()
        conn.close()
        return result

if __name__ == '__main__':
    result = PBResultDB.read_matrix(cid="123456",did="6",start_date="2019-07-12",end_date="2019-07-13")
    print(result)
    print(type(result[0][5]))