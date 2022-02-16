# !/usr/bin/env python
# -*- coding:utf-8 -*-


import traceback
import time

from utils.myLogger import infoLog, tracebackLog
from typing import Dict
from utils.testDBPool import DBPOOL
import datetime
from pymysql.err import IntegrityError, OperationalError, InternalError
import pandas as pd


class PosDBModel:

    @classmethod
    def getHistoryPos(cls, cid, did, end_pre_day):
        """
        获取预测的参考的历史数据
        :param : did 部门id
        :param : startPreDay 预测开始时间
        :param : cid 公司id

        :return:
        """

        sql = """
                       SELECT
                       SUBSTRING_INDEX(shike, " ", 1) as date,
                       concat(substr(shike,12,3),'00') as hour,
                       sum(trueOrders) as trueOrders,
                       sum(predictOrders) as predictOrders
                       FROM view_pos_info_df
                       where cid=%s
                       and did=%s
                       and shike<%s
                       group by
                       SUBSTRING_INDEX(shike, " ", 1) ,
                       concat(substr(shike,12,3),'00');

                    """
        conn = DBPOOL.connection()
        cursor = conn.cursor()
        cursor.execute(sql, (cid, did, end_pre_day + datetime.timedelta(days=0)))

        all_data = cursor.fetchall()
        history_data = {'date': [], 'hour': [], 'trueOrders': [], 'predictOrders': []}

        for m in all_data:
            history_data.get('date', []).append(m[0])
            history_data.get('hour', []).append(m[1] + ':00')
            history_data.get('trueOrders', []).append(int(m[2]))
            history_data.get('predictOrders', []).append(int(m[3]))
        conn.commit()
        cursor.close()
        conn.close()
        data = pd.DataFrame(history_data)
        return data

    @classmethod
    def getBasePos(cls, did, start_base_day, start_pre_day, pre_type, cid):
        """
        获取预测的参考的历史数据
        :param : did 部门id
        :param : startBaseDay 预测参考的数据的历史数据开始时间
        :param : startPreDay 预测开始时间
        :param : preType 预测类型 date_value 营业额
        :param : cid cid
        :return:
        """
        # modified by caoyabin
        columns = {
            # 有真实值使用真实值。没有真实值，取预测值。为负的当作0。
            'trueGMV': ' if(trueGMV!=0, trueGMV, if(predictGMV>0,predictGMV,0))',
            'truePeoples': ' if(truePeoples!=0, truePeoples,if(predictPeoples>0,predictPeoples,0)) ',
            'trueOrders': ' if(trueOrders!=0, trueOrders, if(predictOrders>0,predictOrders,0)) '
        }
        new_sql = """
                select shike, """ + columns.get(pre_type) + """
                from view_pos_info_df
                where shike>=%s and shike<%s and cid = %s and did = %s and status = 0                
                """

        conn = DBPOOL.connection()
        cursor = conn.cursor()
        cursor.execute(new_sql, (start_base_day, start_pre_day, cid, did))
        history_data_dict = {}
        all_data = cursor.fetchall()
        for m in all_data:
            timing_string = m[0].strftime('%Y-%m-%d %H:%M')
            if timing_string[14:16] not in ('00', '15', '30', '45'):
                continue
            history_data_dict[timing_string] = m[1]
        conn.commit()
        cursor.close()
        conn.close()
        return history_data_dict

    @classmethod
    def getAdjustPos(cls, did, startBaseDay, startPreDay, preType):
        """
        获取预测的参考的历史数据
        :param : did 部门id
        :param : startBaseDay 预测参考的数据的历史数据开始时间
        :param : startPreDay 预测开始时间
        :param : preType 预测类型 date_value 营业额

        :return:
        """

        sqlParts = {
            'trueGMV': 'adjustGMV',
            'truePeoples': 'adjustPeoples',
            'trueOrders': 'adjustOrders'
        }
        sqlPart = sqlParts.get(preType)
        sql = """
            select
                 shike,""" + sqlPart + """ as value
            from  view_pos_df
            where did=%s and shike>='%s' and shike<'%s' and status=0
            and %s!=0
            """

        conn = DBPOOL.connection()
        cursor = conn.cursor()

        sqlinfo = (sql % (did, startBaseDay, startPreDay, sqlPart))
        infoLog.info('adjustPosSql : %s' % (sqlinfo.replace('\n', '').replace(' ', '')))
        cursor.execute(sql, (did, startBaseDay, startPreDay, sqlPart))

        adjustPosDict = {}
        alldata = cursor.fetchall()
        for m in alldata:
            adjustPosDict[m[0]] = m[1]
        conn.commit()
        cursor.close()
        conn.close()
        return adjustPosDict

    @classmethod
    def pushData(cls, data):
        resultCode = 100
        conn = DBPOOL.connection()
        cursor = conn.cursor()
        # SQL 插入语句
        sql = "insert into base_pos_df(cid,companyName,did,gmt_bill,gmt_trunover,money,data_value,peoples,singleSales,payment,deviceCode,order_no,insertTime,updateTime,aistatus,bill_year,bill_month,bill_day,bill_hour,bill_minute) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        # 区别与单条插入数据，VALUES ('%s', '%s',  %s,  '%s', %s) 里面不用引号
        # sql = "insert into base_pos_df(cid,companyName) values(%s,%s)"
        infoLog.info('execute sql:%s' % sql)
        infoLog.info('execute data:%s' % data)
        try:
            cursor.executemany(sql, data)  # 执行sql语句
            conn.commit()  # 提交到数据库执行
            infoLog.info('execute code:100')
        except:
            tracebackLog.error('traceback.format_exc():%s', traceback.format_exc())
            # 如果发生错误则回滚
            conn.rollback()
            resultCode = 101
            infoLog.info('execute code:101')
        finally:
            cursor.close()
            conn.close()
            return resultCode

    @classmethod
    def modify_update_i(cls, update_i):
        conn = DBPOOL.connection()
        cursor = conn.cursor()
        for i in update_i:
            for d in i[3]:
                PosDBModel.modifyData(cursor, i[0], i[1], i[2], d[12], i[3], i[4])
                conn.commit()
        cursor.close()
        conn.close()

    @classmethod
    def modifyData(cls, cursor, cid, did, gmt_bill, order_no, items, s):
        if order_no is None:
            s1 = "select count(1) from base_pos_df where cid='%s' and did='%s' and gmt_bill='%s' and aistatus=1"
            cursor.execute(s1, (cid, did, gmt_bill))
        else:
            s2 = "select count(1) from base_pos_df where cid='%s' and did='%s' and order_no='%s' and aistatus=1"
            cursor.execute(s2, (cid, did, order_no))
        c = cursor.fetchone()
        if c is None:
            sql3 = "insert into base_pos_df (cid,did,gmt_bill,gmt_trunover,money,data_value,transaction_num,peoples,singleSales,commodity_code,payment,deviceCode,order_no,insertTime,updateTime,aistatus,bill_year,bill_month,bill_day,bill_hour,bill_minute) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.executemany(sql3, items)  # 执行sql语句 #
        else:
            if order_no is None:
                # SQL 更新语句
                sql1 = "update base_pos_df set aistatus=0 where cid='%s' and did='%s' and gmt_bill='%s' and aistatus=1"
                cursor.execute(sql1, (cid, did, gmt_bill))
            else:
                sql2 = "update base_pos_df set aistatus=0 where cid='%s' and did='%s' and order_no='%s' and aistatus=1"
                cursor.execute(sql2, (cid, did, order_no))
            sql3 = "insert into base_pos_df (cid,did,gmt_bill,gmt_trunover,money,data_value,transaction_num,peoples,singleSales,commodity_code,payment,deviceCode,order_no,insertTime,updateTime,aistatus,bill_year,bill_month,bill_day,bill_hour,bill_minute) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.executemany(sql3, items)  # 执行sql语句

    @classmethod
    def updateView(cls, updateTime, cid, did, day):
        resultCode = 103

        conn = DBPOOL.connection()
        cursor = conn.cursor()

        sql1 = "delete from view_pos_df where cid=%s and did=%s and substr(shike,1,10)=%s "
        infoLog.info('updateView execute data sql %s :%s   %s %s ' % (sql1, cid, did, day))

        try:
            cursor.execute(sql1, (cid, did, day))
            infoLog.info('execute update code:100')
            conn.commit()
        except:
            tracebackLog.error('traceback.format_exc():%s', traceback.format_exc())
            conn.rollback()
            resultCode = 102
            infoLog.info('execute update error code:102')

        try:
            # SQL 插入语句
            sql = """
                    insert into  view_pos_df(cid,did,shike,trueGMV,predictGMV,adjustGMV,truePeoples,predictPeoples,adjustPeoples,status,insertTime,updateTime,trueOrders,predictOrders,adjustOrders)
                    select
                    cid,
                    did,
                    concat(substr(gmt_bill,1,14),LPAD(15*floor(bill_minute/15),2,0))  as shike,
                    round(sum(IFNULL(data_value,0))/100,2) as trueGMV,
                    0 as predictGMV,
                    0 as adjustGMV,
                    sum(IFNULL(peoples,0)) as truePeoples,
                    0 as predictPeoples,
                    0 as adjustPeoples,
                    0 as status,
                    %s as insertTime,
                    %s as updateTime,
                    count(distinct order_no) as trueOrders,
                    0 as predictOrders,
                    0 as adjustOrders
                    from base_pos_df
                    where
                    cid=%s
                    and did=%s
                    and substr(gmt_bill,1,10)=%s
                    and aistatus=1
                    group by cid, 
                    did,
                    concat(substr(gmt_bill,1,14),LPAD(15*floor(bill_minute/15),2,0));
                    """
            infoLog.info('execute data sql %s :%s,%s,%s,%s,%s ' % (sql, updateTime, updateTime, cid, did, day))
            cursor.execute(sql, (updateTime, updateTime, cid, did, day))  # 执行sql语句
            conn.commit()  # 提交到数据库执行
            infoLog.info('execute update save code:100')
            resultCode = 100

            # sqld = """delete from view_pos_df where auto_id in (select n.auto_id from (select a.auto_id  from view_pos_df a join (select cid,did,shike,count(1) as cnt,max(auto_id) as b_auto_id from view_pos_df group by cid,did,shike having cnt>=2 ) b on a.cid=b.cid and a.shike=b.shike and a.did=b.did where a.auto_id!=b_auto_id) n); """
            # cursor.execute(sqld)
            # conn.commit()
        except IntegrityError as e:
            infoLog.info(e)
        except InternalError as e:
            infoLog.info(e)
            time.sleep(6)
            PosDBModel.updateView(cls, updateTime, cid, did, day)
        except OperationalError as e:
            infoLog.info(e)
            time.sleep(6)
            PosDBModel.updateView(cls, updateTime, cid, did, day)
        except:
            tracebackLog.error('traceback.format_exc():%s', traceback.format_exc())
            # 如果发生错误则回滚
            conn.rollback()
            resultCode = 100
        finally:
            cursor.close()
            conn.close()
        return resultCode

    @classmethod
    def updateView_min_max(cls, updateTime, cid, did, sday, eday):
        """
        :param updateTime:
        :param cid:
        :param did:
        :param sday: 开始更新日期
        :param eday: 结束更新日期
        :return:
        """
        resultCode = 103

        conn = DBPOOL.connection()
        cursor = conn.cursor()

        sql1 = "delete from view_pos_df where cid=%s and did=%s and substr(shike,1,10)>=%s  and substr(shike,1,10)<=%s"
        infoLog.info('delete from view_pos_df data sql %s :%s   %s %s  %s' % (sql1, cid, did, sday, eday))

        try:
            cursor.execute(sql1, (cid, did, sday, eday))
            conn.commit()
        except:
            conn.rollback()
            resultCode = 102
            infoLog.info('delete from view_pos_df  error code:102')

        try:
            # SQL 插入语句
            sql = """
                        insert into  view_pos_df(cid,did,shike,trueGMV,predictGMV,adjustGMV,truePeoples,predictPeoples,adjustPeoples,status,insertTime,updateTime,trueOrders,predictOrders,adjustOrders)
                        select
                        cid,
                        did,
                        concat(substr(gmt_bill,1,14),LPAD(15*floor(bill_minute/15),2,0))  as shike,
                        round(sum(IFNULL(data_value,0))/100,2) as trueGMV,
                        0 as predictGMV,
                        0 as adjustGMV,
                        sum(IFNULL(peoples,0)) as truePeoples,
                        0 as predictPeoples,
                        0 as adjustPeoples,
                        0 as status,
                        %s as insertTime,
                        %s as updateTime,
                        count(distinct order_no) as trueOrders,
                        0 as predictOrders,
                        0 as adjustOrders
                        from base_pos_df
                        where
                        cid=%s
                        and did=%s
                        and substr(gmt_bill,1,10)>=%s
                        and substr(gmt_bill,1,10)<=%s
                        and aistatus=1
                        group by cid, 
                        did,
                        concat(substr(gmt_bill,1,14),LPAD(15*floor(bill_minute/15),2,0));
                        """
            # infoLog.info('execute data sql %s :%s,%s,%s,%s,%s,%s ' % (sql, updateTime, updateTime, cid, did, sday,eday))
            cursor.execute(sql, (updateTime, updateTime, cid, did, sday, eday))  # 执行sql语句
            conn.commit()  # 提交到数据库执行
            infoLog.info('execute update save code:100')
            resultCode = 100

        except IntegrityError as e:
            infoLog.info(e)
        except InternalError as e:
            infoLog.info(e)
            time.sleep(6)
            infoLog.info('Repeat execute PosDBModel.updateView_min_max %s,%s,%s,%s ' % (cid, did, sday, eday))
            PosDBModel.updateView_min_max(cls, updateTime, cid, did, sday, eday)
        except OperationalError as e:
            infoLog.info(e)
            time.sleep(6)
            infoLog.info('Repeat execute PosDBModel.updateView_min_max %s,%s,%s,%s ' % (cid, did, sday, eday))
            PosDBModel.updateView_min_max(cls, updateTime, cid, did, sday, eday)
        except:
            tracebackLog.error('traceback.format_exc():%s', traceback.format_exc())
            # 如果发生错误则回滚
            conn.rollback()
            resultCode = 100
        finally:
            cursor.close()
            conn.close()
        return resultCode

    @classmethod
    def modifyForecast(cls, data_dict):
        result_code = 100
        conn = DBPOOL.connection()
        cursor = conn.cursor()
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        raw_sql = ''
        try:
            for forecast_type, data_arr in data_dict.items():
                if 'GMV' in forecast_type:
                    for d in data_arr:
                        raw_sql = """
                                    INSERT INTO view_pos_info_df (trueGMV,updateTime,predictGMV,adjustGMV,cid,
                                    shike,did,truePeoples,predictPeoples,adjustPeoples,trueOrders,
                                    predictOrders,adjustOrders,insertTime,status) 
                                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE 
                                    updateTime = %s, predictGMV = %s, adjustGMV = %s
                                """
                        cursor.execute(raw_sql, (0, now, d[1], d[2], d[3], d[4], d[5], 0, 0, 0, 0, 0, 0, now, 0,
                                                 now, d[1], d[2]))

                elif 'Orders' in forecast_type:
                    for d in data_arr:
                        raw_sql = """
                                    INSERT INTO view_pos_info_df (trueOrders,updateTime,predictOrders,adjustOrders,cid,
                                    shike,did,truePeoples,predictPeoples,adjustPeoples,trueGMV,
                                    predictGMV,adjustGMV,insertTime,status) 
                                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE 
                                    updateTime = %s, predictOrders = %s, adjustOrders = %s
                                """
                        cursor.execute(raw_sql, (0, now, d[1], d[2], d[3], d[4], d[5], 0, 0, 0, 0, 0, 0, now, 0,
                                                 now, d[1], d[2]))
                elif 'Peoples' in forecast_type:
                    for d in data_arr:
                        raw_sql = """
                                    INSERT INTO view_pos_info_df (truePeoples,updateTime,predictPeoples,adjustPeoples,cid,
                                    shike,did,trueGMV,predictGMV,adjustGMV,trueOrders,
                                    predictOrders,adjustOrders,insertTime,status) 
                                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE 
                                    updateTime = %s, predictPeoples = %s, adjustPeoples = %s
                                """
                        cursor.execute(raw_sql, (0, now, d[1], d[2], d[3], d[4], d[5], 0, 0, 0, 0, 0, 0, now, 0,
                                                 now, d[1], d[2]))
                infoLog.info(raw_sql)

        except IntegrityError as e:
            infoLog.info(e)
        except Exception as e:
            tracebackLog.error('traceback.format_exc():%s', traceback.format_exc())
            # 如果发生错误则回滚
            conn.rollback()
            result_code = 101
            return result_code

        conn.commit()
        cursor.close()
        conn.close()
        return result_code

    @classmethod
    def get_forecast_data(cls, cid, did, date, type, bid, time) -> float:
        """
        TODO: 取数
        :param cid: 公司id
        :param did: 部门id
        :param date: 'YYYY-mm-dd'形式的日期字符串
        :param type: 营业额turnover 或 交易笔数order_num
        :param bid:
        :param time: 形如'09:15'的时间字符串
        :return: 对应的预测值 浮点数
        """
        return 0.0

    @classmethod
    def get_base_pos_node(cls, cid, didArr, shike_list, selectPart) -> Dict[str, Dict[str, int]]:
        """
        :param cid:
        :param didArr:
        :param shike_list:
        :param selectPart:
        :return:
        """

        base_pos = {}

        sql = " select shike,sum(%s) as value  from  view_pos_df where cid=%s and did in (%s) and shike in (%s) and status=0 group by shike"

        conn = DBPOOL.connection()
        cursor = conn.cursor()

        sql2 = sql % (selectPart, cid, ','.join(list(map(lambda x: "'%s'" % x, didArr))),
                      ','.join(list(map(lambda x: "'%s'" % x, shike_list))))
        try:
            cursor.execute(sql, (selectPart, cid, ','.join(list(map(lambda x: "'%s'" % x, didArr))),
                                 ','.join(list(map(lambda x: "'%s'" % x, shike_list)))))
            infoLog.info('execute sql:%s' % (sql2))

            alldata = cursor.fetchall()
            for m in alldata:
                base_pos[m[0]] = float(m[1])

            conn.commit()
            cursor.close()
        except:
            tracebackLog.error('execute sql:%s' % sql2)
            tracebackLog.error('traceback.format_exc():%s', traceback.format_exc())
        conn.close()
        return base_pos

    @classmethod
    def get_base_pos_startend(cls, cid, didArr, startTime, endTime, selectPart):
        """

        :param cid:
        :param did:
        :param startTime:
        :param endTime:
        :param selectPart:
        :return:
        """

        pos = 0.0

        sql = " select sum(" + selectPart + ") as value  from  view_pos_df where cid=%s and did in (" + ','.join(
            list(map(lambda x: str(x), didArr))) + ") and shike >=%s and shike<%s and status=0 "
        print('sql', sql)
        conn = DBPOOL.connection()
        cursor = conn.cursor()

        sqlinfo = ''
        try:
            sqlinfo = (sql % (cid, startTime, endTime))

            infoLog.info('execute sql:%s' % (sqlinfo))

            cursor.execute(sql, (cid, startTime, endTime))

            alldata = cursor.fetchall()
            for m in alldata:
                pos = float(m[0])

            conn.commit()
            cursor.close()
        except:
            tracebackLog.error('execute sql:%s' % (sqlinfo))
            tracebackLog.error('traceback.format_exc():%s', traceback.format_exc())
        conn.close()
        return pos

    @classmethod
    def choose_data(cls, adjust_data, predict_data, true_data):
        if adjust_data != 0:
            return adjust_data
        elif predict_data != 0:
            return predict_data
        else:
            return true_data

    @classmethod
    def get_base_pos_startend_time(cls, cid, didArr, startTime, endTime, selectPart):
        """

        :param cid:
        :param did:
        :param startTime:
        :param endTime:
        :param selectPart:
        :return:
        """

        pos = {}
        origin_data = ['if(adjustGMV!=0, adjustGMV, if(predictGMV!=0,predictGMV,trueGMV))',
                       'if(adjustOrders!=0, adjustOrders, if(predictOrders!=0,predictOrders,trueOrders))',
                       'if(adjustPeoples!=0, adjustPeoples, if(predictPeoples!=0,predictPeoples,truePeoples))']

        # sql = " select shike,sum("+selectPart+") as value  from  view_pos_df where cid=%s and did in ("+','.join(list(map(lambda x:str(x),didArr)))+") and shike >=%s and shike<%s and status=0 group by shike"
        # sql = " select shike,adjustGMV, predictGMV, trueGMV, adjustOrders, predictOrders, trueOrders, adjustPeoples, predictPeoples, truePeoples from  view_pos_info_df where cid=%s and did in (" + ','.join(
        #     list(map(lambda x: str(x), didArr))) + ") and shike >=%s and shike<%s and status=0"

        sql = " select shike,adjustGMV, predictGMV, trueGMV, adjustOrders, predictOrders, trueOrders, adjustPeoples, predictPeoples, truePeoples from  view_pos_info_df where cid=%s and did in (" + ','.join(
            list(map(lambda x: str(x),
                     didArr))) + ") and shike >= str_to_date(%s, %s) and shike<str_to_date(%s, %s) and status=0"
        fmt = '%Y-%m-%d %H:%i:%s'

        conn = DBPOOL.connection()
        cursor = conn.cursor()

        sqlinfo = ''
        try:
            sqlinfo = (sql % (cid, startTime, fmt, endTime, fmt))
            infoLog.info('execute sql:%s' % (sqlinfo))
            cursor.execute(sql, (cid, startTime, fmt, endTime, fmt))

            alldata = cursor.fetchall()
            if len(alldata) != 0:
                df = pd.DataFrame(data=list(alldata),
                                  columns=["shike", "adjustGMV", "predictGMV", "trueGMV", "adjustOrders",
                                           "predictOrders",
                                           "trueOrders", "adjustPeoples", "predictPeoples", "truePeoples"])
                if selectPart == origin_data[0]:
                    df['GMV_apply'] = df.apply(lambda x: PosDBModel.choose_data(x.adjustGMV, x.predictGMV, x.trueGMV),
                                               axis=1)
                    value = df['GMV_apply'].groupby(df['shike']).sum().reset_index()
                elif selectPart == origin_data[1]:
                    df['Orders_apply'] = df.apply(
                        lambda x: PosDBModel.choose_data(x.adjustOrders, x.predictOrders, x.trueOrders), axis=1)
                    value = df['Orders_apply'].groupby(df['shike']).sum().reset_index()
                elif selectPart == origin_data[2]:
                    df['Peoples_apply'] = df.apply(
                        lambda x: PosDBModel.choose_data(x.adjustPeoples, x.predictPeoples, x.truePeoples), axis=1)
                    value = df['Peoples_apply'].groupby(df['shike']).sum().reset_index()

                for i in range(len(value)):
                    pos[value.iloc[i, 0]] = float(0 if value.iloc[i, 1] == '' else value.iloc[i, 1])

            # for m in alldata:
            #     pos[m[0]]=float(0 if m[1]=='' else  m[1])
            conn.commit()
            cursor.close()
        except:
            tracebackLog.error('execute sql:%s' % (sqlinfo))
            tracebackLog.error('traceback.format_exc():%s', traceback.format_exc())
        conn.close()
        return pos

    def predict2db(itemkeys, flied):
        """
        :param itemkeys
        :return:
        """
        conn = DBPOOL.connection()
        cursor = conn.cursor()
        sql = 'update view_pos_df set ' + flied + '=%s where cid=%s and did =%s and shike=%s'
        n = cursor.executemany(sql, itemkeys)

        conn.commit()
        conn.close()


if __name__ == '__main__':
    # a={'trueGMV': [('2020-03-06 15:08:07', 0.0, 0.0, '50000671', '2019-12-08 06:00', '62'), ('2020-03-06 15:08:07', 0.0, 0.0, '50000671', '2019-12-08 06:00', '62'),('2020-03-06 15:08:07', 0.0, 0.0, '50000671', '2019-12-08 06:15', '62'), ('2020-03-06 15:08:07', 0.0, 0.0, '50000671', '2019-12-08 06:30', '62'), ('2020-03-06 15:08:07', 0.0, 0.0, '50000671', '2019-12-08 06:45', '62'), ('2020-03-06 15:08:07', 0.0, 0.0, '50000671', '2019-12-08 07:00', '62'), ('2020-03-06 15:08:07', 0.0, 0.0, '50000671', '2019-12-08 07:15', '62'), ('2020-03-06 15:08:07', 0.0, 0.0, '50000671', '2019-12-08 07:30', '62'), ('2020-03-06 15:08:07', 0.0, 0.0, '50000671', '2019-12-08 07:45', '62'), ('2020-03-06 15:08:07', 287.25, 287.25, '50000671', '2019-12-08 08:00', '62'), ('2020-03-06 15:08:07', 287.25, 287.25, '50000671', '2019-12-08 08:15', '62'), ('2020-03-06 15:08:07', 287.25, 287.25, '50000671', '2019-12-08 08:30', '62'), ('2020-03-06 15:08:07', 287.25, 287.25, '50000671', '2019-12-08 08:45', '62'), ('2020-03-06 15:08:07', 2637.0, 2637.0, '50000671', '2019-12-08 09:00', '62'), ('2020-03-06 15:08:07', 2637.0, 2637.0, '50000671', '2019-12-08 09:15', '62'), ('2020-03-06 15:08:07', 2637.0, 2637.0, '50000671', '2019-12-08 09:30', '62'), ('2020-03-06 15:08:07', 2637.0, 2637.0, '50000671', '2019-12-08 09:45', '62'), ('2020-03-06 15:08:07', 2415.5, 2415.5, '50000671', '2019-12-08 10:00', '62'), ('2020-03-06 15:08:07', 2415.5, 2415.5, '50000671', '2019-12-08 10:15', '62'), ('2020-03-06 15:08:07', 2415.5, 2415.5, '50000671', '2019-12-08 10:30', '62'), ('2020-03-06 15:08:07', 2415.5, 2415.5, '50000671', '2019-12-08 10:45', '62'), ('2020-03-06 15:08:07', 2202.5, 2202.5, '50000671', '2019-12-08 11:00', '62'), ('2020-03-06 15:08:07', 2202.5, 2202.5, '50000671', '2019-12-08 11:15', '62'), ('2020-03-06 15:08:07', 2202.5, 2202.5, '50000671', '2019-12-08 11:30', '62'), ('2020-03-06 15:08:07', 2202.5, 2202.5, '50000671', '2019-12-08 11:45', '62'), ('2020-03-06 15:08:07', 1684.5, 1684.5, '50000671', '2019-12-08 12:00', '62'), ('2020-03-06 15:08:07', 1684.5, 1684.5, '50000671', '2019-12-08 12:15', '62'), ('2020-03-06 15:08:07', 1684.5, 1684.5, '50000671', '2019-12-08 12:30', '62'), ('2020-03-06 15:08:07', 1684.5, 1684.5, '50000671', '2019-12-08 12:45', '62'), ('2020-03-06 15:08:07', 1596.75, 1596.75, '50000671', '2019-12-08 13:00', '62'), ('2020-03-06 15:08:07', 1596.75, 1596.75, '50000671', '2019-12-08 13:15', '62'), ('2020-03-06 15:08:07', 1596.75, 1596.75, '50000671', '2019-12-08 13:30', '62'), ('2020-03-06 15:08:07', 1596.75, 1596.75, '50000671', '2019-12-08 13:45', '62'), ('2020-03-06 15:08:07', 1557.5, 1557.5, '50000671', '2019-12-08 14:00', '62'), ('2020-03-06 15:08:07', 1557.5, 1557.5, '50000671', '2019-12-08 14:15', '62'), ('2020-03-06 15:08:07', 1557.5, 1557.5, '50000671', '2019-12-08 14:30', '62'), ('2020-03-06 15:08:07', 1557.5, 1557.5, '50000671', '2019-12-08 14:45', '62'), ('2020-03-06 15:08:07', 1538.75, 1538.75, '50000671', '2019-12-08 15:00', '62'), ('2020-03-06 15:08:07', 1538.75, 1538.75, '50000671', '2019-12-08 15:15', '62'), ('2020-03-06 15:08:07', 1538.75, 1538.75, '50000671', '2019-12-08 15:30', '62'), ('2020-03-06 15:08:07', 1538.75, 1538.75, '50000671', '2019-12-08 15:45', '62'), ('2020-03-06 15:08:07', 2408.75, 2408.75, '50000671', '2019-12-08 16:00', '62'), ('2020-03-06 15:08:07', 2408.75, 2408.75, '50000671', '2019-12-08 16:15', '62'), ('2020-03-06 15:08:07', 2408.75, 2408.75, '50000671', '2019-12-08 16:30', '62'), ('2020-03-06 15:08:07', 2408.75, 2408.75, '50000671', '2019-12-08 16:45', '62'), ('2020-03-06 15:08:07', 2365.5, 2365.5, '50000671', '2019-12-08 17:00', '62'), ('2020-03-06 15:08:07', 2365.5, 2365.5, '50000671', '2019-12-08 17:15', '62'), ('2020-03-06 15:08:07', 2365.5, 2365.5, '50000671', '2019-12-08 17:30', '62'), ('2020-03-06 15:08:07', 2365.5, 2365.5, '50000671', '2019-12-08 17:45', '62'), ('2020-03-06 15:08:07', 1915.75, 1915.75, '50000671', '2019-12-08 18:00', '62'), ('2020-03-06 15:08:07', 1915.75, 1915.75, '50000671', '2019-12-08 18:15', '62'), ('2020-03-06 15:08:07', 1915.75, 1915.75, '50000671', '2019-12-08 18:30', '62'), ('2020-03-06 15:08:07', 1915.75, 1915.75, '50000671', '2019-12-08 18:45', '62'), ('2020-03-06 15:08:07', 2785.0, 2785.0, '50000671', '2019-12-08 19:00', '62'), ('2020-03-06 15:08:07', 2785.0, 2785.0, '50000671', '2019-12-08 19:15', '62'), ('2020-03-06 15:08:07', 2785.0, 2785.0, '50000671', '2019-12-08 19:30', '62'), ('2020-03-06 15:08:07', 2785.0, 2785.0, '50000671', '2019-12-08 19:45', '62'), ('2020-03-06 15:08:07', 2407.0, 2407.0, '50000671', '2019-12-08 20:00', '62'), ('2020-03-06 15:08:07', 2407.0, 2407.0, '50000671', '2019-12-08 20:15', '62'), ('2020-03-06 15:08:07', 2407.0, 2407.0, '50000671', '2019-12-08 20:30', '62'), ('2020-03-06 15:08:07', 2407.0, 2407.0, '50000671', '2019-12-08 20:45', '62'), ('2020-03-06 15:08:07', 1206.0, 1206.0, '50000671', '2019-12-08 21:00', '62'), ('2020-03-06 15:08:07', 1206.0, 1206.0, '50000671', '2019-12-08 21:15', '62'), ('2020-03-06 15:08:07', 1206.0, 1206.0, '50000671', '2019-12-08 21:30', '62'), ('2020-03-06 15:08:07', 1206.0, 1206.0, '50000671', '2019-12-08 21:45', '62'), ('2020-03-06 15:08:07', 399.25, 399.25, '50000671', '2019-12-08 22:00', '62'), ('2020-03-06 15:08:07', 399.25, 399.25, '50000671', '2019-12-08 22:15', '62'), ('2020-03-06 15:08:07', 399.25, 399.25, '50000671', '2019-12-08 22:30', '62'), ('2020-03-06 15:08:07', 399.25, 399.25, '50000671', '2019-12-08 22:45', '62')]}
    # PosDBModel.modifyForecast(a)

    # PosDBModel.getHistoryPos(cid='50000319',did='12',startPreDay='2019-11-01 00:00:00')
    cid = '123456'
    didArr = [14, 55]
    startTime = '2019-07-29 00:00'
    endTime = '2019-07-29 07:30'
    selectPart = 'if(adjustGMV!=0, adjustGMV, if(predictGMV!=0,predictGMV,trueGMV))'
    a = PosDBModel.get_base_pos_startend_time(cid, didArr, startTime, endTime, selectPart)
    print(a)

    b = PosDBModel.modifyForecast()
