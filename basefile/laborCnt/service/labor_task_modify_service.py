"""
@author: liyabin
@contact: liyabin_i@didiglobal.com
@file: ManPowerCls.py
@time: 2019-09-16 13:19
@desc:
"""
from datetime import datetime
from typing import Dict
from utils.myLogger import infoLog
from laborCnt.model.labor_task_db import LaborTaskDB

class LaborTaskModifyService:

    @staticmethod
    @gen.coroutine
    def doRequest(raw_data:Dict):

        save_result = {'code': 0, 'result': '未处理'}
        cid = raw_data['cid']
        for entity in raw_data['taskDetail']:
            opt = entity['opt']
            bid = entity['bid']
            # delete操作
            if opt == 'delete':
                res = LaborTaskModifyService.Labor_task_delete(cid, bid)
                if res:
                    save_result = {'code': 100, 'result': '删除成功'}
                else:
                    save_result = {'code': 101, 'result': '删除失败'}
            elif opt == 'update':
                # 先删除cid + bid 的所有记录
                LaborTaskModifyService.Labor_task_delete(cid, bid)
                for did in entity['didArr']:
                    bid = entity['bid']
                    # update操作
                    res = LaborTaskModifyService.Labor_task_modify(cid, str(did), bid, entity)
                    if res:
                        save_result = {'code': 100, 'result': '操作成功'}
                    else:
                        save_result = {'code': 101, 'result': 'DB操作失败'}

        raise gen.Return(save_result)

    @staticmethod
    def Labor_task_delete(cid:str,bid:str):
        '''
        软删除
        :param cid:
        :param bid:
        :return:
        '''
        res_flag = True
        log_time1 = datetime.now()
        res_flag = LaborTaskDB.delete_laborrecord(cid,bid)
        log_time2 = datetime.now()
        infoLog.info('外层删除耗时: ' + str(log_time2 - log_time1))
        return res_flag

    @staticmethod
    def Labor_task_modify(cid:str, did:str, bid:str, entity:Dict):
        '''
        修改操作
        :param cid:
        :param did:
        :param bid:
        :param entity:
        :return:
        '''
        res_flag = False

        taskName = entity.get('taskName','')
        abCode = entity.get('abCode','')
        taskType = entity.get('taskType','')

        # 填补系数
        fillCoefficient = entity.get('fillCoefficient','')
        # 是否可以舍弃， 1可以  2不可以
        discard :int = entity.get('discard', '')
        # 最小任务时长
        taskMinWorkTime = entity.get('taskMinWorkTime','')
        # 最大任务时长
        taskMaxWorkTime = entity.get('taskMaxWorkTime','')

        opt = entity['opt']

        for wtd in entity['worktimeData']:
            worktimeType = wtd['worktimeType']
            worktimeStart = wtd['worktimeStart']
            worktimeEnd = wtd.get('worktimeEnd', '')
            certs = entity.get("certs", [])
            if certs:
                row_influenced = LaborTaskDB.select_record_exist(cid, bid, did)
                if row_influenced:
                    res_flag = LaborTaskDB.delete_record(cid, bid, did)
                for tk in entity['taskSkill']:
                    taskSkillBid = tk['taskSkillBid']
                    skillNum = tk['skillNum']
                    for cert in entity.get("certs", []):
                        res_flag = LaborTaskDB.update_record(cid, did, bid, taskName, abCode, taskType, opt,
                                                             worktimeType, worktimeStart, worktimeEnd, taskSkillBid,
                                                             skillNum, cert,fillCoefficient,discard,taskMinWorkTime,taskMaxWorkTime)
            else:
                row_influenced = LaborTaskDB.select_record_exist(cid, bid, did)
                if row_influenced:
                    LaborTaskDB.delete_record(cid, bid, did)
                for tk in entity['taskSkill']:
                    taskSkillBid = tk['taskSkillBid']
                    skillNum = tk['skillNum']
                    res_flag = LaborTaskDB.update_record_for_noCerts(cid, did, bid, taskName, abCode, taskType, opt,
                                                                     worktimeType,
                                                                     worktimeStart, worktimeEnd, taskSkillBid, skillNum,
                                                                     fillCoefficient, discard, taskMinWorkTime,
                                                                     taskMaxWorkTime)

        return res_flag

if __name__ == '__main__':
    data = {"taskDetail":[{"fillCoefficient":"1","discard":2,"abCode":"Other","taskMaxWorkTime":"0","certs":[],"taskType":"indirectwh","opt":"update","taskSkill":[{"taskSkillBid":"20200509091157474147439a70001230","skillNum":"10"},{"taskSkillBid":"20200509091157492147439a70001246","skillNum":"10"}],"didArr":[32,52,42,14,62,14,32,42,52,62],"taskName":"补货换图等操作","worktimeData":[{"worktimeEnd":"22:00","worktimeType":"bisTime","worktimeStart":"08:00"}],"taskMinWorkTime":"0","bid":"20200508191436446140437700000086"},{"fillCoefficient":"1","discard":2,"abCode":"CLOSE","taskMaxWorkTime":"0","certs":[],"taskType":"fixedwh","opt":"update","taskSkill":[{"taskSkillBid":"20200509091157439147439a70001212","skillNum":"10"},{"taskSkillBid":"20200509091157474147439a70001230","skillNum":"10"}],"didArr":[32,52,42,14,14,32,42,52],"taskName":"闭店","worktimeData":[{"worktimeEnd":"22:00","worktimeType":"customTime","worktimeStart":"21:30"}],"taskMinWorkTime":"0","bid":"20200508174806985140439480000062"},{"fillCoefficient":"1","discard":2,"taskType":"fixedwh","opt":"update","abCode":"565JH","taskSkill":[{"taskSkillBid":"20200509091157509147439a70001250","skillNum":"10"},{"taskSkillBid":"20200509091157421147439a70001200","skillNum":"10"},{"taskSkillBid":"20200509091157492147439a70001246","skillNum":"10"}],"didArr":[14,14],"taskName":"开店接货 - 565","worktimeData":[{"worktimeEnd":"10:00","worktimeType":"customTime","worktimeStart":"08:00"}],"bid":"20200508173400534140439480000053","certs":[]},{"fillCoefficient":"1","discard":2,"taskType":"directwh","opt":"update","abCode":"S","taskSkill":[{"taskSkillBid":"20200509091157457147439a70001224","skillNum":"10"},{"taskSkillBid":"20200508202639808147439a70000960","skillNum":"10"},{"taskSkillBid":"20200509091157474147439a70001230","skillNum":"10"}],"didArr":[32,52,42,14,62,14,32,42,52,62],"taskName":"服务销售+收银+补货","worktimeData":[{"worktimeEnd":"22:00","worktimeType":"bisTime","worktimeStart":"08:00"}],"bid":"2020050617274685414043b350000164","certs":[]}],"timestr":"2020-05-09 15:46:26.373","token":"8c99ebca7113c4f2fad8d048a4467e4c","cid":50000799}


    res = LaborTaskModifyService.doRequest(data)
    print(res)

