#!/usr/bin/env python
# encoding: utf-8

"""
@author: lynnlidan
@contact: lynnlidan@didiglobal.com
@file: labor_db_service.py
@time: 2019-08-16 18:37
@desc:
"""

import logging,json
from typing import List, Dict, Union, Tuple
from datetime import datetime, timedelta

from labor.model.labor_standard_db import LaborStandard
from forecastPOS.model.posDB import PosDBModel
from utils.myLogger import infoLog, tracebackLog
from tornado import gen
import threading
import requests


class LaborDbService:

    @classmethod
    def write_labor_standard_push_into_db(cls, bid, cid, mode, masterType, slaveType, detailArr) -> int:
        """
        依次写库 insert
        :param bid:
        :param cid:
        :param did:
        :param mode:
        :param masterType:
        :param slaveType:
        :param detailArr:
        :return:
        """
        total_num = 0
        failed_num = 0
        for detail in detailArr:
            total_num += 1
            detailRank = detail['detailRank']
            masterTypeScale = detail['masterTypeScale']
            worktimeMinute = detail['worktimeMinute']
            masterTypeMinScale = detail["masterTypeMinScale"]
            slaveTypeScale = detail.get("slaveTypeScale", '')
            slaveTypeMinScale = detail.get("slaveTypeMinScale",'')
            res = LaborStandard.insert_record(bid, cid, mode, masterType, slaveType, detailRank, masterTypeScale,slaveTypeScale, worktimeMinute, 1,masterTypeMinScale,slaveTypeMinScale)
            if not res:
                failed_num += 1
        if total_num:
            logging.info('write labor standard push into db total: %s, success: %s, failed: %s', str(total_num),str(total_num - failed_num), str(failed_num))

        if not failed_num:
            return 0  # 无错误发生
        elif failed_num < total_num:
            return 1  # 有错误发生
        else:
            return 2  # 全部错误

    @classmethod
    def delete_labor_standard(cls, bid, cid) -> int:
        """
        删除记录（软删除）
        :param bid:
        :param cid:
        :param did:
        :return:
        """
        if LaborStandard.soft_delete_record(bid, cid):
            return 0
        return 3


    @classmethod
    def delete_labor_standard_bids(cls, delete_bids, cid) -> int:
        """
        批量删除记录（软删除）
        :param delete_bids:
        :param cid:
        :return:
        """
        if LaborStandard.soft_delete_record_bids(delete_bids, cid):
            return 0
        return 3

    @classmethod
    def update_labor_standard(cls, bid, cid, mode, masterType, slaveType, detailArr) -> int:
        """
        更新记录 直接采用软删除 再插入的方法
        :param bid:
        :param cid:
        :param did:
        :param mode:
        :param masterType:
        :param slaveType:
        :param detailArr:
        :return:
        """
        res = LaborDbService.delete_labor_standard(bid, cid)
        if not res:
            res = LaborDbService.write_labor_standard_push_into_db(bid, cid, mode, masterType, slaveType,detailArr)
        return res


    @classmethod
    def initializData(cls, date_list,taskArr,didArr,cid):
        #print('进入到这个hhhhhh量 initializData',date_list,taskArr,didArr)
        data = {}
        taskBids_list: List[str] = []
        start_end_shikes: List[str] = []  # 09:15-09:30
        laborStandardBids: List[str] = []

        minStart = min(date_list) + ' 00:00'
        maxEnd = max(date_list) + ' 23:45'

        for task in taskArr:
            if 'taskBid' in task and task['taskBid'] not in task:
                taskBids_list.append(task['taskBid'])
            if 'laborStandardBid' in task and task['laborStandardBid'] not in task:
                laborStandardBids.append(task['laborStandardBid'])

            for times in task.get('taskTimeArr', []):
                if isinstance(times, dict) and 'startTimeStr' in times and 'endTimeStr' in times:
                    startTimeStr = times['startTimeStr']
                    endTimeStr = times['endTimeStr']

                    start_end = '%s-%s' % (startTimeStr, endTimeStr)
                    if start_end not in start_end_shikes:
                        start_end_shikes.append(start_end)

        for date in date_list:
            data[date] = {}
            for start_end in start_end_shikes:
                data[date][start_end] = {}
                for taskbid in taskBids_list:
                    data[date][start_end][taskbid] = {'value':0,'scope':[0,0]}  # 标准pos量对应的值，0.9pos量对应的值，1.1pos量对应的值
                    minStart = min(minStart, date + ' ' + start_end.split('-')[0])
                    maxEnd = max(maxEnd, date + ' ' + start_end.split('-')[1])

        laborStandardDict = {}
        # for did in didArr:
        for laborStandardBid in laborStandardBids:
            laborStandard = LaborStandard.get_labor_standard(laborStandardBid, cid)
            laborStandardDict[laborStandardBid] = laborStandard

        return data,minStart, maxEnd,taskBids_list,laborStandardBids,laborStandardDict

    @classmethod
    def labor_standard_calculate_task(cls, cid: str, date_list:List[str], didArr: List[int], taskArr: List[Dict[str, Union[str, List[Dict[str, str]]]]], forecastType:str):
        s = datetime.now()
        data, minStart, maxEnd,taskBids_list, laborStandardBids, laborStandardDict = LaborDbService.initializData(date_list,taskArr,didArr,cid)  # 初始化输出,格式化
        e = datetime.now()
        infoLog.info('RequestHandler 构造结束'+str (e - s))
        items = []  # 用于记录需要向数据库修改的值
        itemsKeys = []  # 用于记录向数据库修改的值的keys
        for did in didArr:
            did = str(did)

            s1=datetime.now()

            # standard = ['turnover', 'order_num',  'peoples']
            type_sql = ['if(adjustGMV!=0, adjustGMV, if(predictGMV!=0,predictGMV,trueGMV))',
                        'if(adjustOrders!=0, adjustOrders, if(predictOrders!=0,predictOrders,trueOrders))',
                        'if(adjustPeoples!=0, adjustPeoples, if(predictPeoples!=0,predictPeoples,truePeoples))']
            selectPart = ''

            # 存储POS结果
            posBase_list = []
            for t_s in type_sql:
                selectPart = t_s
                posBase_list.append(PosDBModel.get_base_pos_startend_time(cid, [did], minStart, maxEnd, selectPart))

            e1 = datetime.now()
            infoLog.info('RequestHandler 获取pos' +str (e1 - s1))

            calcBase ={} #获取修改值的逻辑不要了 LaborStandard.get_base_calc(cid,[did],minStart, maxEnd,taskBids_list,laborStandardBids)

            e2 = datetime.now()
            infoLog.info('RequestHandler 获取calc' +str (e2 - e1))

            updatetime=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            for task in taskArr:

                forecastStandard = task.get('forecastStandard', '')

                taskBid=task['taskBid']  #这个任务
                laborStandardBid=task['laborStandardBid'] #这个劳动力标准来的
                laborStandard = laborStandardDict.get(laborStandardBid,{})

                #判断计算劳动人数应该
                standard_index = -1
                if laborStandard.get('masterType','') == forecastStandard:
                    standard_index = 0
                elif laborStandard.get('slaveType','') == forecastStandard:
                    standard_index = 1

                labor_data = laborStandard.get('data',{})

                '''
                如一个单业务类型“交易笔数”的劳动力标准，分别设置了3组标准，
                即scale=10,工时为30分钟；scale=20，工时为60分钟；scale=30，工时为90分钟；
                那么假如预测出来一时段的pos数据“交易笔数”<10，那么就取30分钟工时;
                假如“交易笔数”>10 并且“交易笔数”<20，那么取60分钟工时；
                假如“交易笔数”>20 那么取90分钟工时；
                '''

                for date in date_list:
                    print('date', date)
                    for taskTime in task['taskTimeArr'] :
                        startTime = taskTime['startTimeStr']
                        endTime   = taskTime['endTimeStr']
                        begin_end = '%s-%s' % (startTime, endTime)
                        finditem='%s_%s_%s_%s_%s_%s' %(cid,did,date,begin_end.split('-')[0],begin_end.split('-')[1],taskBid)


                        calc_dict = data[date][begin_end][taskBid]

                        if  finditem in calcBase and calcBase[finditem]!=0:
                            calc_dict['value']=calc_dict['value']+calcBase[finditem]
                            calc_dict['scope'][0] = calc_dict['scope'][0]+calcBase[finditem]
                            calc_dict['scope'][1] = calc_dict['scope'][1] + calcBase[finditem]

                            data[date][begin_end][taskBid] = calc_dict
                            infoLog.info("taskBid : %s , laborStandardBid : %s , begin_end : %s ,修改值 :%s " % (taskBid, laborStandardBid, begin_end, str(data[date][begin_end][taskBid])))
                            continue

                        if 1 in labor_data:
                            pos = 0
                            if forecastStandard == 'turnover':
                                posBase = posBase_list[0]
                                for i in posBase:
                                    if date + ' ' + startTime <= str(i) < date + ' ' + endTime:
                                        pos += posBase[i]
                            elif forecastStandard == 'order_num':
                                posBase = posBase_list[1]
                                for i in posBase:
                                    if date + ' ' + startTime <= str(i) < date + ' ' + endTime:
                                        pos += posBase[i]
                            else:
                                posBase = posBase_list[2]
                                for i in posBase:
                                    if date + ' ' + startTime <= str(i) < date + ' ' + endTime:
                                        pos += posBase[i]
                            calc = LaborDbService.get_calc_value(labor_data, standard_index, pos)     #计算出一个真实值
                            min_calc = LaborDbService.get_calc_value(labor_data, standard_index, pos*0.9) #计算出一个最小值
                            max_calc = LaborDbService.get_calc_value(labor_data, standard_index, pos*1.1) #计算出一个最大值
                            calc_dict['value'] = calc_dict['value']+calc
                            calc_dict['scope'][0] = calc_dict['scope'][0] + min_calc
                            calc_dict['scope'][1] = calc_dict['scope'][1] + max_calc
                            # print(pos, calc_dict, labor_data)

                            data[date][begin_end][taskBid]=calc_dict

                            if calc_dict['value']>0:
                                #insert into labor_cacl_value(inserttime,updatetime,forecastType,forecastStandard," \"cid,dayStr,startTimeStr,endTimeStr,taskBid,laborStandardBid,caclValue,did,status," \ "min_caclValue,max_caclValue) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                                items.append((updatetime,updatetime,forecastType, forecastStandard, cid, date,startTime,endTime, taskBid, laborStandardBid, calc_dict['value'] ,did,1,calc_dict['scope'][0],calc_dict['scope'][1]))

                            uniqonKey =  (forecastType,cid, date, did)
                            #forecastType = % s and cid = % s and dayStr = % s and startTimeStr = % s and endTimeStr = % s and taskBid = % s and did = % s
                            if uniqonKey not in itemsKeys:

                                itemsKeys.append(uniqonKey)
            end1=datetime.now()
            infoLog.info('RequestHandler 函数结束耗时' +str (end1 - s1))

        save_begin=datetime.now()
        LaborStandard.labor_cacl_value_save(items, itemsKeys)
        #t = threading.Thread(target=LaborStandard.labor_cacl_value_save, args=(items, itemsKeys))
        #t.start()
        save_end=datetime.now()
        infoLog.info('RequestHandler 数据库存储' +str (save_end - save_begin))

        e = datetime.now()
        infoLog.info('RequestHandler 函数结束耗时' +str(e - s))
        print('RequestHandler 函数结束耗时' +str(e - s))
        return data


    def get_calc_value(labor_data,standard_index,pos):
        """
        获取POS值，根据劳动力标准数据，计算对应的劳动人数上下限
        :param standard_index:
        :param pos:
        :return:
        """

        max_pos = labor_data[len(labor_data)][1]
        min_pos = labor_data[1][0]
        calc_value = 0
        data_info = ()
        count_i = 0
        if standard_index == 0:
            for data_i, data_info in labor_data.items():
                count_i += 1
                if pos >= float(data_info[0]) and pos < float(data_info[1]):
                    calc_value = labor_data[data_i][2]
                    break
            if count_i == len(labor_data):
                if pos >= max_pos:
                    calc_value = labor_data[len(labor_data)][2]
                elif pos <= min_pos:
                    calc_value = labor_data[1][2]

        if standard_index == 1:
            for data_i, data_info in labor_data.items():
                end = data_info[standard_index]
                if (pos > begin and pos <= end and (not flag)) or (pos == 0 and end == 0):
                    flag = True
                    calc_value = labor_data[data_i][2]
                begin = data_info[standard_index]
                if flag:
                    break
            if pos > end:
                calc_value = data_info[2]
        return calc_value

    @gen.coroutine
    def labor_cacl_value_modify(paramsDict):
        '''

        :param paramsDict:
        :return:
        '''
        resultCode=100
        cid = paramsDict.get('cid','')

        forecastModifyArr = paramsDict.get('forecastModifyArr',[])
        forecastType = paramsDict.get('forecastType', '')
        didArr = paramsDict.get('didArr', '')
        for forecastModify in forecastModifyArr:
            forecastDate = forecastModify.get('forecastDate','')
            startTimeStr = forecastModify.get('startTimeStr','')
            endTimeStr = forecastModify.get('endTimeStr', '')

            forecastValue = forecastModify.get('forecastValue', '')
            editValue = forecastModify.get('editValue', '')

            taskBid = forecastModify.get('taskBid', '')
            laborStandardBid=forecastModify.get('laborStandardBid','')

            forecastStandard = forecastModify.get('forecastStandard','')
            updatetime=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            for did in didArr:
                resultCode = max(LaborStandard.labor_cacl_value_modify_task(updatetime,cid,taskBid,forecastStandard, laborStandardBid, did,forecastDate,startTimeStr,endTimeStr,forecastValue,editValue,forecastType),resultCode)
        raise gen.Return(resultCode)

    @gen.coroutine
    def labor_standard_forecast_v2(cid, forecastType, didArr, dateArr):
        """
        工时预测
        :param forecast_date_end:
        :param forecast_date_start:
        :param cid:
        :param forecastType:
        :param didArr:
        :param taskArr:
        :return:
        """
        data_all = {}
        for arr in dateArr:
            forecast_date_start = arr['dateTime']
            forecast_date_end = arr['dateTime']
            taskArr = arr.get('taskArr', [])

            print('labor_standard_forecast')
            cid = str(cid)
            date_list: List[str] = []
            date: str = forecast_date_start

            while date <= forecast_date_end:
                date_list.append(date)
                date = (datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')

            if len(arr['taskArr']) == 0:
                data = {}
                data[forecast_date_start] = {}
            else:
            # 任务工时预测
                data = LaborDbService.labor_standard_calculate_task(cid, date_list, didArr, taskArr, forecastType)
            data_all.update(data)
        raise gen.Return(data_all)

    @gen.coroutine
    def labor_standard_forecast(cid, forecastType,  forecast_date_start, forecast_date_end, didArr, taskArr):
        """
        工时预测
        :param forecast_date_end:
        :param forecast_date_start:
        :param cid:
        :param forecastType:
        :param didArr:
        :param taskArr:
        :return:
        """
        print('labor_standard_forecast')
        cid = str(cid)
        date_list: List[str] = []
        date: str = forecast_date_start

        while date <= forecast_date_end:
            date_list.append(date)
            date = (datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')

        # 任务工时预测
        data = LaborDbService.labor_standard_calculate_task(cid,  date_list, didArr, taskArr, forecastType)
        raise gen.Return(data)

    def labor_standard_forecast_s(forecast_date_start,forecast_date_end,raw_data):
        print('labor_standard_forecast_s')
        datestart = datetime.strptime(forecast_date_start, '%Y-%m-%d')
        dateend = datetime.strptime(forecast_date_end, '%Y-%m-%d')
        data={}
        while datestart <= dateend:
            d=datestart.strftime('%Y-%m-%d')
            raw_data['forecast_date_start']=d
            raw_data['forecast_date_end']=d
            print('日期%s 开始时间:%s' %(d,datetime.now()),raw_data['forecast_date_start'],raw_data['forecast_date_end'])
            infoLog.info('日期%s 开始时间:%s' %(d,datetime.now()))
            response = requests.post('*', data=json.dumps(raw_data),headers={'content-type': "application/json"})
            infoLog.info('日期%s 结束时间:%s' % (d, datetime.now()))
            print(response.text)
            data.update(json.loads(response.text)['data'])
            datestart += timedelta(days=1)
        print(data.keys())
        return data




if __name__ == '__main__':
    # raw_data={"forecast_date_start":"2020-02-12","taskArr":[{"taskTimeArr":[{"startTimeStr":"09:30","endTimeStr":"10:00"},{"startTimeStr":"13:00","endTimeStr":"13:30"},{"startTimeStr":"13:30","endTimeStr":"14:00"},{"startTimeStr":"20:00","endTimeStr":"20:30"}],"forecastStandard":"order_num","laborStandardBid":"2020011910055461814013ba20000167","taskBid":"2020011911413970014043ba20000174"},{"taskTimeArr":[{"startTimeStr":"14:00","endTimeStr":"14:30"},{"startTimeStr":"19:30","endTimeStr":"20:00"}],"forecastStandard":"order_num","laborStandardBid":"2020011910522884814013ba20000175","taskBid":"2020011911373739814043ba20000164"},{"taskTimeArr":[{"startTimeStr":"20:30","endTimeStr":"21:00"},{"startTimeStr":"21:00","endTimeStr":"21:30"}],"forecastStandard":"order_num","laborStandardBid":"2020011910034032114013ba20000155","taskBid":"2020011910491098314043ba20000151"},{"taskTimeArr":[{"startTimeStr":"08:30","endTimeStr":"09:00"},{"startTimeStr":"09:00","endTimeStr":"09:30"},{"startTimeStr":"09:30","endTimeStr":"10:00"},{"startTimeStr":"10:00","endTimeStr":"10:30"}],"forecastStandard":"order_num","laborStandardBid":"2020011910020350314013ba20000149","taskBid":"2020011910484687814043ba20000145"},{"taskTimeArr":[{"startTimeStr":"20:00","endTimeStr":"20:30"},{"startTimeStr":"20:30","endTimeStr":"21:00"},{"startTimeStr":"21:00","endTimeStr":"21:30"},{"startTimeStr":"21:30","endTimeStr":"22:00"},{"startTimeStr":"22:00","endTimeStr":"22:30"}],"forecastStandard":"order_num","laborStandardBid":"2020011909585012514013ba20000131","taskBid":"2020011910460586114043ba20000136"},{"taskTimeArr":[{"startTimeStr":"06:30","endTimeStr":"07:00"},{"startTimeStr":"07:00","endTimeStr":"07:30"},{"startTimeStr":"07:30","endTimeStr":"08:00"},{"startTimeStr":"08:00","endTimeStr":"08:30"},{"startTimeStr":"08:30","endTimeStr":"09:00"},{"startTimeStr":"09:00","endTimeStr":"09:30"}],"forecastStandard":"order_num","laborStandardBid":"2020011909563328514013ba20000126","taskBid":"2020011910451237214043ba20000129"},{"taskTimeArr":[{"startTimeStr":"20:30","endTimeStr":"21:00"},{"startTimeStr":"21:00","endTimeStr":"21:30"},{"startTimeStr":"21:30","endTimeStr":"22:00"},{"startTimeStr":"22:00","endTimeStr":"22:30"}],"forecastStandard":"order_num","laborStandardBid":"2020011909512080614013ba20000110","taskBid":"2020011910434583214043ba20000116"},{"taskTimeArr":[{"startTimeStr":"06:30","endTimeStr":"07:00"},{"startTimeStr":"07:00","endTimeStr":"07:30"},{"startTimeStr":"07:30","endTimeStr":"08:00"},{"startTimeStr":"08:00","endTimeStr":"08:30"}],"forecastStandard":"order_num","laborStandardBid":"2020011714525910514013ba20000106","taskBid":"2020011910312016214043ba20000101"},{"taskTimeArr":[{"startTimeStr":"06:30","endTimeStr":"07:00"},{"startTimeStr":"07:00","endTimeStr":"07:30"},{"startTimeStr":"07:30","endTimeStr":"08:00"},{"startTimeStr":"08:00","endTimeStr":"08:30"},{"startTimeStr":"08:30","endTimeStr":"09:00"},{"startTimeStr":"09:00","endTimeStr":"09:30"},{"startTimeStr":"09:30","endTimeStr":"10:00"},{"startTimeStr":"10:00","endTimeStr":"10:30"},{"startTimeStr":"10:30","endTimeStr":"11:00"},{"startTimeStr":"11:00","endTimeStr":"11:30"},{"startTimeStr":"11:30","endTimeStr":"12:00"},{"startTimeStr":"12:00","endTimeStr":"12:30"},{"startTimeStr":"12:30","endTimeStr":"13:00"},{"startTimeStr":"13:00","endTimeStr":"13:30"},{"startTimeStr":"13:30","endTimeStr":"14:00"},{"startTimeStr":"14:00","endTimeStr":"14:30"},{"startTimeStr":"14:30","endTimeStr":"15:00"},{"startTimeStr":"15:00","endTimeStr":"15:30"},{"startTimeStr":"15:30","endTimeStr":"16:00"},{"startTimeStr":"16:00","endTimeStr":"16:30"},{"startTimeStr":"16:30","endTimeStr":"17:00"},{"startTimeStr":"17:00","endTimeStr":"17:30"},{"startTimeStr":"17:30","endTimeStr":"18:00"},{"startTimeStr":"18:00","endTimeStr":"18:30"},{"startTimeStr":"18:30","endTimeStr":"19:00"},{"startTimeStr":"19:00","endTimeStr":"19:30"},{"startTimeStr":"19:30","endTimeStr":"20:00"},{"startTimeStr":"20:00","endTimeStr":"20:30"},{"startTimeStr":"20:30","endTimeStr":"21:00"},{"startTimeStr":"21:00","endTimeStr":"21:30"},{"startTimeStr":"21:30","endTimeStr":"22:00"},{"startTimeStr":"22:00","endTimeStr":"22:30"}],"forecastStandard":"order_num","laborStandardBid":"2020011712275969414013ba20000093","taskBid":"2020011910301640214043ba20000097"},{"taskTimeArr":[{"startTimeStr":"06:30","endTimeStr":"07:00"},{"startTimeStr":"07:00","endTimeStr":"07:30"},{"startTimeStr":"07:30","endTimeStr":"08:00"},{"startTimeStr":"08:00","endTimeStr":"08:30"},{"startTimeStr":"08:30","endTimeStr":"09:00"},{"startTimeStr":"09:00","endTimeStr":"09:30"},{"startTimeStr":"09:30","endTimeStr":"10:00"},{"startTimeStr":"10:00","endTimeStr":"10:30"},{"startTimeStr":"10:30","endTimeStr":"11:00"},{"startTimeStr":"11:00","endTimeStr":"11:30"},{"startTimeStr":"11:30","endTimeStr":"12:00"},{"startTimeStr":"12:00","endTimeStr":"12:30"},{"startTimeStr":"12:30","endTimeStr":"13:00"},{"startTimeStr":"13:00","endTimeStr":"13:30"},{"startTimeStr":"13:30","endTimeStr":"14:00"},{"startTimeStr":"14:00","endTimeStr":"14:30"},{"startTimeStr":"14:30","endTimeStr":"15:00"},{"startTimeStr":"15:00","endTimeStr":"15:30"},{"startTimeStr":"15:30","endTimeStr":"16:00"},{"startTimeStr":"16:00","endTimeStr":"16:30"},{"startTimeStr":"16:30","endTimeStr":"17:00"},{"startTimeStr":"17:00","endTimeStr":"17:30"},{"startTimeStr":"17:30","endTimeStr":"18:00"},{"startTimeStr":"18:00","endTimeStr":"18:30"},{"startTimeStr":"18:30","endTimeStr":"19:00"},{"startTimeStr":"19:00","endTimeStr":"19:30"},{"startTimeStr":"19:30","endTimeStr":"20:00"},{"startTimeStr":"20:00","endTimeStr":"20:30"},{"startTimeStr":"20:30","endTimeStr":"21:00"},{"startTimeStr":"21:00","endTimeStr":"21:30"},{"startTimeStr":"21:30","endTimeStr":"22:00"},{"startTimeStr":"22:00","endTimeStr":"22:30"}],"forecastStandard":"order_num","laborStandardBid":"2020011712175149914013ba20000089","taskBid":"2020011910291887514043ba20000081"},{"taskTimeArr":[{"startTimeStr":"06:30","endTimeStr":"07:00"},{"startTimeStr":"07:00","endTimeStr":"07:30"},{"startTimeStr":"07:30","endTimeStr":"08:00"},{"startTimeStr":"08:00","endTimeStr":"08:30"},{"startTimeStr":"08:30","endTimeStr":"09:00"},{"startTimeStr":"09:00","endTimeStr":"09:30"},{"startTimeStr":"09:30","endTimeStr":"10:00"},{"startTimeStr":"10:00","endTimeStr":"10:30"},{"startTimeStr":"10:30","endTimeStr":"11:00"},{"startTimeStr":"11:00","endTimeStr":"11:30"},{"startTimeStr":"11:30","endTimeStr":"12:00"},{"startTimeStr":"12:00","endTimeStr":"12:30"},{"startTimeStr":"12:30","endTimeStr":"13:00"},{"startTimeStr":"13:00","endTimeStr":"13:30"},{"startTimeStr":"13:30","endTimeStr":"14:00"},{"startTimeStr":"14:00","endTimeStr":"14:30"},{"startTimeStr":"14:30","endTimeStr":"15:00"},{"startTimeStr":"15:00","endTimeStr":"15:30"},{"startTimeStr":"15:30","endTimeStr":"16:00"},{"startTimeStr":"16:00","endTimeStr":"16:30"},{"startTimeStr":"16:30","endTimeStr":"17:00"},{"startTimeStr":"17:00","endTimeStr":"17:30"},{"startTimeStr":"17:30","endTimeStr":"18:00"},{"startTimeStr":"18:00","endTimeStr":"18:30"},{"startTimeStr":"18:30","endTimeStr":"19:00"},{"startTimeStr":"19:00","endTimeStr":"19:30"},{"startTimeStr":"19:30","endTimeStr":"20:00"},{"startTimeStr":"20:00","endTimeStr":"20:30"},{"startTimeStr":"20:30","endTimeStr":"21:00"},{"startTimeStr":"21:00","endTimeStr":"21:30"},{"startTimeStr":"21:30","endTimeStr":"22:00"},{"startTimeStr":"22:00","endTimeStr":"22:30"}],"forecastStandard":"order_num","laborStandardBid":"2020011711431802114013ba20000074","taskBid":"2020011910283150614043ba20000072"},{"taskTimeArr":[{"startTimeStr":"06:30","endTimeStr":"07:00"},{"startTimeStr":"07:00","endTimeStr":"07:30"},{"startTimeStr":"07:30","endTimeStr":"08:00"},{"startTimeStr":"08:00","endTimeStr":"08:30"},{"startTimeStr":"08:30","endTimeStr":"09:00"},{"startTimeStr":"09:00","endTimeStr":"09:30"},{"startTimeStr":"09:30","endTimeStr":"10:00"},{"startTimeStr":"10:00","endTimeStr":"10:30"},{"startTimeStr":"10:30","endTimeStr":"11:00"},{"startTimeStr":"11:00","endTimeStr":"11:30"},{"startTimeStr":"11:30","endTimeStr":"12:00"},{"startTimeStr":"12:00","endTimeStr":"12:30"},{"startTimeStr":"12:30","endTimeStr":"13:00"},{"startTimeStr":"13:00","endTimeStr":"13:30"},{"startTimeStr":"13:30","endTimeStr":"14:00"},{"startTimeStr":"14:00","endTimeStr":"14:30"},{"startTimeStr":"14:30","endTimeStr":"15:00"},{"startTimeStr":"15:00","endTimeStr":"15:30"},{"startTimeStr":"15:30","endTimeStr":"16:00"},{"startTimeStr":"16:00","endTimeStr":"16:30"},{"startTimeStr":"16:30","endTimeStr":"17:00"},{"startTimeStr":"17:00","endTimeStr":"17:30"},{"startTimeStr":"17:30","endTimeStr":"18:00"},{"startTimeStr":"18:00","endTimeStr":"18:30"},{"startTimeStr":"18:30","endTimeStr":"19:00"},{"startTimeStr":"19:00","endTimeStr":"19:30"},{"startTimeStr":"19:30","endTimeStr":"20:00"},{"startTimeStr":"20:00","endTimeStr":"20:30"},{"startTimeStr":"20:30","endTimeStr":"21:00"},{"startTimeStr":"21:00","endTimeStr":"21:30"},{"startTimeStr":"21:30","endTimeStr":"22:00"},{"startTimeStr":"22:00","endTimeStr":"22:30"}],"forecastStandard":"order_num","laborStandardBid":"2020011711403270414013ba20000062","taskBid":"2020011910271112914043ba20000063"},{"taskTimeArr":[{"startTimeStr":"06:30","endTimeStr":"07:00"},{"startTimeStr":"07:00","endTimeStr":"07:30"},{"startTimeStr":"07:30","endTimeStr":"08:00"},{"startTimeStr":"08:00","endTimeStr":"08:30"},{"startTimeStr":"08:30","endTimeStr":"09:00"},{"startTimeStr":"09:00","endTimeStr":"09:30"},{"startTimeStr":"09:30","endTimeStr":"10:00"},{"startTimeStr":"10:00","endTimeStr":"10:30"},{"startTimeStr":"10:30","endTimeStr":"11:00"},{"startTimeStr":"11:00","endTimeStr":"11:30"},{"startTimeStr":"11:30","endTimeStr":"12:00"},{"startTimeStr":"12:00","endTimeStr":"12:30"},{"startTimeStr":"12:30","endTimeStr":"13:00"},{"startTimeStr":"13:00","endTimeStr":"13:30"},{"startTimeStr":"13:30","endTimeStr":"14:00"},{"startTimeStr":"14:00","endTimeStr":"14:30"},{"startTimeStr":"14:30","endTimeStr":"15:00"},{"startTimeStr":"15:00","endTimeStr":"15:30"},{"startTimeStr":"15:30","endTimeStr":"16:00"},{"startTimeStr":"16:00","endTimeStr":"16:30"},{"startTimeStr":"16:30","endTimeStr":"17:00"},{"startTimeStr":"17:00","endTimeStr":"17:30"},{"startTimeStr":"17:30","endTimeStr":"18:00"},{"startTimeStr":"18:00","endTimeStr":"18:30"},{"startTimeStr":"18:30","endTimeStr":"19:00"},{"startTimeStr":"19:00","endTimeStr":"19:30"},{"startTimeStr":"19:30","endTimeStr":"20:00"},{"startTimeStr":"20:00","endTimeStr":"20:30"},{"startTimeStr":"20:30","endTimeStr":"21:00"},{"startTimeStr":"21:00","endTimeStr":"21:30"},{"startTimeStr":"21:30","endTimeStr":"22:00"},{"startTimeStr":"22:00","endTimeStr":"22:30"}],"forecastStandard":"order_num","laborStandardBid":"2020011711233026514013ba20000052","taskBid":"2020011910260637414043ba20000054"},{"taskTimeArr":[{"startTimeStr":"06:30","endTimeStr":"07:00"},{"startTimeStr":"07:00","endTimeStr":"07:30"},{"startTimeStr":"07:30","endTimeStr":"08:00"},{"startTimeStr":"08:00","endTimeStr":"08:30"},{"startTimeStr":"08:30","endTimeStr":"09:00"},{"startTimeStr":"09:00","endTimeStr":"09:30"},{"startTimeStr":"09:30","endTimeStr":"10:00"},{"startTimeStr":"10:00","endTimeStr":"10:30"},{"startTimeStr":"10:30","endTimeStr":"11:00"},{"startTimeStr":"11:00","endTimeStr":"11:30"},{"startTimeStr":"11:30","endTimeStr":"12:00"},{"startTimeStr":"12:00","endTimeStr":"12:30"},{"startTimeStr":"12:30","endTimeStr":"13:00"},{"startTimeStr":"13:00","endTimeStr":"13:30"},{"startTimeStr":"13:30","endTimeStr":"14:00"},{"startTimeStr":"14:00","endTimeStr":"14:30"},{"startTimeStr":"14:30","endTimeStr":"15:00"},{"startTimeStr":"15:00","endTimeStr":"15:30"},{"startTimeStr":"15:30","endTimeStr":"16:00"},{"startTimeStr":"16:00","endTimeStr":"16:30"},{"startTimeStr":"16:30","endTimeStr":"17:00"},{"startTimeStr":"17:00","endTimeStr":"17:30"},{"startTimeStr":"17:30","endTimeStr":"18:00"},{"startTimeStr":"18:00","endTimeStr":"18:30"},{"startTimeStr":"18:30","endTimeStr":"19:00"},{"startTimeStr":"19:00","endTimeStr":"19:30"},{"startTimeStr":"19:30","endTimeStr":"20:00"},{"startTimeStr":"20:00","endTimeStr":"20:30"},{"startTimeStr":"20:30","endTimeStr":"21:00"},{"startTimeStr":"21:00","endTimeStr":"21:30"},{"startTimeStr":"21:30","endTimeStr":"22:00"},{"startTimeStr":"22:00","endTimeStr":"22:30"}],"forecastStandard":"order_num","laborStandardBid":"2020011711200761514013ba20000045","taskBid":"2020011910251711814043ba20000047"},{"taskTimeArr":[{"startTimeStr":"06:30","endTimeStr":"07:00"},{"startTimeStr":"07:00","endTimeStr":"07:30"},{"startTimeStr":"07:30","endTimeStr":"08:00"},{"startTimeStr":"08:00","endTimeStr":"08:30"},{"startTimeStr":"08:30","endTimeStr":"09:00"},{"startTimeStr":"09:00","endTimeStr":"09:30"},{"startTimeStr":"09:30","endTimeStr":"10:00"},{"startTimeStr":"10:00","endTimeStr":"10:30"},{"startTimeStr":"10:30","endTimeStr":"11:00"},{"startTimeStr":"11:00","endTimeStr":"11:30"},{"startTimeStr":"11:30","endTimeStr":"12:00"},{"startTimeStr":"12:00","endTimeStr":"12:30"},{"startTimeStr":"12:30","endTimeStr":"13:00"},{"startTimeStr":"13:00","endTimeStr":"13:30"},{"startTimeStr":"13:30","endTimeStr":"14:00"},{"startTimeStr":"14:00","endTimeStr":"14:30"},{"startTimeStr":"14:30","endTimeStr":"15:00"},{"startTimeStr":"15:00","endTimeStr":"15:30"},{"startTimeStr":"15:30","endTimeStr":"16:00"},{"startTimeStr":"16:00","endTimeStr":"16:30"},{"startTimeStr":"16:30","endTimeStr":"17:00"},{"startTimeStr":"17:00","endTimeStr":"17:30"},{"startTimeStr":"17:30","endTimeStr":"18:00"},{"startTimeStr":"18:00","endTimeStr":"18:30"},{"startTimeStr":"18:30","endTimeStr":"19:00"},{"startTimeStr":"19:00","endTimeStr":"19:30"},{"startTimeStr":"19:30","endTimeStr":"20:00"},{"startTimeStr":"20:00","endTimeStr":"20:30"},{"startTimeStr":"20:30","endTimeStr":"21:00"},{"startTimeStr":"21:00","endTimeStr":"21:30"},{"startTimeStr":"21:30","endTimeStr":"22:00"},{"startTimeStr":"22:00","endTimeStr":"22:30"}],"forecastStandard":"order_num","laborStandardBid":"2020011711174879714013ba20000036","taskBid":"2020011910240080214043ba20000037"},{"taskTimeArr":[{"startTimeStr":"06:30","endTimeStr":"07:00"},{"startTimeStr":"07:00","endTimeStr":"07:30"},{"startTimeStr":"07:30","endTimeStr":"08:00"},{"startTimeStr":"08:00","endTimeStr":"08:30"},{"startTimeStr":"08:30","endTimeStr":"09:00"},{"startTimeStr":"09:00","endTimeStr":"09:30"},{"startTimeStr":"09:30","endTimeStr":"10:00"},{"startTimeStr":"10:00","endTimeStr":"10:30"},{"startTimeStr":"10:30","endTimeStr":"11:00"},{"startTimeStr":"11:00","endTimeStr":"11:30"},{"startTimeStr":"11:30","endTimeStr":"12:00"},{"startTimeStr":"12:00","endTimeStr":"12:30"},{"startTimeStr":"12:30","endTimeStr":"13:00"},{"startTimeStr":"13:00","endTimeStr":"13:30"},{"startTimeStr":"13:30","endTimeStr":"14:00"},{"startTimeStr":"14:00","endTimeStr":"14:30"},{"startTimeStr":"14:30","endTimeStr":"15:00"},{"startTimeStr":"15:00","endTimeStr":"15:30"},{"startTimeStr":"15:30","endTimeStr":"16:00"},{"startTimeStr":"16:00","endTimeStr":"16:30"},{"startTimeStr":"16:30","endTimeStr":"17:00"},{"startTimeStr":"17:00","endTimeStr":"17:30"},{"startTimeStr":"17:30","endTimeStr":"18:00"},{"startTimeStr":"18:00","endTimeStr":"18:30"},{"startTimeStr":"18:30","endTimeStr":"19:00"},{"startTimeStr":"19:00","endTimeStr":"19:30"},{"startTimeStr":"19:30","endTimeStr":"20:00"},{"startTimeStr":"20:00","endTimeStr":"20:30"},{"startTimeStr":"20:30","endTimeStr":"21:00"},{"startTimeStr":"21:00","endTimeStr":"21:30"},{"startTimeStr":"21:30","endTimeStr":"22:00"},{"startTimeStr":"22:00","endTimeStr":"22:30"}],"forecastStandard":"order_num","laborStandardBid":"2020011711142178614013ba20000024","taskBid":"2020011910222437314043ba20000024"},{"taskTimeArr":[{"startTimeStr":"06:30","endTimeStr":"07:00"},{"startTimeStr":"07:00","endTimeStr":"07:30"},{"startTimeStr":"07:30","endTimeStr":"08:00"},{"startTimeStr":"08:00","endTimeStr":"08:30"},{"startTimeStr":"08:30","endTimeStr":"09:00"},{"startTimeStr":"09:00","endTimeStr":"09:30"},{"startTimeStr":"09:30","endTimeStr":"10:00"},{"startTimeStr":"10:00","endTimeStr":"10:30"},{"startTimeStr":"10:30","endTimeStr":"11:00"},{"startTimeStr":"11:00","endTimeStr":"11:30"},{"startTimeStr":"11:30","endTimeStr":"12:00"},{"startTimeStr":"12:00","endTimeStr":"12:30"},{"startTimeStr":"12:30","endTimeStr":"13:00"},{"startTimeStr":"13:00","endTimeStr":"13:30"},{"startTimeStr":"13:30","endTimeStr":"14:00"},{"startTimeStr":"14:00","endTimeStr":"14:30"},{"startTimeStr":"14:30","endTimeStr":"15:00"},{"startTimeStr":"15:00","endTimeStr":"15:30"},{"startTimeStr":"15:30","endTimeStr":"16:00"},{"startTimeStr":"16:00","endTimeStr":"16:30"},{"startTimeStr":"16:30","endTimeStr":"17:00"},{"startTimeStr":"17:00","endTimeStr":"17:30"},{"startTimeStr":"17:30","endTimeStr":"18:00"},{"startTimeStr":"18:00","endTimeStr":"18:30"},{"startTimeStr":"18:30","endTimeStr":"19:00"},{"startTimeStr":"19:00","endTimeStr":"19:30"},{"startTimeStr":"19:30","endTimeStr":"20:00"},{"startTimeStr":"20:00","endTimeStr":"20:30"},{"startTimeStr":"20:30","endTimeStr":"21:00"},{"startTimeStr":"21:00","endTimeStr":"21:30"},{"startTimeStr":"21:30","endTimeStr":"22:00"},{"startTimeStr":"22:00","endTimeStr":"22:30"}],"forecastStandard":"order_num","laborStandardBid":"2020011711113969714013ba20000015","taskBid":"2020011910210978514043ba20000012"}],"didArr":[12],"forecast_date_end":"2020-02-12","forecastType":"0","token": "80eef7008995c9fa9476bdd0acc560f2", "timestr": "2020-03-10 18:08:49.405800","cid":50000319}
    # raw_data = {"token": "79064903985024d18a3b778a79fe9b88", "timestr": "2020-04-08 21:53:59.271283","cid": "60000006","forecastType": "0", "forecast_date_start": "2019-07-12", "forecast_date_end": "2019-07-18", "didArr": [6],"taskArr": [{"taskBid": "201903292247340840341012959f0001", "laborStandardBid": "20191226103154364054140139290002","forecastStandard": "turnover", "taskTimeArr": [{"startTimeStr": "09:00", "endTimeStr": "09:15"},{"startTimeStr": "09:15", "endTimeStr": "09:30"},{"startTimeStr": "09:30", "endTimeStr": "09:45"}]}]}
    # cid = raw_data.get('cid', '')
    # forecast_type = raw_data.get('forecastType', '')
    # forecast_date_start = raw_data.get('forecast_date_start', '')
    # forecast_date_end = raw_data.get('forecast_date_end', '')
    # did_arr = raw_data.get('didArr', '')
    # task_arr = raw_data.get('taskArr', [])
    # data =  LaborDbService.labor_standard_forecast(cid, forecast_type, forecast_date_start, forecast_date_end,  did_arr, task_arr)
    # result = {'code': 100, 'result': "预测成功", 'data': data}
    # print(result)

    print('都可以的')
    test_data = {"didArr":[38044],"timestr":"2020-08-06 11:20:33.290","forecastType":"0","dateArr":[{"dateTime":"2020-07-29","taskArr":[{"taskTimeArr":[{"startTimeStr":"08:00","endTimeStr":"08:30"},{"startTimeStr":"08:30","endTimeStr":"09:00"},{"startTimeStr":"09:00","endTimeStr":"09:30"},{"startTimeStr":"09:30","endTimeStr":"10:00"},{"startTimeStr":"10:00","endTimeStr":"10:30"},{"startTimeStr":"10:30","endTimeStr":"11:00"},{"startTimeStr":"11:00","endTimeStr":"11:30"},{"startTimeStr":"11:30","endTimeStr":"12:00"},{"startTimeStr":"12:00","endTimeStr":"12:30"},{"startTimeStr":"12:30","endTimeStr":"13:00"},{"startTimeStr":"13:00","endTimeStr":"13:30"},{"startTimeStr":"13:30","endTimeStr":"14:00"},{"startTimeStr":"14:00","endTimeStr":"14:30"},{"startTimeStr":"14:30","endTimeStr":"15:00"},{"startTimeStr":"15:00","endTimeStr":"15:30"},{"startTimeStr":"15:30","endTimeStr":"16:00"},{"startTimeStr":"16:00","endTimeStr":"16:30"},{"startTimeStr":"16:30","endTimeStr":"17:00"},{"startTimeStr":"17:00","endTimeStr":"17:30"},{"startTimeStr":"17:30","endTimeStr":"18:00"},{"startTimeStr":"18:00","endTimeStr":"18:30"},{"startTimeStr":"18:30","endTimeStr":"19:00"},{"startTimeStr":"19:00","endTimeStr":"19:30"},{"startTimeStr":"19:30","endTimeStr":"20:00"}],"forecastStandard":"turnover","laborStandardBid":"20200805103643877140101b70000025","taskBid":"20200805103820621140401b70000024"},{"taskTimeArr":[{"startTimeStr":"08:00","endTimeStr":"08:30"},{"startTimeStr":"08:30","endTimeStr":"09:00"},{"startTimeStr":"09:00","endTimeStr":"09:30"},{"startTimeStr":"09:30","endTimeStr":"10:00"},{"startTimeStr":"10:00","endTimeStr":"10:30"},{"startTimeStr":"10:30","endTimeStr":"11:00"},{"startTimeStr":"11:00","endTimeStr":"11:30"},{"startTimeStr":"11:30","endTimeStr":"12:00"},{"startTimeStr":"12:00","endTimeStr":"12:30"},{"startTimeStr":"12:30","endTimeStr":"13:00"},{"startTimeStr":"13:00","endTimeStr":"13:30"},{"startTimeStr":"13:30","endTimeStr":"14:00"},{"startTimeStr":"14:00","endTimeStr":"14:30"},{"startTimeStr":"14:30","endTimeStr":"15:00"},{"startTimeStr":"15:00","endTimeStr":"15:30"},{"startTimeStr":"15:30","endTimeStr":"16:00"},{"startTimeStr":"16:00","endTimeStr":"16:30"},{"startTimeStr":"16:30","endTimeStr":"17:00"},{"startTimeStr":"17:00","endTimeStr":"17:30"},{"startTimeStr":"17:30","endTimeStr":"18:00"},{"startTimeStr":"18:00","endTimeStr":"18:30"},{"startTimeStr":"18:30","endTimeStr":"19:00"},{"startTimeStr":"19:00","endTimeStr":"19:30"},{"startTimeStr":"19:30","endTimeStr":"20:00"}],"forecastStandard":"turnover","laborStandardBid":"20200805103643877140101b70000025","taskBid":"20200805103732037140401b70000016"}]},{"dateTime":"2020-07-30","taskArr":[{"taskTimeArr":[{"startTimeStr":"08:00","endTimeStr":"08:30"},{"startTimeStr":"08:30","endTimeStr":"09:00"},{"startTimeStr":"09:00","endTimeStr":"09:30"},{"startTimeStr":"09:30","endTimeStr":"10:00"},{"startTimeStr":"10:00","endTimeStr":"10:30"},{"startTimeStr":"10:30","endTimeStr":"11:00"},{"startTimeStr":"11:00","endTimeStr":"11:30"},{"startTimeStr":"11:30","endTimeStr":"12:00"},{"startTimeStr":"12:00","endTimeStr":"12:30"},{"startTimeStr":"12:30","endTimeStr":"13:00"},{"startTimeStr":"13:00","endTimeStr":"13:30"},{"startTimeStr":"13:30","endTimeStr":"14:00"},{"startTimeStr":"14:00","endTimeStr":"14:30"},{"startTimeStr":"14:30","endTimeStr":"15:00"},{"startTimeStr":"15:00","endTimeStr":"15:30"},{"startTimeStr":"15:30","endTimeStr":"16:00"},{"startTimeStr":"16:00","endTimeStr":"16:30"},{"startTimeStr":"16:30","endTimeStr":"17:00"},{"startTimeStr":"17:00","endTimeStr":"17:30"},{"startTimeStr":"17:30","endTimeStr":"18:00"},{"startTimeStr":"18:00","endTimeStr":"18:30"},{"startTimeStr":"18:30","endTimeStr":"19:00"},{"startTimeStr":"19:00","endTimeStr":"19:30"},{"startTimeStr":"19:30","endTimeStr":"20:00"}],"forecastStandard":"turnover","laborStandardBid":"20200805103643877140101b70000025","taskBid":"20200805103820621140401b70000024"},{"taskTimeArr":[{"startTimeStr":"08:00","endTimeStr":"08:30"},{"startTimeStr":"08:30","endTimeStr":"09:00"},{"startTimeStr":"09:00","endTimeStr":"09:30"},{"startTimeStr":"09:30","endTimeStr":"10:00"},{"startTimeStr":"10:00","endTimeStr":"10:30"},{"startTimeStr":"10:30","endTimeStr":"11:00"},{"startTimeStr":"11:00","endTimeStr":"11:30"},{"startTimeStr":"11:30","endTimeStr":"12:00"},{"startTimeStr":"12:00","endTimeStr":"12:30"},{"startTimeStr":"12:30","endTimeStr":"13:00"},{"startTimeStr":"13:00","endTimeStr":"13:30"},{"startTimeStr":"13:30","endTimeStr":"14:00"},{"startTimeStr":"14:00","endTimeStr":"14:30"},{"startTimeStr":"14:30","endTimeStr":"15:00"},{"startTimeStr":"15:00","endTimeStr":"15:30"},{"startTimeStr":"15:30","endTimeStr":"16:00"},{"startTimeStr":"16:00","endTimeStr":"16:30"},{"startTimeStr":"16:30","endTimeStr":"17:00"},{"startTimeStr":"17:00","endTimeStr":"17:30"},{"startTimeStr":"17:30","endTimeStr":"18:00"},{"startTimeStr":"18:00","endTimeStr":"18:30"},{"startTimeStr":"18:30","endTimeStr":"19:00"},{"startTimeStr":"19:00","endTimeStr":"19:30"},{"startTimeStr":"19:30","endTimeStr":"20:00"}],"forecastStandard":"turnover","laborStandardBid":"20200805103643877140101b70000025","taskBid":"20200805103732037140401b70000016"}]},{"dateTime":"2020-07-31","taskArr":[{"taskTimeArr":[{"startTimeStr":"08:00","endTimeStr":"08:30"},{"startTimeStr":"08:30","endTimeStr":"09:00"},{"startTimeStr":"09:00","endTimeStr":"09:30"},{"startTimeStr":"09:30","endTimeStr":"10:00"},{"startTimeStr":"10:00","endTimeStr":"10:30"},{"startTimeStr":"10:30","endTimeStr":"11:00"},{"startTimeStr":"11:00","endTimeStr":"11:30"},{"startTimeStr":"11:30","endTimeStr":"12:00"},{"startTimeStr":"12:00","endTimeStr":"12:30"},{"startTimeStr":"12:30","endTimeStr":"13:00"},{"startTimeStr":"13:00","endTimeStr":"13:30"},{"startTimeStr":"13:30","endTimeStr":"14:00"},{"startTimeStr":"14:00","endTimeStr":"14:30"},{"startTimeStr":"14:30","endTimeStr":"15:00"},{"startTimeStr":"15:00","endTimeStr":"15:30"},{"startTimeStr":"15:30","endTimeStr":"16:00"},{"startTimeStr":"16:00","endTimeStr":"16:30"},{"startTimeStr":"16:30","endTimeStr":"17:00"},{"startTimeStr":"17:00","endTimeStr":"17:30"},{"startTimeStr":"17:30","endTimeStr":"18:00"},{"startTimeStr":"18:00","endTimeStr":"18:30"},{"startTimeStr":"18:30","endTimeStr":"19:00"},{"startTimeStr":"19:00","endTimeStr":"19:30"},{"startTimeStr":"19:30","endTimeStr":"20:00"}],"forecastStandard":"turnover","laborStandardBid":"20200805103643877140101b70000025","taskBid":"20200805103820621140401b70000024"},{"taskTimeArr":[{"startTimeStr":"08:00","endTimeStr":"08:30"},{"startTimeStr":"08:30","endTimeStr":"09:00"},{"startTimeStr":"09:00","endTimeStr":"09:30"},{"startTimeStr":"09:30","endTimeStr":"10:00"},{"startTimeStr":"10:00","endTimeStr":"10:30"},{"startTimeStr":"10:30","endTimeStr":"11:00"},{"startTimeStr":"11:00","endTimeStr":"11:30"},{"startTimeStr":"11:30","endTimeStr":"12:00"},{"startTimeStr":"12:00","endTimeStr":"12:30"},{"startTimeStr":"12:30","endTimeStr":"13:00"},{"startTimeStr":"13:00","endTimeStr":"13:30"},{"startTimeStr":"13:30","endTimeStr":"14:00"},{"startTimeStr":"14:00","endTimeStr":"14:30"},{"startTimeStr":"14:30","endTimeStr":"15:00"},{"startTimeStr":"15:00","endTimeStr":"15:30"},{"startTimeStr":"15:30","endTimeStr":"16:00"},{"startTimeStr":"16:00","endTimeStr":"16:30"},{"startTimeStr":"16:30","endTimeStr":"17:00"},{"startTimeStr":"17:00","endTimeStr":"17:30"},{"startTimeStr":"17:30","endTimeStr":"18:00"},{"startTimeStr":"18:00","endTimeStr":"18:30"},{"startTimeStr":"18:30","endTimeStr":"19:00"},{"startTimeStr":"19:00","endTimeStr":"19:30"},{"startTimeStr":"19:30","endTimeStr":"20:00"}],"forecastStandard":"turnover","laborStandardBid":"20200805103643877140101b70000025","taskBid":"20200805103732037140401b70000016"}]},{"dateTime":"2020-08-01","taskArr":[{"taskTimeArr":[{"startTimeStr":"08:00","endTimeStr":"08:30"},{"startTimeStr":"08:30","endTimeStr":"09:00"},{"startTimeStr":"09:00","endTimeStr":"09:30"},{"startTimeStr":"09:30","endTimeStr":"10:00"},{"startTimeStr":"10:00","endTimeStr":"10:30"},{"startTimeStr":"10:30","endTimeStr":"11:00"},{"startTimeStr":"11:00","endTimeStr":"11:30"},{"startTimeStr":"11:30","endTimeStr":"12:00"},{"startTimeStr":"12:00","endTimeStr":"12:30"},{"startTimeStr":"12:30","endTimeStr":"13:00"},{"startTimeStr":"13:00","endTimeStr":"13:30"},{"startTimeStr":"13:30","endTimeStr":"14:00"},{"startTimeStr":"14:00","endTimeStr":"14:30"},{"startTimeStr":"14:30","endTimeStr":"15:00"},{"startTimeStr":"15:00","endTimeStr":"15:30"},{"startTimeStr":"15:30","endTimeStr":"16:00"},{"startTimeStr":"16:00","endTimeStr":"16:30"},{"startTimeStr":"16:30","endTimeStr":"17:00"},{"startTimeStr":"17:00","endTimeStr":"17:30"},{"startTimeStr":"17:30","endTimeStr":"18:00"},{"startTimeStr":"18:00","endTimeStr":"18:30"},{"startTimeStr":"18:30","endTimeStr":"19:00"},{"startTimeStr":"19:00","endTimeStr":"19:30"},{"startTimeStr":"19:30","endTimeStr":"20:00"}],"forecastStandard":"turnover","laborStandardBid":"20200805103643877140101b70000025","taskBid":"20200805103820621140401b70000024"},{"taskTimeArr":[{"startTimeStr":"08:00","endTimeStr":"08:30"},{"startTimeStr":"08:30","endTimeStr":"09:00"},{"startTimeStr":"09:00","endTimeStr":"09:30"},{"startTimeStr":"09:30","endTimeStr":"10:00"},{"startTimeStr":"10:00","endTimeStr":"10:30"},{"startTimeStr":"10:30","endTimeStr":"11:00"},{"startTimeStr":"11:00","endTimeStr":"11:30"},{"startTimeStr":"11:30","endTimeStr":"12:00"},{"startTimeStr":"12:00","endTimeStr":"12:30"},{"startTimeStr":"12:30","endTimeStr":"13:00"},{"startTimeStr":"13:00","endTimeStr":"13:30"},{"startTimeStr":"13:30","endTimeStr":"14:00"},{"startTimeStr":"14:00","endTimeStr":"14:30"},{"startTimeStr":"14:30","endTimeStr":"15:00"},{"startTimeStr":"15:00","endTimeStr":"15:30"},{"startTimeStr":"15:30","endTimeStr":"16:00"},{"startTimeStr":"16:00","endTimeStr":"16:30"},{"startTimeStr":"16:30","endTimeStr":"17:00"},{"startTimeStr":"17:00","endTimeStr":"17:30"},{"startTimeStr":"17:30","endTimeStr":"18:00"},{"startTimeStr":"18:00","endTimeStr":"18:30"},{"startTimeStr":"18:30","endTimeStr":"19:00"},{"startTimeStr":"19:00","endTimeStr":"19:30"},{"startTimeStr":"19:30","endTimeStr":"20:00"}],"forecastStandard":"turnover","laborStandardBid":"20200805103643877140101b70000025","taskBid":"20200805103732037140401b70000016"}]},{"dateTime":"2020-08-02","taskArr":[{"taskTimeArr":[{"startTimeStr":"08:00","endTimeStr":"08:30"},{"startTimeStr":"08:30","endTimeStr":"09:00"},{"startTimeStr":"09:00","endTimeStr":"09:30"},{"startTimeStr":"09:30","endTimeStr":"10:00"},{"startTimeStr":"10:00","endTimeStr":"10:30"},{"startTimeStr":"10:30","endTimeStr":"11:00"},{"startTimeStr":"11:00","endTimeStr":"11:30"},{"startTimeStr":"11:30","endTimeStr":"12:00"},{"startTimeStr":"12:00","endTimeStr":"12:30"},{"startTimeStr":"12:30","endTimeStr":"13:00"},{"startTimeStr":"13:00","endTimeStr":"13:30"},{"startTimeStr":"13:30","endTimeStr":"14:00"},{"startTimeStr":"14:00","endTimeStr":"14:30"},{"startTimeStr":"14:30","endTimeStr":"15:00"},{"startTimeStr":"15:00","endTimeStr":"15:30"},{"startTimeStr":"15:30","endTimeStr":"16:00"},{"startTimeStr":"16:00","endTimeStr":"16:30"},{"startTimeStr":"16:30","endTimeStr":"17:00"},{"startTimeStr":"17:00","endTimeStr":"17:30"},{"startTimeStr":"17:30","endTimeStr":"18:00"},{"startTimeStr":"18:00","endTimeStr":"18:30"},{"startTimeStr":"18:30","endTimeStr":"19:00"},{"startTimeStr":"19:00","endTimeStr":"19:30"},{"startTimeStr":"19:30","endTimeStr":"20:00"}],"forecastStandard":"turnover","laborStandardBid":"20200805103643877140101b70000025","taskBid":"20200805103820621140401b70000024"},{"taskTimeArr":[{"startTimeStr":"08:00","endTimeStr":"08:30"},{"startTimeStr":"08:30","endTimeStr":"09:00"},{"startTimeStr":"09:00","endTimeStr":"09:30"},{"startTimeStr":"09:30","endTimeStr":"10:00"},{"startTimeStr":"10:00","endTimeStr":"10:30"},{"startTimeStr":"10:30","endTimeStr":"11:00"},{"startTimeStr":"11:00","endTimeStr":"11:30"},{"startTimeStr":"11:30","endTimeStr":"12:00"},{"startTimeStr":"12:00","endTimeStr":"12:30"},{"startTimeStr":"12:30","endTimeStr":"13:00"},{"startTimeStr":"13:00","endTimeStr":"13:30"},{"startTimeStr":"13:30","endTimeStr":"14:00"},{"startTimeStr":"14:00","endTimeStr":"14:30"},{"startTimeStr":"14:30","endTimeStr":"15:00"},{"startTimeStr":"15:00","endTimeStr":"15:30"},{"startTimeStr":"15:30","endTimeStr":"16:00"},{"startTimeStr":"16:00","endTimeStr":"16:30"},{"startTimeStr":"16:30","endTimeStr":"17:00"},{"startTimeStr":"17:00","endTimeStr":"17:30"},{"startTimeStr":"17:30","endTimeStr":"18:00"},{"startTimeStr":"18:00","endTimeStr":"18:30"},{"startTimeStr":"18:30","endTimeStr":"19:00"},{"startTimeStr":"19:00","endTimeStr":"19:30"},{"startTimeStr":"19:30","endTimeStr":"20:00"}],"forecastStandard":"turnover","laborStandardBid":"20200805103643877140101b70000025","taskBid":"20200805103732037140401b70000016"}]},{"dateTime":"2020-08-03","taskArr":[{"taskTimeArr":[{"startTimeStr":"08:00","endTimeStr":"08:30"},{"startTimeStr":"08:30","endTimeStr":"09:00"},{"startTimeStr":"09:00","endTimeStr":"09:30"},{"startTimeStr":"09:30","endTimeStr":"10:00"},{"startTimeStr":"10:00","endTimeStr":"10:30"},{"startTimeStr":"10:30","endTimeStr":"11:00"},{"startTimeStr":"11:00","endTimeStr":"11:30"},{"startTimeStr":"11:30","endTimeStr":"12:00"},{"startTimeStr":"12:00","endTimeStr":"12:30"},{"startTimeStr":"12:30","endTimeStr":"13:00"},{"startTimeStr":"13:00","endTimeStr":"13:30"},{"startTimeStr":"13:30","endTimeStr":"14:00"},{"startTimeStr":"14:00","endTimeStr":"14:30"},{"startTimeStr":"14:30","endTimeStr":"15:00"},{"startTimeStr":"15:00","endTimeStr":"15:30"},{"startTimeStr":"15:30","endTimeStr":"16:00"},{"startTimeStr":"16:00","endTimeStr":"16:30"},{"startTimeStr":"16:30","endTimeStr":"17:00"},{"startTimeStr":"17:00","endTimeStr":"17:30"},{"startTimeStr":"17:30","endTimeStr":"18:00"},{"startTimeStr":"18:00","endTimeStr":"18:30"},{"startTimeStr":"18:30","endTimeStr":"19:00"},{"startTimeStr":"19:00","endTimeStr":"19:30"},{"startTimeStr":"19:30","endTimeStr":"20:00"}],"forecastStandard":"turnover","laborStandardBid":"20200805103643877140101b70000025","taskBid":"20200805103820621140401b70000024"},{"taskTimeArr":[{"startTimeStr":"08:00","endTimeStr":"08:30"},{"startTimeStr":"08:30","endTimeStr":"09:00"},{"startTimeStr":"09:00","endTimeStr":"09:30"},{"startTimeStr":"09:30","endTimeStr":"10:00"},{"startTimeStr":"10:00","endTimeStr":"10:30"},{"startTimeStr":"10:30","endTimeStr":"11:00"},{"startTimeStr":"11:00","endTimeStr":"11:30"},{"startTimeStr":"11:30","endTimeStr":"12:00"},{"startTimeStr":"12:00","endTimeStr":"12:30"},{"startTimeStr":"12:30","endTimeStr":"13:00"},{"startTimeStr":"13:00","endTimeStr":"13:30"},{"startTimeStr":"13:30","endTimeStr":"14:00"},{"startTimeStr":"14:00","endTimeStr":"14:30"},{"startTimeStr":"14:30","endTimeStr":"15:00"},{"startTimeStr":"15:00","endTimeStr":"15:30"},{"startTimeStr":"15:30","endTimeStr":"16:00"},{"startTimeStr":"16:00","endTimeStr":"16:30"},{"startTimeStr":"16:30","endTimeStr":"17:00"},{"startTimeStr":"17:00","endTimeStr":"17:30"},{"startTimeStr":"17:30","endTimeStr":"18:00"},{"startTimeStr":"18:00","endTimeStr":"18:30"},{"startTimeStr":"18:30","endTimeStr":"19:00"},{"startTimeStr":"19:00","endTimeStr":"19:30"},{"startTimeStr":"19:30","endTimeStr":"20:00"}],"forecastStandard":"turnover","laborStandardBid":"20200805103643877140101b70000025","taskBid":"20200805103732037140401b70000016"}]}],"token":"113ed293f999a5ba81790d6d389a5eb3","cid":60000003}

    cid = test_data.get('cid', '')
    forecast_type = test_data.get('forecastType', '')
    did_arr = test_data.get('didArr', '')
    date_arr = test_data.get('dateArr', [])
    data_after = LaborDbService.labor_standard_forecast_v2(cid, forecast_type, did_arr, date_arr)
    print(data_after)





