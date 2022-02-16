import pymysql
from DBUtils.PooledDB import PooledDB, SharedDBConnection
from config.db import conf
from utils.myLogger import infoLog, tracebackLog
from utils.global_keys import *
from utils.testDBPool import DBPOOL

def sql_run(func):
    def wrapper(*args, **kwargs):
        for t in range(TRY_times):
            data = func(*args, **kwargs)
            if data:
                return data
        return None
    return wrapper

class DBpool():
    def __init__(self):
        self.pool = self.Build_DB_pool(conf)
        print("init mysql")

    def Build_DB_pool(self,conf):
        DBPOOL = PooledDB(
            creator=pymysql,  # 使用链接数据库的模块
            maxconnections=POS_THREAD_NUM,  # 连接池允许的最大连接数，0和None表示不限制连接数
            mincached=POS_THREAD_NUM,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
            maxcached=POS_THREAD_NUM,  # 链接池中最多闲置的链接，0和None不限制
            blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
            maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
            setsession=[],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
            ping=0,
            host=conf.db['mysql']['host'],
            port=conf.db['mysql']['port'],
            user=conf.db['mysql']['user'],
            password=conf.db['mysql']['password'],
            database=conf.db['mysql']['database'],
            charset='utf8'
            )
        return DBPOOL
    def get_DB_pool(self):
        return self.pool

    @sql_run
    def update_sql_many(self,sql,items):
        conn, cursor = self._create()
        try:
             conn.ping()
             cursor.executemany(sql,items)
             conn.commit()
             self._close(cursor, conn)
             return True
        except Exception as e:
            conn.rollback()
            tracebackLog.error(e)
            self._close(cursor, conn)
        return False

    def update_sql_one(self,sql):
        conn,cursor = self._create()
        try:
             conn.ping()
             cursor.execute(sql)
             conn.commit()
             self._close(cursor, conn)
             return True
        except Exception as e:
            tracebackLog.error(e)
            conn.rollback()
            self._close(cursor, conn)
        return False

    def get_sql_all(self,sql):
        conn, cursor = self._create()
        try:
            conn.ping()
            cursor.execute(sql)
            data = cursor.fetchall()
            self._close(cursor,conn)
            return data
        except Exception as e:
            tracebackLog.error(e)
            self._close(cursor, conn)
        return None

    def get_sql_one(self,sql):
        conn, cursor = self._create()
        try:
            conn.ping()
            cursor.execute(sql)
            data = cursor.fetchone()
            self._close(cursor,conn)
            return data
        except Exception as e:
            tracebackLog.error(e)
            self._close(cursor, conn)
            return None

    def _close(self,conn,cursor):
        cursor.close()
        conn.close()

    def _create(self):
        conn = self.pool.connection()
        cursor = conn.cursor()
        return conn,cursor

