'''
create by liyabin
'''

from typing import List,Dict,Tuple,Set
from POC.model.forecast_task_DB import ForecastTaskDB

class LaborTask:
    @staticmethod
    def get_laborTask_info(cid:str) ->Dict:
        '''
        任务详情的 部分数据
        :param cid:
        :return:
        '''
        task_tuple = ForecastTaskDB.read_laborTask_info(cid)
        task_dict = {}
        #a.cid,a.did,a.bid,b.taskName,b.abCode,b.taskType,b.worktimeType,b.worktimeStart,b.worktimeEnd,a.taskSkillBids,a.skillNums,a.certs
        for item in task_tuple:
            # [taskName,taskSkillBids,skillNums,certs]
            task_info:List[str,str,str,str] = []

            taskBid = item[2]
            taskName = item[3]
            taskSkillBids = item[9]
            skillNums = item[10]
            certs = item[11]
            task_info.append(taskName)
            task_info.append(taskSkillBids)
            task_info.append(skillNums)
            task_info.append(certs)
            task_dict[taskBid] = task_info

        return task_dict

    @staticmethod
    def get_laborTask_all_info(cid:str,did:str) ->Dict:
        '''
        任务详情 全部数据
        :param cid:
        :return:
        '''
        task_tuple = ForecastTaskDB.read_laborTask_info(cid,did)
        task_dict = {}
        #a.cid,a.did,a.bid,b.taskName,b.abCode,b.taskType,b.worktimeType,b.worktimeStart,b.worktimeEnd,a.taskSkillBids,a.skillNums,a.certs
        for item in task_tuple:
            # [taskName,taskSkillBids,skillNums,certs]
            task_all_info = {}

            task_all_info["cid"] = item[0]
            task_all_info["did"] = item[1]
            task_all_info["taskBid"] = item[2]
            task_all_info["taskName"] = item[3]
            task_all_info["abCode"] = item[4]
            task_all_info["taskType"] = item[5]
            task_all_info["worktimeType"] = item[6]
            task_all_info["taskSkillBids"] = item[9]
            task_all_info["skillNums"] = item[10]
            task_all_info["certs"] = item[11]

            taskBid = task_all_info["taskBid"]
            task_dict[taskBid] = task_all_info

        return task_dict

    @staticmethod
    def get_laborTask_for_temp_emp(cid: str, did: str) -> Dict:
        '''
        任务详情 全部数据
        :param cid:
        :return:
        '''

        # `cid`,`did`,`bid`,`fillCoefficient`,`discard`,`taskMinWorkTime`,`taskMaxWorkTime`
        task_tuple = ForecastTaskDB.read_laborTask_for_temp_emp(cid, did)
        task_dict = {}
        for item in task_tuple:

            item_cid = item[0]
            item_did = item[1]
            item_bid = item[2]
            item_fillCoefficient = item[3]
            item_discard = True if item[4] == '1' else False
            item_taskMinWorkTime = item[5]
            item_taskMaxWorkTime = item[6]

            task_dict[item_cid+item_did+item_bid] = [item_fillCoefficient,item_discard,item_taskMinWorkTime,item_taskMaxWorkTime]

        return task_dict

if __name__ == '__main__':
    #print(LaborTask.get_laborTask_all_info(cid="51000447",did='22'))

    print(LaborTask.get_laborTask_for_temp_emp(cid="11111",did='1'))
