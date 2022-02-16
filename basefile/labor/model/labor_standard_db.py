#!/usr/bin/env python
# encoding: utf-8

"""
@author: sunsong
@contact: sunsong@didiglobal.com
@file: labor_standard_db.py
@time: 2019-08-19 15:57
@desc:
"""

import logging
import traceback
from typing import List, Tuple, Dict, Union
from utils.myLogger import infoLog, tracebackLog
from config.db import conf
from datetime import datetime, timedelta
from utils.testDBPool import DBPOOL
from tornado import gen


class LaborStandard:

    @classmethod
    def insert_record(cls, bid, cid, mode, masterType, slaveType, detailRank, masterTypeScale,
                      slaveTypeScale, worktimeMinute, status,masterTypeMinScale,slaveTypeMinScale) -> bool:
        """
        插入记录
        :param bid:
        :param cid:
        :param mode:
        :param masterType:
        :param slaveType:
        :param detailRank:
        :param masterTypeScale:
        :param slaveTypeScale:
        :param worktimeMinute:
        :param status:
        :return:
        """

        flag = True
        conn = DBPOOL.connection()
        now = datetime.now()
        try:
            cursor = conn.cursor()
            sql = """
            INSERT INTO labor_standard(bid, cid, mode, masterType, slaveType, detailRank, masterTypeScale, slaveTypeScale, 
            worktimeMinute, status,create_time,update_time,masterTypeMinScale,slaveTypeMinScale) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s);"""

            cursor.execute(sql, (bid, cid, mode, masterType,slaveType,detailRank,masterTypeScale,slaveTypeScale,worktimeMinute,status,now,now,masterTypeMinScale,slaveTypeMinScale))

            conn.commit()
            logging.debug("success , sql ,  INSERT INTO labor_standard (bid, cid, mode, masterType, slaveType, detailRank, masterTypeScale, slaveTypeScale, worktimeMinute, status,create_time,update_time) VALUES ('%s', '%s', '%s', '%s', '%s', %s, %s, %s, %s, %s,%s,%s)" %( str(bid), str(cid), str(mode), str(masterType),str(slaveType), detailRank,masterTypeScale, slaveTypeScale,worktimeMinute, status,now,now))
        except Exception:
            logging.warning("failed , sql ,  INSERT INTO labor_standard (bid, cid, mode, masterType, slaveType, detailRank, masterTypeScale, slaveTypeScale, worktimeMinute, status,create_time,update_time) VALUES ('%s','%s', '%s', '%s', '%s', %s, %s, %s, %s, %s,%s,%s)" %( str(bid), str(cid), str(mode), str(masterType),str(slaveType), detailRank,masterTypeScale, slaveTypeScale,worktimeMinute, status,now,now))
            conn.rollback()
            flag = False
        conn.close()
        return flag

    @classmethod
    def soft_delete_record(cls, bid, cid) -> bool:
        """
        软删除
        :param bid:
        :param cid:
        :param did:
        :return:
        """
        flag = True
        conn = DBPOOL.connection()
        cursor = conn.cursor()
        now = datetime.now()
        sql = """
        UPDATE labor_standard SET status=0,update_time=%s WHERE cid=%s AND bid=%s;
        """
        try:
            cursor.execute(sql, (now,str(bid), str(cid)))
            conn.commit()
            logging.debug('success, sql: %s', sql)
        except Exception:
            logging.warning('failed, sql: %s', sql)
            conn.rollback()
            flag = False
        conn.close()
        return flag

    @classmethod
    def soft_delete_record_bids(cls, delete_bids, cid) -> bool:
        """
        软删除
        :param delete_bids:
        :param cid:
        :return:
        """
        flag = True
        conn = DBPOOL.connection()
        cursor = conn.cursor()
        now = datetime.now()
        for bid in delete_bids:
            sql = """
                UPDATE labor_standard SET status=0,update_time=%s WHERE cid=%s AND bid = %s;
                """
            try:
                cursor.execute(sql, (now,str(cid), str(bid)))
                conn.commit()
                logging.debug('success, sql: %s', sql)
            except Exception:
                logging.warning('failed, sql: %s', sql)
                conn.rollback()
                flag = False
        conn.close()
        return flag

    @classmethod
    def get_labor_standard_by_nodeid(cls, bid, cid) -> Dict[str, Union[str, List[Tuple[int, str, str, int]]]]:
        """
        获取工时标准
        :param bid:
        :param cid:
        :param did:
        :return:
        """
        conn = DBPOOL.connection()
        cursor = conn.cursor()
        sql = """
            SELECT mode, masterType, slaveType, detailRank, masterTypeScale, slaveTypeScale, worktimeMinute FROM labor_standard 
            WHERE cid=%s AND bid=%s  AND status=1;
            """
        try:
            cursor.execute(sql, (str(bid), str(cid)))
            result = cursor.fetchall()
            logging.debug('success, sql: %s', sql)
        except Exception:
            logging.warning('failed, sql: %s', sql)
            result = []
        conn.close()
        if result:
            res_list: Dict[int, Tuple[int, str, str, int]] = {}
            for item in result:
                mode = item[0]  # ['mode']
                master_type = item[1]  # ['masterType']
                slave_type = item[2]  # ['slaveType']
                rank = int(item[3])  # ['detailRank']
                m_scale = float(item[4])  # ['masterTypeScale']
                s_scale = float(item[5])  # ['slaveTypeScale']
                w_time = int(item[6])  # ['worktimeMinute']
                res_list[rank] = (m_scale, s_scale, w_time)
            res = {
                'mode': mode,
                'masterType': master_type,
                'slaveType': slave_type,
                'data': res_list
            }
            return res
        else:
            logging.warning('get null result while get labor standard for bid: %s, cid: %s', str(bid),str(cid))
            return {}

    @classmethod
    def get_labor_standard(cls, bid, cid) -> Dict[str, Union[str, List[Tuple[int, str, str, int]]]]:
        """
        获取工时标准
        :param bid:
        :param cid:
        :param did:
        :return:
        """
        conn = DBPOOL.connection()
        cursor = conn.cursor()
        sql = """
            SELECT mode, masterType, slaveType, detailRank, masterTypeMinScale, masterTypeScale,  worktimeMinute FROM labor_standard 
            WHERE cid=%s AND bid=%s  AND status=1;
            """
        try:
            cursor.execute(sql, (str(cid), str(bid)))
            result = cursor.fetchall()
            logging.info('success, sql: %s', sql)
        except Exception:
            logging.info('failed, sql: %s', sql)
            result = []
        conn.close()
        if result:
            res_list: Dict[int, Tuple[int, str, str, int]] = {}
            for item in result:
                mode = item[0]  # ['mode']
                master_type = item[1]  # ['masterType']
                slave_type = item[2]  # ['slaveType']
                detailRank = item[3]  # int(item[3]) #['detailRank']
                masterTypeMinScale = float(0 if item[4] == '' else item[4])  # ['masterTypeScale']
                masterTypeScale = float(0 if item[5] == '' else item[5])  # ['slaveTypeScale']
                w_time = int(0 if item[6] == '' else item[6])  # ['worktimeMinute']
                res_list[detailRank] = (masterTypeMinScale, masterTypeScale, w_time)
            res = {
                'mode': mode,
                'masterType': master_type,
                'slaveType': slave_type,
                'data': res_list
            }
            return res
        else:
            logging.info('get null result while get labor standard for bid: %s, cid: %s', str(bid),
                         str(cid))
            return {}

    @classmethod
    def labor_cacl_value_modify_node(cls, updatetime, cid, nodeBid, forecastStandard, nodeStandardBid, dayStr,
                                     startTimeStr, endTimeStr, forecastValue, editValue):
        '''
        存储计算的劳动工时
        labor_cacl_value node
        '''
        resultCode = 100
        conn = DBPOOL.connection()
        cursor = conn.cursor()
        sql_cnt = "select count(1) from labor_cacl_value where cid=%s and nodeBid=%s and nodeStandardBid=%s and " \
                  "endTimeStr=%s and startTimeStr=%s and dayStr=%s and status=1 and forecastStandard=%s"
        cursor.execute(sql_cnt, (cid, dayStr,startTimeStr,endTimeStr, nodeStandardBid, nodeBid, forecastStandard))
        c = cursor.fetchone()[0]
        # SQL 更新语句
        forecastType = 'node'
        try:
            if int(c) > 0:
                sql1 = "update labor_cacl_value set forecastValue=%s,editValue=%s,updatetime=%s where cid=%s and " \
                       "dayStr=%s and startTimeStr=%s and endTimeStr=%s and nodeStandardBid=%s and nodeBid=%s and " \
                       "forecastStandard=%s "
                cursor.execute(sql1, (forecastValue, editValue, updatetime, cid, dayStr,startTimeStr,endTimeStr,
                                      nodeStandardBid, nodeBid, forecastStandard))
            else:
                sql1 = "insert into  labor_cacl_value (forecastType,forecastStandard,inserttime,updatetime," \
                       "forecastValue,editValue,cid,dayStr,startTimeStr,endTimeStr,nodeStandardBid,nodeBid,status) " \
                       "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1) "
                cursor.execute(sql1, (forecastType, forecastStandard, updatetime, updatetime, forecastValue,
                                      editValue, cid, dayStr, startTimeStr, endTimeStr, nodeStandardBid, nodeBid))
            conn.commit()
            # return resultCode
        except:
            tracebackLog.error('traceback.format_exc():%s', traceback.format_exc())
            conn.rollback()
            resultCode = 102
            infoLog.info('execute update error code:102')
        finally:
            cursor.close()
            conn.close()
        return resultCode

    @classmethod
    def labor_cacl_value_modify_task(cls, updatetime, cid, taskBid, forecastStandard, laborStandardBid, did, dayStr,
                                     startTimeStr, endTimeStr, forecastValue, editValue, forecastType):
        '''
        存储计算的劳动工时
        labor_cacl_value
        '''
        resultCode = 100
        conn = DBPOOL.connection()
        cursor = conn.cursor()

        sql_cnt = "select count(1) from labor_cacl_value where cid=%s and did=%s and dayStr=%s and startTimeStr=%s " \
                  "and endTimeStr=%s and taskBid=%s and status=1 and forecastType=%s"
        cursor.execute(sql_cnt, (cid, did, dayStr, startTimeStr, endTimeStr, taskBid, forecastType))
        mm = cursor.fetchone()
        c = mm[0]

        # SQL 更新语句
        try:
            if int(c) > 0:
                sql1 = "update labor_cacl_value set min_caclValue=%s,max_caclValue=%s,forecastValue=%s,editValue=%s,updatetime=%s where cid=%s and " \
                       "taskBid=%s and did=%s and startTimeStr=%s and endTimeStr=%s and dayStr=%s and forecastType=%s"
                cursor.execute(sql1, (editValue,editValue,forecastValue, editValue, updatetime, cid, taskBid,did,startTimeStr, endTimeStr,dayStr, forecastType))
            else:
                sql1 = "insert into labor_cacl_value (forecastType, forecastStandard, inserttime, updatetime, " \
                       "forecastValue, editValue, cid, dayStr, startTimeStr, endTimeStr, laborStandardBid, taskBid, " \
                       "status,did,min_caclValue,max_caclValue) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1,%s,%s,%s)"
                cursor.execute(sql1, (forecastType, forecastStandard, updatetime, updatetime, forecastValue, editValue,
                                      cid, dayStr, startTimeStr, endTimeStr, laborStandardBid, taskBid, did,editValue,editValue))

            conn.commit()
            return resultCode
        except:
            tracebackLog.error('traceback.format_exc():%s', traceback.format_exc())
            conn.rollback()
            resultCode = 102
            cursor.close()
            conn.close()
            infoLog.info('execute update error code:102')
            return resultCode



    def labor_cacl_value_save(items, keys):
        '''
        存储计算的劳动工时
        labor_cacl_value
        :return:
        '''
        a = datetime.now()
        resultCode = 100
        conn = DBPOOL.connection()
        cursor = conn.cursor()
        b = datetime.now()
        infoLog.info('RequestDB labor_cacl_value_save' + str(b - a))

        # SQL 更新语句
        try:

            sql1 = "update labor_cacl_value set status = 0 where forecastType=%s and cid=%s and  dayStr=%s and did=%s"
            cursor.executemany(sql1, keys)

            c = datetime.now()
            infoLog.info('RequestDB labor_cacl_value_save' + str(c - b))

        except:
            tracebackLog.error('traceback.format_exc():%s', traceback.format_exc())
            conn.rollback()
            resultCode = 102
            cursor.close()
            conn.close()
            infoLog.info('execute update error code:102')
            return resultCode

        try:
            # SQL 插入语句
            d = datetime.now()
            infoLog.info('RequestDB labor_cacl_value_save' + str(d - c))
            sql = "insert into labor_cacl_value(inserttime,updatetime,forecastType,forecastStandard," \
                  "cid,dayStr,startTimeStr,endTimeStr,taskBid,laborStandardBid,caclValue,did,status," \
                  "min_caclValue,max_caclValue) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            infoLog.info('execute sql:%s' % sql)
            for i in items:
                cursor.execute(sql, i)  # 执行sql语句
            conn.commit()  # 提交到数据库执行
            infoLog.info('execute update save code:100')
            e = datetime.now()
            infoLog.info('RequestDB labor_cacl_value_save' + str(e - d))
        except:
            tracebackLog.error('traceback.format_exc():%s', traceback.format_exc())
            # 如果发生错误则回滚
            conn.rollback()
            resultCode = 101
            infoLog.info('execute insert error code:101')
        finally:
            cursor.close()
            conn.close()
            return resultCode

    @classmethod
    def get_base_calc(cls, cid, didArr, minStart, maxEnd, taskBids_list, laborStandardBids):
        calcBase = {}
        minStart = minStart[0:10]
        maxEnd = maxEnd[0:10]
        sql = " select dayStr,startTimeStr,endTimeStr,taskBid,laborStandardBid,if(editValue!=0,editValue," \
              "if(caclValue!=0,caclValue,forecastValue)) value  " \
              "from  labor_cacl_value " \
              "where cid=%s " \
              "and did in (" + ','.join(list(map(lambda x: str(x), didArr))) + ") " \
                "and dayStr >=%s " \
                "and dayStr <=%s " \
                 "and taskBid in (" + ','.join(list(map(lambda x: "'"+str(x)+"'", taskBids_list))) + ") "\
                 "and status=1  and editValue!=0" #每次调用都

        conn = DBPOOL.connection()
        cursor = conn.cursor()

        try:
            sqlinfo = (sql % (cid, minStart, maxEnd))

            cursor.execute(sql, (cid, minStart, maxEnd))
            alldata = cursor.fetchall()
            for m in alldata:
                if int(0 if m[5] == '' else m[5])!=0:
                   dayStr=m[0]
                   startTimeStr=m[1]
                   endTimeStr=m[2]
                   taskBid=m[3]
                   laborStandardBid=m[4]
                   key = '%s_%s_%s_%s_%s_%s' % (cid, ','.join(list(map(lambda x: str(x), didArr))), dayStr,
                                                startTimeStr, endTimeStr, taskBid)
                   calcBase[key] = float(0 if m[5] == '' else m[5])
            conn.commit()
            cursor.close()
        except:
            tracebackLog.error('execute sql:%s' % (sqlinfo))
            tracebackLog.error('traceback.format_exc():%s', traceback.format_exc())
        conn.close()
        return calcBase

    @classmethod
    def get_base_calc_node(cls, cid, didArr, startTime, endTime, nodeBid, nodeStandardBid):
        calcBase = {}

        sql = " select dayStr,startTimeStr,endTimeStr,if(editValue!=0,editValue,if(caclValue!=0,caclValue,forecastValue)) value  " \
              "from  labor_cacl_value " \
              "where cid=%s " \
              "and did in (" + ','.join(list(map(lambda x: str(x), didArr))) + ") " \
                "and dayStr >=%s " \
                "and dayStr <=%s " \
                 "and nodeBid = %s"\
                 "and nodeStandardBid  =%s" \
                 "and status=1 "

        conn = DBPOOL.connection()
        cursor = conn.cursor()

        try:
            sqlinfo = (sql % (cid, startTime, endTime, nodeBid, nodeStandardBid))

            cursor.execute(sql, (cid, startTime, endTime, nodeBid, nodeStandardBid))
            alldata = cursor.fetchall()
            for m in alldata:
                if int(0 if m[3] == '' else m[3])!=0:
                   dayStr=m[0]
                   startTimeStr=m[1]
                   endTimeStr=m[2]
                   key='%s_%s_%s' % (dayStr, startTimeStr, endTimeStr)
                   calcBase[key] = float(0 if m[3] == '' else m[3])
            conn.commit()
            cursor.close()
        except:
            tracebackLog.error('execute sql:%s' % (sqlinfo))
            tracebackLog.error('traceback.format_exc():%s', traceback.format_exc())
        conn.close()
        return calcBase


if __name__ == '__main__':
    pass
