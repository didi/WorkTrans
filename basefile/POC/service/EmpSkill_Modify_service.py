"""
第四阶段接口二 ：员工技能修改
by lyy
2019-10-09 14:00
"""
from datetime import datetime
from typing import Dict
from utils.myLogger import infoLog
from POC.model.EmpSkill_db import EmpSkillDB
from tornado import gen
import requests, json
class EmpSkillModifyService:
    @staticmethod
    @gen.coroutine
    def HandleRequest(raw_data:Dict):
        save_result = {'code': 0, 'result': '未处理'}
        cid = str(raw_data.get('cid',''))
        accessToken=raw_data.get('accessToken','')
        callbackBid=raw_data.get('callbackBid','')
        #cid = raw_data.get('cid', '')
        for emp in raw_data['skillData']:
            eid = emp.get('eid','')
            opt = emp.get('opt','')
            skills:list = emp.get('skills','')

            #删除
            # if opt == 'delete':
            #     log_time1 = datetime.now()
            #     res = EmpSkillDB.delete_record(cid, eid)
            #     log_time2 = datetime.now()
            #     infoLog.info('删除耗时: ' + str(log_time2 - log_time1))
            #
            #     if res:
            #         save_result = {'code': 100, 'result': '删除成功'}
            #     else:
            #         save_result = {'code': 101, 'result': '删除失败'}
            #         break
            if opt == 'update':
                save_result = {'code': 100, 'result': '更新成功'}
                del_flag = EmpSkillDB.update_delete_record(cid, eid)
                if del_flag:  # 删除成功，进行插入
                    for skill in skills:
                        skillid = skill.get('skill','')
                        skillNum = skill.get('skillNum','')
                        in_flag = EmpSkillDB.insert_record(cid, eid, skillid, skillNum)
                        if not in_flag:
                            save_result = {'code': 101, 'result': '更新失败'}
                            break
                else:
                    save_result = {'code': 101, 'result': 'DB操作失败'}


        try:
            # #################
            # ## 回调
            # #################
            callbackProgressUrl = raw_data.get('callbackUrl', '')
             #didArr: List = raw_data.get('didArr', [6])

            if "http://" in callbackProgressUrl or "https://" in callbackProgressUrl:
                 callbackProgressUrl = callbackProgressUrl
            else:
                 callbackProgressUrl = "http://" + callbackProgressUrl

            if del_flag:
                callStatus = 1
            else:
                callStatus = 2
            callbackData = {"accessToken": accessToken, "callbackBid": callbackBid, "cid": cid,
                            "type": 1, "callStatus": callStatus}
            infoLog.info('技能修改回调-滴滴请求参数: {}'.format(callbackData))
            headers = {'content-type': 'application/json'}

            json.dumps(callbackData).encode('utf-8')
            response = requests.post(url = callbackProgressUrl, json = callbackData, headers = headers)
            html_code = response.status_code
            infoLog.info('技能修改回调接口-喔趣返回：{}'.format(html_code))
            infoLog.info('技能修改回调接口-喔趣返回数据：{}'.format(response.text))
        except Exception:
            infoLog.info('技能修改回调失败')

        raise gen.Return(save_result)
