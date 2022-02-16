# !/usr/bin/env python
# -*- coding:utf-8 -*-

import sys;

import pandas as pd
import numpy as np
from pandas import DataFrame
import json

from forecastPOS.model.posDB import PosDBModel
from utils.dateUtils import DateUtils
import traceback, datetime
from utils.myLogger import infoLog, tracebackLog
from forecastPOS.algorithm.prophet import ProphetForecast
from forecastPOS.algorithm.lstm import LstmForecast
from config.pos_auto_conf import PosAutoConfig
from tornado import gen
import threading
from utils.testDBPool import DBPOOL
from specialEvent.model.special_event_scope_model import SpecialEventScopeModel


# 需要xlwt库的支持
# import xlwt
# file = Workbook(encoding='utf-8')
# # 指定file以utf-8的格式打开
# table = file.add_sheet('data')
# # 指定打开的文件名
#
# data = {
#     "1": ["张三", 150, 120, 100],
#     "2": ["李四", 90, 99, 95],
#     "3": ["王五", 60, 66, 68]
# }
# # 字典数据
#
# ldata = []
# num = [a for a in data]
# # for循环指定取出key值存入num中
# num.sort()
# # 字典数据取出后无需，需要先排序
#
# for x in num:
#     # for循环将data字典中的键和值分批的保存在ldata中
#     t = [int(x)]
#     for a in data[x]:
#         t.append(a)
#     ldata.append(t)
#
# for i, p in enumerate(ldata):
#     # 将数据写入文件,i是enumerate()函数返回的序号数
#     for j, q in enumerate(p):
#         # print i,j,q
#         table.write(i, j, q)
# file.save('data.xlsx')

class PosDBService():
    def getBasePos(did, startBaseDay, startPreDay, preType, cycles, cycleLenth, fixDict, cid, historyPosData):
        """
        :param did 部门id
        :param startBaseDay base的历史数据的开始日期
        :param startPreDay 开始预测的日期

        :param preType ： 预测哪种数据

        :param cycles 预测的base数据周期数 用于reshape数据
        :param cycleLenth 周期长度

        :return:
        """
        startBaseDaySeq = pd.date_range(start=startBaseDay, periods=cycles * cycleLenth * 96, freq='15min').tolist()
        startBaseDayKey = list(map(lambda x: str(x)[0:16], startBaseDaySeq))
        if preType not in ['trueGMV', 'truePeoples', 'trueOrders']:
            return {}

        # 获取全部的历史数据
        # historydataDict = PosDBModel.getBasePos(did, startBaseDay, startPreDay, preType,cid)
        # print('historydataDict_all=',historydataDict)
        # 获取剔除特殊事件后的历史数据
        # historydataDict = PosDBService.getBasePosByNoEvents(did, startBaseDay, startPreDay, preType, cid)
        # print('historydataDict=', historydataDict)
        # 获取只包含特殊事件的历史数据
        # historydataDict = PosDBService.getBasePosByEvents(did, startBaseDay, startPreDay, preType, cid)
        # print('historydataDict=', historydataDict)

        # modified by caoyabin
        # historydataDict = PosDBModel.getBasePos(did, startBaseDay, startPreDay, preType,cid)
        historydataDict = historyPosData

        historydata = []

        for k in startBaseDayKey:
            historydata.append(fixDict.get(k, historydataDict.get(k, 0)))
        historyPD = np.array(historydata).reshape(cycles, 96 * cycleLenth)

        return historyPD

    @staticmethod
    def getHistoryPosData(did, startBaseDay, startPreDay, preType, cid):
        return PosDBModel.getBasePos(did, startBaseDay, startPreDay, preType, cid)

    @staticmethod
    def predictByProphet(cid,did, startPreDay, endPreDay, preType,data=None):
        """
        预测类型 1按周期预测 平均加权法 固定周期平均
        :param did:
        :param startPreDay: 预测开始时间
        :param endPreDay: 预测结束的时间
        :param preType:trueGmv 预测营业额    | truePeoples 预测人数
        :return:prophetDict key是未来一周的时刻 value是计算出来的值
        """

        """
        if preType == 'trueGmv':
            config = ProphetConfig.config_gmv
        else:
            config = ProphetConfig.config_people

        base_week = config['base_week']
        """

        startPreDaySeq = pd.date_range(start=startPreDay, end=endPreDay, freq='15min').tolist()
        startPreDayKey = list(map(lambda x: str(x)[0:16], startPreDaySeq))
        startPreDayKey = startPreDayKey[0:-1]

        pre_df = pd.DataFrame()
        pre_df['ds'] = pd.Series(startPreDayKey)

        prophet_forecast = ProphetForecast(cid, did, pre_df, preType)
        prophet_dict = {}
        pre_res = prophet_forecast.get_forecast_result()
        if pre_res is None:
            return prophet_dict
        num = 0
        for key in startPreDayKey:
            prophet_dict[key] = pre_res[num]
            num += 1

        return prophet_dict

    @classmethod
    def getBasePosByEvents(cls, did, start_base_day, start_pre_day, pre_type, cid):
        """
        获取(特殊事件)影响的参考的POS历史数据
        :param:did 部门id
        :param:start_base_day 预测参考的数据的历史数据开始时间，比如使用历史数据为（20190101）-20191001，预测20191002-20191007，则此处为20190101
        :param:start_pre_day 预测开始时间，比如使用历史数据为20190101-20191001，预测（20191002）-20191007，则此处为20191002
        :param:pre_type 预测类型 包含：trueGMV：GMV预测；truePeoples：客流量预测；trueOrders:订单量预测；
        :param:cid 部门cid
        :return:字典对象：history_data_dict；key:15分钟时间(e.g.:'2020-03-02 10:00')；value:此时刻对应的POS量比如（e.g.:（GMV）2301.5元）
        """
        return PosDBService.getBasePos_new(did, cid, start_base_day, start_pre_day, pre_type, 'include')

    @classmethod
    def getBasePosByNoEvents(cls, did, start_base_day, start_pre_day, pre_type, cid):
        """
        获取(剔除特殊事件)影响的参考的POS历史数据
        :param:did 部门id
        :param:start_base_day 预测参考的数据的历史数据开始时间，比如使用历史数据为（20190101）-20191001，预测20191002-20191007，则此处为20190101
        :param:start_pre_day 预测开始时间，比如使用历史数据为20190101-20191001，预测（20191002）-20191007，则此处为20191002
        :param:pre_type 预测类型包含：trueGMV：GMV预测；truePeoples：客流量预测；trueOrders:订单量预测；
        :param:cid 部门cid
        :return:字典对象：history_data_dict；key:15分钟时间(e.g.:'2020030210:00')；value:此时刻对应的POS量比如（e.g.:（GMV）2301.5元）
        """

        return PosDBService.getBasePos_new(did, cid, start_base_day, start_pre_day, pre_type, 'exclude')

    @classmethod
    def getBasePos_new(cls, did, cid, start_base_day, start_pre_day, pre_type, special_event_type):
        """
        获取POS历史数据
        :param:did 部门id
        :param:cid
        :param:start_base_day 预测参考的数据的历史数据开始时间，比如使用历史数据为（20190101）-20191001，预测20191002-20191007，则此处为20190101
        :param:start_pre_day 预测开始时间，比如使用历史数据为20190101-20191001，预测（20191002）-20191007，则此处为20191002
        :param:pre_type 预测类型 包含：trueGMV：GMV预测；truePeoples：客流量预测；trueOrders:订单量预测；
        :param:special_event_type 特殊事件类型 包含 include:仅含特殊事件影响的; exclude:仅含无特殊事件影响的； all：全部
        :return:字典对象：history_data_dict；key:15分钟时间(e.g.:'2020-03-02 10:00')；value:此时刻对应的POS量比如（e.g.:（GMV）2301.5元）
        """

        history_data_dict = {}
        start_time = start_base_day + ' 00:00'
        end_time = start_pre_day + ' 00:00'
        conn = DBPOOL.connection()
        with conn.cursor() as cursor:
            sql = """
                            SELECT
                                g.cid,
                                g.did,
                                g.shike,
                                g.goods_bid,
                                g.price,
                                g.true_gmv,
                                g.true_orders,
                                g.true_peoples
                            FROM
                                view_goods_df g
                            WHERE
                                g.STATUS = 1
                                AND g.shike>=%s
                                AND g.shike<%s
                                AND g.did = %s
                                AND g.cid = %s
                            """
            try:
                result_index = 5
                if pre_type == 'trueGMV':
                    result_index = 5
                elif pre_type == 'truePeoples':
                    result_index = 7
                elif pre_type == 'trueOrders':
                    result_index = 6
                cursor.execute(sql, (start_time, end_time, did, cid))
                results = cursor.fetchall()

                if special_event_type == 'include':  # 只考虑包含特殊事件的
                    goods_ids = SpecialEventScopeModel.get_goods_ids(cid, did, start_time, end_time)
                    for one in results:
                        if str(one[3]) in goods_ids:
                            history_data_dict[one[2]] = one[result_index]

                elif special_event_type == 'exclude':  # 只考虑排除特殊事件的
                    goods_ids = SpecialEventScopeModel.get_goods_ids(cid, did, start_time, end_time)
                    print('特殊商品bid', goods_ids)
                    print('results=', results)
                    for one in results:
                        print('str(one[3])=', str(one[3]))
                        if str(one[3]) not in goods_ids:
                            history_data_dict[one[2]] = one[result_index]

                else:  # 不考虑特殊事件 全取出
                    for one in results:
                        history_data_dict[one[2]] = one[result_index]
            except Exception:
                conn.rollback()
        conn.close()
        return history_data_dict
    @classmethod
    def extendPreday(cls,type1, did, startPreDay, preType, cycleLenth, cycles, cyclesCoef, endPreDay, smoothCoef, iswoqu,
                     cid, historyPosData):
        """
        :return:
        """
        resultDict = {}
        preDayKey = list(
            map(lambda x: str(x)[0:16], pd.date_range(start=startPreDay, end=endPreDay, freq='15min').tolist()))[0:-1]

        fixDict = {}

        startDay = startPreDay
        endDay = '1991-01-01'

        if cycles != len(cyclesCoef):
            cyclesCoef = np.zeros((1, cycles))[0].tolist()

        while endDay < endPreDay:
            endDay = DateUtils.nDatesAgo(startDay, -7)  # 7天后

            if type1 == 'avgm':
                smoothCoef = 1
                fixDict = PosDBService.predictByAvg(did, startDay, preType, cycleLenth, cycles, cyclesCoef, endDay,
                                                    fixDict, smoothCoef, iswoqu, cid, historyPosData)
            else:
                cyclesCoef = np.zeros((1, cycles))[0].tolist()
                fixDict = PosDBService.predictByAvg(did, startDay, preType, cycleLenth, cycles, cyclesCoef, endDay,
                                                    fixDict, smoothCoef, iswoqu, cid, historyPosData)

            for k, v in fixDict.items():
                if k in preDayKey:
                    resultDict[k] = v

            startDay = endDay
            cycles = cycles - 1
            cyclesCoef = cyclesCoef[1:]
            cyclesCoef.append(0)
        return resultDict

    def predictByAvg(did, startPreDay, preType, cycleLenth, cycles, cyclesCoef, endPreDay, fixDict, smoothCoef, iswoqu,
                     cid, historyPosData):
        """
        预测类型 1按周期预测 平均加权法 固定周期平均
        :param startPreDay:
        :param endPreDay:
        :param preType:
        :param cycleLenth:周期长度
        :param cycles:
        :param cyclesCoef:
        :return:avgfixDict key是未来一周的时刻 value是计算出来的值
        """
        cycleLenth = 7
        if cycles == 0:
            cycles = 1
            cyclesCoef = [0]
        startBaseDay = DateUtils.nDatesAgo(startPreDay, cycles * cycleLenth)
        # 计算
        cyclesCoefP = list(map(lambda x: x + 1, cyclesCoef))

        # 获取历史POS量
        baseValue = PosDBService.getBasePos(did, startBaseDay, startPreDay, preType, len(cyclesCoef), cycleLenth,
                                            fixDict, cid, historyPosData)

        # 根据历史POS量计算当前POS量
        avgfixList = []
        if iswoqu:
            avgPD = pd.DataFrame(baseValue).mul(cyclesCoefP, axis=0).sum() / len(cyclesCoef)
            avgfixList = list(pd.DataFrame(avgPD.values.T)[0])
        else:
            historyPD = pd.DataFrame(baseValue).T
            historyPD['n0'] = (historyPD != 0).sum(axis=1)
            historyPD['sumt'] = historyPD.drop('n0', axis=1).T.mul(cyclesCoefP, axis=0).apply(sum)
            historyPD['avgp'] = (historyPD['sumt'] / historyPD['n0']).fillna(0)
            avgfixList = list(pd.DataFrame(historyPD['avgp'].values.T)[0])
        startPreDaySeq = pd.date_range(start=startPreDay, end=endPreDay, freq='15min').tolist()
        startPreDaySeq = startPreDaySeq[0:-1]
        startPreDayKey = list(map(lambda x: str(x)[0:16], startPreDaySeq))
        avgfixDict = {}

        for i, m in enumerate(startPreDayKey):
            avgfixDict[m] = round(avgfixList[i] * smoothCoef)
        return avgfixDict

    def predictBySmoothFix(did, startPreDay, preType, cycleLenth, cycles, smoothCoef, endPreDay, fixDict, cid):
        """
        预测类型 固定周期平均 平滑指数法
        :param startPreDay:
        :param preType:
        :param cycleLenth: 周期长度
        :param cycles: 查看的base数据的周期数
        :param smoothCoef:平滑常数
        :return:
        """
        startBaseDay = DateUtils.nDatesAgo(startPreDay, cycles * cycleLenth)

        # 获取历史数据
        historyPosData = PosDBService.getHistoryPosData(did, startBaseDay, endPreDay, preType, cid)
        historyPD = PosDBService.getBasePos(did, startBaseDay, startPreDay, preType, cycles, cycleLenth, fixDict, cid,
                                            historyPosData)

        smoothfixPD = (pd.DataFrame(historyPD).sum() / cycles) * (1 + 1 - smoothCoef)
        smoothfixList = list(pd.DataFrame(smoothfixPD.values.T)[0])

        startPreDaySeq = pd.date_range(start=startPreDay, end=endPreDay, freq='15min').tolist()
        startPreDaySeq = startPreDaySeq[0:-1]
        startPreDayKey = list(map(lambda x: str(x)[0:16], startPreDaySeq))
        smoothfixDict = {}
        for i, m in enumerate(startPreDayKey):
            smoothfixDict[m] = round(smoothfixList[i])

        return smoothfixDict

    def mergeData(avgDict, smoothDict, deepDict, prophetDict, seq2seqDict, startPreDay, endPreDay):
        """
        四种预测算法做等权平均，获取不到取平均那值
        :param avgData,smoothData,spatialTemporalData,modelData: 四种预测方式预测的结果数据
        :return:
        """

        startPreDaySeq = pd.date_range(start=startPreDay, end=endPreDay, freq='15min').tolist()
        startPreDayKey = list(map(lambda x: str(x)[0:16], startPreDaySeq))

        predictData = {}
        for k in startPreDayKey:
            predictData[k] = avgDict.get(k, 0) * 1 / 5 + smoothDict.get(k, 0) * 1 / 5 + deepDict.get(k,
                                                                                                     0) * 1 / 5 + prophetDict.get(
                k, 0) * 1 / 5 + seq2seqDict.get(k, 0) * 1 / 5
        return predictData

    def tuncDict(sDict):
        '''
        给出值以及范围
        :return:
        '''
        rDict = {}

        for k, v in sDict.items():
            rDict[k] = {'value': v, 'scope': [round(v * 0.9, 2), round(v * 1.1, 2)]}
        return rDict

    def fmt_fcst_ForLSTM(startPreDay, endPreDay):
        date_list = []
        startPreDay = datetime.datetime.strptime(startPreDay, '%Y-%m-%d')
        endPreDay = datetime.datetime.strptime(endPreDay, '%Y-%m-%d')
        date_list = [x.strftime('%Y-%m-%d %H:00:00') for x in list(pd.date_range(start=startPreDay, freq='1h',
                                                                                 end=endPreDay + datetime.timedelta(
                                                                                     days=0) + datetime.timedelta(
                                                                                     hours=-1)))]
        c = {"rdate": date_list}
        data = DataFrame(c)
        return data

    def fByLSTM(cid, did, pre_df, fcst_df):
        rDict = {}
        lstm_forecast = LstmForecast(cid, did, pre_df, fcst_df)
        df_lstm_r = lstm_forecast.get_forecast_result()
        df_lstm_list = np.array(df_lstm_r).tolist()
        for i in df_lstm_list:
            if i[1] != 0:
                rDict[i[0].strftime("%Y-%m-%d %H:%M")] = i[1]
        return rDict

    def fmtForLSTM(cid, did, endPreDay):
        # 读取历史数据，view生成的df， 需要从数据库读出（ 比如人家要的是营业额或者是订单量或者是客流量）
        historyData = PosDBModel.getHistoryPos(cid, did, endPreDay)
        return historyData



    def set0(sDict, historydataDict):

        for k in sDict.keys():
            if k in historydataDict.keys() and historydataDict[k] == 0:
                sDict[k] = 0
        return sDict

    def setAdjust(sDict, adjustDict):

        for k in adjustDict:
            if k in sDict:
                sDict[k] = adjustDict[k]
        return sDict

    def pushData(raw_data):
        '''
        向数据库插入数据
        :param raw_data 前端数据
        :return:
        '''
        saveResult = {}

        data = []
        cid = raw_data.get('cid', '')
        companyName = raw_data.get('companyName', '')

        insertTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updateTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for v in raw_data.get('data', ''):
            did = v.get('did', '')
            gmtBill = v.get('gmtBill', '')
            gmtTurnover = v.get('gmtTurnover', '')
            money = v.get('money', '0')
            money = float(money)
            data_value = v.get('money', '').replace('.', '0')
            data_value = int(data_value)
            peoples = v.get('peoples', '0')
            peoples = int(peoples)
            singleSales = v.get('singleSales', '0')
            singleSales = int(singleSales)
            payment = v.get('payment', '')
            deviceCode = v.get('deviceCode', '')
            orderNo = v.get('orderNo', '')

            bill_year = int(gmtBill[0:4])
            bill_month = int(gmtBill[5:7])
            bill_day = int(gmtBill[8:10])
            bill_hour = int(gmtBill[11:13])
            bill_minute = int(gmtBill[14:16])

            data.append((cid, companyName, did, gmtBill, gmtTurnover, money, data_value, peoples, singleSales, payment,
                         deviceCode, orderNo, insertTime, updateTime, 1, bill_year, bill_month, bill_day, bill_hour,
                         bill_minute))
        infoLog.info('pushData - start:%s' % data)

        resultCode = PosDBModel.pushData(data)

        try:
            if resultCode == 100:
                saveResult['code'] = resultCode
                saveResult['result'] = '存储成功'
            elif resultCode == 101:
                saveResult['code'] = resultCode
                saveResult['result'] = 'DB操作错误'
            infoLog.info('pushData saveResult:%s' % saveResult)

        except Exception as e:

            tracebackLog.error('traceback.format_exc():%s', traceback.format_exc())

            saveResult['code'] = resultCode
            saveResult['result'] = '其他未知错误'

        finally:
            return saveResult

    def updateView(view_times):
        s = datetime.datetime.now()
        updatetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sday = ''
        eday = '1991-01-01'
        for view_time in view_times:
            cid, did, day = view_time.split('_')
            if day <= sday:
                sday = day
            if day >= eday:
                eday = day
        infoLog.info('PosDBModel.updateView_min_max :%s %s %s %s %s' % (updatetime, cid, did, sday, eday))
        resultCode = PosDBModel.updateView_min_max(updatetime, cid, did, sday, eday)

        e = datetime.datetime.now()
        infoLog.info('updateView_单次执行:' + str((e - s).seconds))
        return resultCode

    @classmethod
    def fmtData(cls, cid, updateTime, v):
        did = v.split(",", -1)[0]
        gmtBill = v.split(",", -1)[1]
        gmtTurnover = v.split(",", -1)[2]
        # if v.split(",", -1)[3]='':
        money = v.split(",", -1)[3] if v.split(",", -1)[3] != '' else '0'
        try:
            money = float(money)
        except:
            money = 0

        data_value = money * 100
        transaction_num = v.split(",", -1)[4] if v.split(",", -1)[4] != '' else '0'
        peoples = v.split(",", -1)[5] if v.split(",", -1)[5] != '' else '0'

        singleSales = v.split(",", -1)[6] if v.split(",", -1)[6] != '' else '0'
        commodity_code = v.split(",", -1)[7]

        try:
            data_value = int(data_value)
        except:
            data_value = 0

        try:
            peoples = int(peoples)
        except:
            peoples = 0

        try:
            singleSales = int(singleSales)
        except:
            singleSales = 0

        try:
            transaction_num = int(transaction_num)
        except:
            transaction_num = 0

        payment = v.split(",", -1)[8]
        deviceCode = v.split(",", -1)[9]
        orderNo = v.split(",", -1)[10]

        bill_year = int(gmtBill[0:4])
        bill_month = int(gmtBill[5:7])
        bill_day = int(gmtBill[8:10])
        bill_hour = int(gmtBill[11:13])
        bill_minute = int(gmtBill[14:16])

        s = "updateTime='%s'" % updateTime

        if 'money' in v:
            s += ",money='%s'" % money
            s += ",data_value=%s" % data_value
        if 'transaction_num' in v:
            s += ",transaction_num=%s" % transaction_num
        if 'peoples' in v:
            s += ",peoples=%s" % peoples
        if 'singleSales' in v:
            s += ",singleSales=%s" % singleSales
        if 'commodity_code' in v:
            s += ",commodity_code='%s'" % commodity_code
        if 'payment' in v:
            s += ",payment='%s'" % payment
        if 'deviceCode' in v:
            s += ",deviceCode='%s'" % deviceCode
        if 'orderNo' in v:
            s += ",order_no='%s'" % orderNo

        items = [(cid, did, gmtBill, gmtTurnover, money, data_value, transaction_num, peoples,
                  singleSales, commodity_code, payment, deviceCode, orderNo, updateTime, updateTime, 1,
                  bill_year, bill_month, bill_day, bill_hour, bill_minute)]

        return did, gmtBill, items, s

    @classmethod
    def fmtData1(cls, cid, updateTime, v):
        did = v.get('did', '')
        gmtBill = v.get('gmtBill', '')

        gmtTurnover = v.get('gmtTurnover', '')
        money = v.get('money', '0')
        try:
            money = float(money)
        except:
            money = 0

        data_value = float(v.get('money', 0)) * 100
        transaction_num = v.get('transactionNum', 0)
        peoples = v.get('peoples', '0')

        singleSales = v.get('singleSales', '0')
        commodity_code = v.get('commodityCode', '')

        try:
            data_value = int(data_value)
        except:
            data_value = 0

        try:
            peoples = int(peoples)
        except:
            peoples = 0

        try:
            singleSales = int(singleSales)
        except:
            singleSales = 0

        try:
            transaction_num = int(transaction_num)
        except:
            transaction_num = 0

        payment = v.get('payment', '')
        deviceCode = v.get('deviceCode', '')
        orderNo = v.get('orderNo', '')

        bill_year = int(gmtBill[0:4])
        bill_month = int(gmtBill[5:7])
        bill_day = int(gmtBill[8:10])
        bill_hour = int(gmtBill[11:13])
        bill_minute = int(gmtBill[14:16])

        s = "updateTime='%s'" % updateTime

        if 'money' in v:
            s += ",money='%s'" % money
            s += ",data_value=%s" % data_value
        if 'transaction_num' in v:
            s += ",transaction_num=%s" % transaction_num
        if 'peoples' in v:
            s += ",peoples=%s" % peoples
        if 'singleSales' in v:
            s += ",singleSales=%s" % singleSales
        if 'commodity_code' in v:
            s += ",commodity_code='%s'" % commodity_code
        if 'payment' in v:
            s += ",payment='%s'" % payment
        if 'deviceCode' in v:
            s += ",deviceCode='%s'" % deviceCode
        if 'orderNo' in v:
            s += ",order_no='%s'" % orderNo

        items = [(cid, did, gmtBill, gmtTurnover, money, data_value, transaction_num, peoples,
                  singleSales, commodity_code, payment, deviceCode, orderNo, updateTime, updateTime, 1,
                  bill_year, bill_month, bill_day, bill_hour, bill_minute)]

        return did, gmtBill, items, s

    @classmethod
    @gen.coroutine
    def modifyData(cls, raw_data):
        """
        修改POS数据
        :param raw_data 前端数据
        :return:
        """

        saveResult = {}
        cid = raw_data.get('cid', '')

        updateTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        view_times = set()
        update_i = []

        # 11,2019-05-16 12:03:22,2019-05-16 12:03:33,280.00,13,3,80,SPA01,现金,A1,002847306ac359f6016ac3cdd4c10368","13,2019-06-16 12:05:22,2019-05-20 12:03:33,280.00,13,3,80,SPA01,现金,A1,002847306ac359f6016ac3cdd1111111"

        for v in raw_data.get('datas', ''):
            did, gmtBill, items, s = PosDBService.fmtData(cid, updateTime, v)
            update_i.append([cid, did, gmtBill, items, s])  # 更新pos明细记录
            view_time = gmtBill[0:10]
            view_times.add('%s_%s_%s' % (cid, did, view_time))  # 更新view 需要信息 沃尔玛 1号店 2019-12-01

        s = datetime.datetime.now()
        resultCode = PosDBModel.modify_update_i(update_i)  # 1000 数组

        e = datetime.datetime.now()
        infoLog.info('modify_update_pos: ' + str((e - s).seconds))
        resultCode = PosDBService.updateView(view_times)  # 数组
        e1 = datetime.datetime.now()
        infoLog.info('modify_update_view: ' + str((e1 - s).seconds))

        try:
            saveResult['code'] = resultCode
            if resultCode == 100:
                saveResult['code'] = resultCode
                if resultCode == 100:
                    saveResult['result'] = '更新成功'
                elif resultCode == 103:
                    saveResult['result'] = '更新pos成功，但是更新view表失败'
            elif resultCode == 101:
                saveResult['result'] = 'DB操作错误'
            elif resultCode == 102:
                saveResult['result'] = 'DB更新错误'
            infoLog.info('modifyData saveResult:%s' % saveResult)

        except Exception as e:

            tracebackLog.error('traceback.format_exc():%s', traceback.format_exc())

            saveResult['code'] = 400
            saveResult['result'] = '其他未知错误'

        finally:
            raise gen.Return(saveResult)

    @classmethod
    @gen.coroutine
    def modifyData1(cls, raw_data):
        """
        修改POS数据
        :param raw_data 前端数据
        :return:
        """

        saveResult = {}
        cid = raw_data.get('cid', '')

        updateTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        view_times = set()
        update_i = []

        for v in raw_data.get('data', ''):
            did, gmtBill, items, s = PosDBService.fmtData1(cid, updateTime, v)
            update_i.append([cid, did, gmtBill, items, s])
            view_time = gmtBill[0:10]
            view_times.add('%s_%s_%s' % (cid, did, view_time))

        s = datetime.datetime.now()
        resultCode = PosDBModel.modify_update_i(update_i)
        e = datetime.datetime.now()
        infoLog.info('modify_update_pos: ' + str((e - s).seconds))
        resultCode = PosDBService.updateView(view_times)
        e1 = datetime.datetime.now()
        infoLog.info('modify_update_view: ' + str((e1 - s).seconds))

        try:
            saveResult['code'] = resultCode
            if resultCode == 100:
                saveResult['code'] = resultCode
                if resultCode == 100:
                    saveResult['result'] = '更新成功'
                elif resultCode == 103:
                    saveResult['result'] = '更新pos成功，但是更新view表失败'
            elif resultCode == 101:
                saveResult['result'] = 'DB操作错误'
            elif resultCode == 102:
                saveResult['result'] = 'DB更新错误'
            infoLog.info('modifyData saveResult:%s' % saveResult)

        except Exception as e:

            tracebackLog.error('traceback.format_exc():%s', traceback.format_exc())

            saveResult['code'] = 400
            saveResult['result'] = '其他未知错误'

        finally:
            raise gen.Return(saveResult)

    def getFactDid(did, startPreDay, preType, cid):
        """
        获取每家门店前一天的POS总量，用于得到该门店的实际did
        :param startPreDay:
        :param preType:
        :return:
        """

        factDid = 6
        yesDay = DateUtils.nDatesAgo(startPreDay, 1)  # 前一天的pos量
        yesPos = PosDBModel.getBasePos(did, yesDay, startPreDay, preType, cid)
        yesSumPos = 0
        for i in yesPos.values():
            yesSumPos += float(i)
        for d in [6, 14, 49, 58, 16, 44, 52, 47, 50, 15, 48, 57]:
            d_yesPos = PosDBModel.getBasePos(d, yesDay, startPreDay, preType, cid)
            d_yesSumPos = 0
            for j in d_yesPos.values():
                d_yesSumPos += float(j)

            if d_yesSumPos == yesSumPos:
                factDid = d
                break
        return factDid
    @classmethod
    @gen.coroutine
    def predictProcess(cls,predictParam):
        """
        实现预测算法
        :param predictParam: 参数
        :return:
        """

        predictType = predictParam.get('predictType', 'WEEK')
        cid = predictParam.get('cid', '123456')
        did = predictParam.get('did', '')
        startPreDay = predictParam.get('startDay', '')

        endPreDay = predictParam.get('endDay', '')
        endPreDay = DateUtils.nDatesAgo(endPreDay, -1)
        # caoyabin '' -> 7
        cycleLenth = predictParam.get('dayCount', 7)
        cycles = 100
        preType = predictParam.get('preType', 'truePeoples')
        smoothCoef = predictParam.get('smoothCoef', 0.9)
        cyclesCoef = predictParam.get('cyclesCoef', np.zeros((1, cycles))[0].tolist())
        avgDict = {}
        smoothDict = {}
        deepDict = {}
        prophetDict = {}
        seq2seqDict = {}

        # 根据POS量确定参照哪家门店的模型
        # did_req=PosDBService.getFactDid(did,startPreDay,preType,cid)
        did_req = did
        infoLog.info("请求的did是: %s ,参照的did: %s" % (str(did), str(did_req)))

        # 获取灵活的模型参数
        coffDict = PosAutoConfig.config_coffDict

        # modified by caoyabin
        avgCycles = cycles
        deepCycles = coffDict.get('%s_deepDict_%d' % (preType.lower(), did), [30, 1])[0]
        startBaseDay = DateUtils.nDatesAgo(startPreDay, max([avgCycles, deepCycles]) * cycleLenth)
        historyPosData = PosDBService.getHistoryPosData(did, startBaseDay, endPreDay, preType, cid)

        s = datetime.datetime.now()
        if predictType != '这个字段没什么用WEEK':
            iswoqu = True
            avgDict = PosDBService.extendPreday('avgm', did_req, startPreDay, preType, cycleLenth, cycles, cyclesCoef,
                                                endPreDay, smoothCoef, iswoqu, cid, historyPosData)
            # smoothDict = PosDBService.extendPreday('smooth' , did_req, startPreDay, preType, cycleLenth, cycles,cyclesCoef,endPreDay,smoothCoef,iswoqu)
            smoothDict = avgDict
            iswoqu = False
            cycles, smoothCoef = coffDict.get('%s_deepDict_%d' % (preType.lower(), did), [30, 1])
            if str(cid) == '50000671':  # 沃尔玛
                cycles = 2
            # elif str(cid) == '50000319':  # 西少爷
            #     cycles = 18
            elif str(cid) == '50000735' and str(did) == '12':  # 喜茶 12
                cycles = 17
            elif str(cid) == '50000735' and str(did) == '22':  # 喜茶 22
                cycles = 16
            infoLog.info("cycles :%s ，cid:%s ,did:%s" % (cycles, str(cid), str(did)))
            if str(cid) == '50000319':
                pre_df = PosDBService.fmtForLSTM(cid, did, startPreDay)
                fcst_df = PosDBService.fmt_fcst_ForLSTM(startPreDay, endPreDay)
                deepDict = PosDBService.fByLSTM(cid, did, pre_df, fcst_df)
            else:
                deepDict = PosDBService.extendPreday('avgm', did_req, startPreDay, preType, cycleLenth, cycles,
                                                     cyclesCoef, endPreDay, smoothCoef, iswoqu, cid, historyPosData)
                #prophetDict = PosDBService.predictByProphet(did, startBaseDay, startPreDay, preType)


        """
            cycles, smoothCoef = coffDict.get('%s_prophetDict_%d' % (preType.lower(), did), [30, 1])
            prophetDict = PosDBService.extendPreday('avgm', did_req, startPreDay, preType, cycleLenth, cycles, cyclesCoef,endPreDay, smoothCoef, iswoqu)

            cycles, smoothCoef = coffDict.get('%s_seq2seqDict_%d' % (preType.lower(), did), [30, 1])
            seq2seqDict = PosDBService.extendPreday('avgm', did_req, startPreDay, preType, cycleLenth, cycles, cyclesCoef,endPreDay, smoothCoef, iswoqu)

        #获取有手动修改的POS值,update结果
        adjustDict=PosDBModel.getAdjustPos(did_req,startPreDay,DateUtils.nDatesAgo(endPreDay,-1),preType)

        deepDict=PosDBService.setAdjust(deepDict,adjustDict)
        prophetDict = PosDBService.setAdjust(prophetDict, adjustDict)
        seq2seqDict = PosDBService.setAdjust(seq2seqDict, adjustDict)
        """

        prophetDict = deepDict
        seq2seqDict = deepDict
        predictData = {
            'avgDict': PosDBService.tuncDict(avgDict),
            'smoothDict': PosDBService.tuncDict(smoothDict),
            'deepDict': PosDBService.tuncDict(deepDict),
            'prophetDict': PosDBService.tuncDict(prophetDict),
            'seq2seqDict': PosDBService.tuncDict(seq2seqDict)
        }

        starttime = datetime.datetime.now()
        print('start', (starttime - s).seconds)
        t = threading.Thread(target=PosDBService.savePredict, args=(preType, predictData.get('deepDict'), cid, did))
        t.start()
        endtime = datetime.datetime.now()
        print('end', (endtime - starttime).seconds)

        raise gen.Return(predictData)
        # print('11111'+predictData)
    @classmethod
    def savePredict(cls,preType, dict, cid, did):
        s = datetime.datetime.now()
        data_arr = []
        # if preType =
        preType = preType.replace('true', '')
        updatetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for i, v in dict.items():
            if v.get('value') != 0:
                data_arr.append([updatetime, v.get('value'), v.get('value'), cid, i, did])

        data_dict = {preType: data_arr}
        PosDBModel.modifyForecast(data_dict)
        infoLog.info(data_arr)
        e = datetime.datetime.now()
        m = 'DB save %s 条' % (str(len(data_arr)))
        infoLog.info(m)
        infoLog.info((e - s).seconds)

    @gen.coroutine
    def modifyForecast(params):
        '''
        timestr;
        token;
        cid: "123456"
        didArr: [6,7]
        changedDataArr:
            forecastDate: "2017-01-02"
            startTimeStr: "00:15"
            endTimeStr: "00:30"
            forecastType: "trueGMV/trueOrders/truePeoples";
            forecastPosValue: "0.0"
            changedPosValue: "150.00"
        '''
        save_result = {}
        cid = params.get('cid', '')
        did_arr = params.get('didArr', [])
        # did_str = tuple(did_arr)

        changed_data_arr = params.get('changedDataArr', [])
        did_num = len(did_arr)
        #  cid, did, shike, forecastType, forecastPosValue, changedPosValue
        #  return dic_arr and execute sql for each dict
        data_dict = {}
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for data in changed_data_arr:
            data_arr = []
            forecast_date = data.get('forecastDate', '')
            start_time_str = data.get('startTimeStr', '')
            end_time_str = data.get('endTimeStr', '')
            forecast_type = data.get('forecastType', '')
            forecast_pos_value = eval(data.get('forecastPosValue', '0.0'))
            changed_pos_value = eval(data.get('changedPosValue', '0.0'))

            start_hour, start_minute = int(start_time_str[:2]), int(start_time_str[-2:]) // 15 * 15

            if datetime.datetime.strptime(end_time_str, "%H:%M").time() > datetime.datetime.strptime(start_time_str,
                                                                                                     "%H:%M").time():
                start_str = forecast_date + ' ' + str(start_hour).zfill(2) + ':' + str(start_minute).zfill(2)
                end_hour, end_minute = int(end_time_str[:2]), int(end_time_str[-2:]) // 15 * 15
                end_str = forecast_date + ' ' + str(end_hour).zfill(2) + ':' + str(end_minute).zfill(2)
            else:
                start_str = forecast_date + ' ' + str(start_hour).zfill(2) + ':' + str(start_minute).zfill(2)
                end_hour, end_minute = int(end_time_str[:2]), int(end_time_str[-2:]) // 15 * 15
                forecast_date = datetime.datetime.strptime(str(forecast_date), "%Y-%m-%d").date()
                date = forecast_date + datetime.timedelta(days=1)
                end_str = str(date) + ' ' + str(end_hour).zfill(2) + ':' + str(end_minute).zfill(2)

            start_time = datetime.datetime.strptime(str(start_str), "%Y-%m-%d %H:%M")
            end_time = datetime.datetime.strptime(str(end_str), "%Y-%m-%d %H:%M")
            shike_str_arr = []
            time_delta = 15
            while start_time <= end_time:
                start_time_str = start_time.strftime("%Y-%m-%d %H:%M")
                shike_str_arr.append(start_time_str)
                start_time += datetime.timedelta(minutes=time_delta)
            if end_time_str[-2:] in ['00', '15', '30', '45']:
                shike_str_arr.pop()
            shike_num = len(shike_str_arr)
            for shike in shike_str_arr:
                for did in did_arr:
                    temp = (now,
                            float(round(forecast_pos_value, 2) / (did_num * shike_num)),
                            float(round(changed_pos_value, 2) / (did_num * shike_num)),
                            str(cid),
                            shike,
                            str(did))
                    data_arr.append(temp)

            if forecast_type not in data_dict:
                data_dict[forecast_type] = []
            data_dict[forecast_type] = data_dict[forecast_type] + data_arr

        result_code = PosDBModel.modifyForecast(data_dict)

        try:
            if result_code == 100:
                save_result['code'] = result_code
                save_result['result'] = '存储成功'
            elif result_code == 101:
                save_result['code'] = result_code
                save_result['result'] = 'DB操作错误'
            infoLog.info('modifyForecast saveResult:%s' % save_result)

        except Exception as e:

            tracebackLog.error('traceback.format_exc():%s', traceback.format_exc())
            save_result['code'] = 400
            save_result['result'] = '其他未知错误'

        finally:
            raise gen.Return(save_result)


if __name__ == '__main__':
    data = {"token": "fb3ef8e49f622413d96713c75c371649", "timestr": "2020-05-09 09:37:48.721999","preType":"trueGMV","startDay":"2019-11-01","predictType":"CUSTOM","endDay":"2019-11-03","did":4954,"cid":50000031}
    result = PosDBService.predictProcess(data)
    print(result)
