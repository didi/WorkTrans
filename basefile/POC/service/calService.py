"""
@author: shenzh
@contact: shenzihan_i@didichuxing.com
@file: calService.py
@time: 2019-10-11 10:48
@desc:
"""
from datetime import datetime
from utils.myLogger import infoLog
from laborCnt.model.man_power_db import ManPowerDB
from POC.model.calDB import CalDB
from utils.dateUtils import DateUtils
from utils.dateTimeProcess import DateTimeProcess
import time
import json
class CalService:

    @staticmethod
    @gen.coroutine
    def doRequest(raw_data):
        save_result = {'code': 0, 'result': '未处理'}
        cid: str = raw_data['cid']
        # applyId: str = raw_data['applyId']
        insert_items = []
        del_items = []
        for entity in raw_data['editData']:
            updateTime = DateUtils.get_now_datetime_str()
            eid: str = entity['eid']
            schDay: str = entity['schDay']
            allWorkTime : str = entity.get('allWorkTime','')
            del_items.append((updateTime,eid,cid,schDay))
            if entity['workUnit'] == []:
                for schme in ['emp', 'worktime', 'fillRate', 'effect', 'violation']:
                    now_datetime = DateUtils.get_now_datetime_str()
                    insert_items.append([cid, '99999999999999999999999999', eid, schDay, '', '', '', '', '', '', '',
                                         'lyb', '', now_datetime, now_datetime, 1, schme])
            else:
                for entity1 in entity['workUnit']:
                    type: str = entity1['type']
                    outId :str = entity1['outId']
                    startTime: str = entity1['startTime'] # "2020-05-02 10:00"
                    endTime: str = entity1['endTime']

                    startTimeStr = startTime.split(' ')[1]
                    endTimeStr = endTime.split(' ')[1]

                    workTime = None
                    if 'workTime' in entity1:
                        workTime = entity1.get('workTime', '')
                    else:
                        workTime:str = str(DateTimeProcess.worktime_interval(start_time=startTimeStr,end_time=endTimeStr,timeSize=0))

                    for schme in ['emp','worktime','fillRate','effect','violation']:
                        now_datetime = DateUtils.get_now_datetime_str()
                        insert_items.append([cid, '99999999999999999999999999', eid, schDay, allWorkTime, type, outId, '', startTimeStr, endTimeStr, workTime, 'lyb', '', now_datetime, now_datetime, 1,schme])

        res = CalService.delete_cal_record(del_items)
        if not res:
            save_result = {'code': 101, 'result': 'DB操作失败(删除失败)'}
            raise gen.Return(save_result)
        print(insert_items)
        res = CalService.update_cal_record_bach(insert_items)
        if res:
            save_result = {'code': 100, 'result': '操作成功'}
        else:
            save_result = {'code': 101, 'result': 'DB操作失败(插入失败)'}

        try:
            # #################
            # ## 回调
            # #################
            callbackProgressUrl = raw_data.get('callbackUrl', '')
            accessToken = raw_data.get('accessToken', '')
            callbackBid = raw_data.get('callbackBid', '')
            # didArr: List = raw_data.get('didArr', [6])

            if "http://" in callbackProgressUrl or "https://" in callbackProgressUrl:
                callbackProgressUrl = callbackProgressUrl
            else:
                callbackProgressUrl = "http://" + callbackProgressUrl

            if res:
                callStatus = 1
            else:
                callStatus = 2

            callbackData = {"accessToken": accessToken, "callbackBid": callbackBid, "cid": cid,
                            "type": 2, "callStatus": callStatus}

            infoLog.info('排班修改回调-滴滴请求参数：{}'.format(callbackData))
            headers = {'content-type': 'application/json'}

            json.dumps(callbackData).encode('utf-8')
            response = requests.post(url = callbackProgressUrl, json = callbackData, headers = headers)
            html_code = response.status_code
            infoLog.info('排班修改回调接口-喔趣返回：{}'.format(html_code))
            infoLog.info('排班修改回调接口-喔趣返回数据：{}'.format(response.text))
        except Exception:
            infoLog.info('排班修改回调失败')

        raise gen.Return(save_result)


    @staticmethod
    def update_cal_record(cid:str,eid:str,schDay:str,allWorkTime:str,type:str,outId:str,startTime:str,endTime:str,workTime:str):
        res = True
        s = datetime.now()
        res = CalDB.insert_cal_record(cid, eid, schDay, allWorkTime, type, outId ,startTime, endTime, workTime)
        e = datetime.now()
        infoLog.info('CalService Update耗时: ' + str(e - s))
        return res

    @staticmethod
    def update_cal_record_bach(items: list):
        res = True
        s = datetime.now()
        res = CalDB.insert_cal_record_bach(items)
        e = datetime.now()
        infoLog.info('update_cal_record_bach CalService Update耗时: ' + str(e - s))
        return res

    @staticmethod
    def delete_cal_record(items):
        res = True
        s = datetime.now()
        res = CalDB.delete_cal_record(items)
        e = datetime.now()
        infoLog.info('CalService Delete耗时: ' + str(e - s))
        return res


if __name__ == '__main__':
    raw_data={"editData":[{"schDay":"2020-07-04","eid":"114955","workUnit":[]}],"timestr":"2020-07-05 00:05:22.082","token":"1b9ae0b3b0d429ff534a42a2ff760e87","cid":60000039}
    print(CalService.doRequest(raw_data))



