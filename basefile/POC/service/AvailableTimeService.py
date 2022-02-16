"""
@author: liyabin
@contact: liyabin_i@didiglobal.com
@file: AvailableTimeService.py
@time: 2019-10-9 14:57
@desc:
"""
from datetime import datetime
from typing import Dict
from utils.myLogger import infoLog
from POC.model.AvailableTimeDB import AvailableTimeDB
from tornado import gen

class AvailableTimeService:

    @staticmethod
    @gen.coroutine
    def doRequest(raw_data:Dict):

        save_result = {'code': 0, 'result': '未处理'}
        cid = str(raw_data['cid'])
        availabletime = raw_data["availabletime"]

        for item in availabletime:
            res = False
            eid = str(item['eid'])
            opt = item['opt']
            day = item["day"]
            # 判断操作类型opt：update、delete
            # 删除操作
            if opt == "delete":
                # 默认删除成功
                save_result = {'code': 100, 'result': '删除成功'}
                res = AvailableTimeService.delete_available_time(cid, eid, day)
                if not res:
                    save_result = {'code': 101, 'result': '删除失败'}
                    break
            # 更新操作
            else:
                # 先进行删除操作
                res = AvailableTimeService.delete_available_time(cid, eid, day)
                if not res:
                    save_result = {'code': 101, 'result': '更新失败(删除失败)'}
                    break

                type = item['type']
                times = item['times']

                if len(times) == 0:
                    # 默认更新成功
                    save_result = {'code': 100, 'result': '更新成功'}
                    res = AvailableTimeDB.insert_record(cid, eid, opt, type, day, "NULL","NULL")
                    if not res:
                        save_result = {'code': 101, 'result': '更新失败'}
                        break

                else:
                    for item2 in times:
                        start = item2["start"]
                        end = item2['end']

                        # 默认更新成功
                        save_result = {'code': 100, 'result': '更新成功'}
                        res = AvailableTimeDB.insert_record(cid,eid,opt,type,day,start,end)
                        if not res:
                            save_result = {'code': 101, 'result': '更新失败'}
                            break

        raise  gen.Return(save_result)

    @staticmethod
    def delete_available_time(cid:str,eid:str,day:str) -> bool:
        '''
        软删除
        :param cid:
        :param eid:
        :param opt:
        :param day:
        :return:
        '''
        res_flag = False
        log_time1 = datetime.now()
        res_flag = AvailableTimeDB.delete_record(cid,eid,day)
        log_time2 = datetime.now()
        infoLog.info('AvailableTimeService delete耗时: ' + str(log_time2 - log_time1))
        return res_flag

    @staticmethod
    def update_available_time(cid:str,eid:str,opt:str,type:str,day:str,start:str,end:str) -> bool:
        res = True
        log_time1 = datetime.now()
        res = AvailableTimeDB.update_record(cid,eid,opt,type,day,start,end)
        log_time2 = datetime.now()
        infoLog.info('AvailableTimeService Update耗时: ' + str(log_time2 - log_time1))
        return res

if __name__ == '__main__':
    data = {"timestr":"2020-04-26 11:26:50.172","availabletime":[{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-01"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-02"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-03"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-04"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-05"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-06"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-07"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-08"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-09"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-10"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-11"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-12"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-13"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-14"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-15"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-16"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-17"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-18"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-19"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-20"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-21"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-22"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-23"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-24"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-25"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-26"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-27"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-28"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-29"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-30"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-01-31"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-02-01"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-02-02"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-02-03"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-02-04"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-02-05"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-02-06"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-02-07"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-02-08"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-02-09"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-02-10"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-02-11"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-02-12"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-02-13"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-02-14"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-02-15"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-02-16"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-02-17"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-02-18"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-02-19"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-02-20"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-02-21"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-02-22"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-02-23"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-02-24"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-02-25"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-02-26"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-02-27"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-02-28"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-02-29"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-03-01"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-03-02"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-03-03"},{"eid":"5358","opt":"update","times":[],"type":"0","day":"2020-03-04"}],"token":"3560e9378a3517afac0c6b9f1d8e7a78","cid":60000004}

    res = AvailableTimeService.doRequest(data)
    print(res)



