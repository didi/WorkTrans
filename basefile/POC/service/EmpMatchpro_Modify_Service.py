"""
第四阶段接口5 ：员工匹配属性修改
by lyy
2019-10-10
"""
from datetime import datetime
from typing import Dict
from utils.myLogger import infoLog
from POC.model.EmpMatchpro_db import EmpMatchproDB
from tornado import gen

class EmpMatchproModifyService:
    @staticmethod
    @gen.coroutine
    def HandleRequest(raw_data:Dict):
        save_result = {'code': 0, 'result': '未处理'}
        cid = raw_data.get('cid','')
        didArr = raw_data.get('didArr','')
        #匹配属性列表不为空，表示有需更新或删除的东西
        #if len(raw_data['matchpros']) != 0:
        #一级操作是删除，则匹配cid did bid，deleteBids，删除符合的记录
        if raw_data['opt'] == 'delete':
            deleteBids = raw_data.get('deleteBids',[])
            log_time1 = datetime.now()
            res = EmpMatchproDB.delete_record_deleteBids(deleteBids, cid)
            log_time2 = datetime.now()
            infoLog.info('删除耗时: ' + str(log_time2 - log_time1))

            if res:
                save_result = {'code': 100, 'result': '删除成功'}
            else:
                save_result = {'code': 101, 'result': '删除失败'}
        else:#一级操作是修改,则将原数据删除，然后插入新数据
            bid = raw_data.get('bid', '')
            for did in didArr:
                flag = 0
                del_res = EmpMatchproDB.delete_record(cid, bid, did)
                # 删除成功，则插入新数据
                if del_res:
                    for item in raw_data['matchpros']:
                        weight = item.get('weight','')
                        ruleGroup = item.get('ruleGroup','')
                        ruleDesc = item.get('ruleDesc','')
                        ruleCpType = item.get('ruleCpType','')
                        ruletag = item.get('ruletag','')
                        ruleCpNum = item.get('ruleCpNum','')
                        res = EmpMatchproDB.insert_record(cid, bid, did,weight,ruleGroup,ruleDesc,ruleCpType,ruletag,ruleCpNum)
                        if not res:#插入数据失败
                            flag = 1
                            break
                else:#删除失败
                    flag = 1

                if flag == 1:
                    break

            if flag == 0:
                save_result = {'code': 100, 'result': '修改成功'}
            else:
                save_result = {'code': 101, 'result': '修改失败'}

        raise gen.Return(save_result)
