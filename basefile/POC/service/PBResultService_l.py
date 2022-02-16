"""
by liyabin
阶段四接口6-获取排班结果
2019-11-14
"""
from typing import Dict,List,Set,Tuple

from POC.bean.CombTasks import CombTasks
from utils.dateTimeProcess import DateTimeProcess
from POC.bean.LaborTask import LaborTask
from POC.service.CombTaskService import CombTaskService
from POC.model.forecast_task_DB import ForecastTaskDB
from POC.bean.EmpComplianceRule import EmpComplianceRule
from POC.service.ComTaskEmpMappingService import ComTaskEmpMappingService
from POC.algorithm.CombTasksEmpMapping import Mapping
from POC.bean.init_emp_record import InitRecord
from POC.service.EmpRecordsService import EmpRecordsService
import datetime
from POC.model.forecast_task_DB import ForecastTaskDB
from utils.myLogger import infoLog
import random

class PBResultService_L:
    @staticmethod
    def doRequest(raw_data: Dict):

        save_result = {'data':{}}

        # 排班类型（任务排班：0、岗位排班：1、组织排班：2）
        schType = str(raw_data.get('schType',"0"))

        if(schType in ['0','1','2']):
            data = PBResultService_L.task_schType(raw_data)
            save_result = {'data': data}
            return save_result

        return save_result

    @staticmethod
    def task_schType(raw_data: Dict,third_rules,all_forecast_days:List[str],quotient_set,employee_records,
                                                         task_all_info, comb_rule_info, shift_split_rule_info,
                                                         emp_info_tuple, callbackData, shiftData, legalityBids,
                                                         emp_matchpro, emps, emp_rule_dict,now_restEid_list,pbDay_realnums,d):
        '''
        工时最少规则
        :param raw_data:
        :return:
        '''
        start_Time = datetime.datetime.now()

        # 排班类型（任务排班：0、岗位排班：1、组织排班：2）
        schType = str(raw_data.get('schType', "0"))
        # 获取排班方案
        scheme = raw_data["scheme"]

        cid = str(raw_data.get('cid',"123456"))
        didArr: List = raw_data.get('didArr', [6])
        applyId = str(raw_data.get('applyId','-1'))
        timeSize = int(raw_data.get('timeInterval',15))

        # 合规性部门规则bids
        legalityBids = raw_data.get("legalityBids", [])
        start = raw_data.get('start','1990-01-01')
        end = raw_data.get('end','1990-01-01')

        # -----------------------读取数据-----------------------
        # 将开始结束日期处理为天数列表
        forecast_days = DateTimeProcess.date_interval(start_day=start, end_day=end)

        # 任务详情，用于虚拟员工排班
        task_info_for_temp_emp = LaborTask.get_laborTask_for_temp_emp(cid=cid, did=str(didArr[0]))

        if third_rules is None:

            comb_rule_list: List = ForecastTaskDB.read_comb_rule_to_list(cid=cid, did=didArr[0])
            shift_split_rule_list: List = ForecastTaskDB.read_labor_shift_split_rule_to_list(cid=cid, did=didArr[0])
            shift_mod_list: List = ForecastTaskDB.read_shift_mod_to_list(cid=cid, did=didArr[0])

            third_rules = {'comb_rule_list':comb_rule_list,'shift_split_rule_list':shift_split_rule_list,'shift_mod_list':shift_mod_list}

        # --------------------读取数据完成---------------------
        # 存储返回员工结果
        cal = []
        # 循环执行日期
        for day_index,day in enumerate(forecast_days):

            # 存取每个可行解
            result_list = []

            repeat_nums = 10
            for i in range(repeat_nums):

                ratio_of_cycles = (i + 1) / repeat_nums
                result_list.append(
                    PBResultService_L.repeated_trials(cid=cid, task_all_info=task_all_info, shiftData=shiftData,
                                                      legalityBids=legalityBids, emps=emps, emp_rule_dict=emp_rule_dict,
                                                      emp_matchpro=emp_matchpro, employee_records=employee_records,
                                                      forecast_day=day, timeSize=int(timeSize),all_forecast_days=all_forecast_days,
                                                      quotient_set=quotient_set,callbackData=callbackData,
                                                      ratio_of_cycles=ratio_of_cycles,emp_info_tuple=emp_info_tuple,now_restEid_list=now_restEid_list))
                print("第%d次排班结果已完成！！！" % i)

            if(scheme == 'fillRate' or scheme == 'effect' ):
                result_list.sort(key=lambda x: x[0], reverse=True)
            elif (scheme == 'worktime'):
                result_list.sort(key=lambda x: x[0], reverse=False)
            elif(scheme == 'emp'):
                result_list.sort(key=lambda x: x[1], reverse=False)
            elif(scheme == 'violation'):
                result_list.sort(key=lambda x: x[2], reverse=False)

            print("已有正式员工的工作总时长（分钟）：%d" % result_list[0][0])
            print("使用的员工人数为：%d" % result_list[0][1])
            pbDay_realnums[d] = result_list[0][1] #每天使用的正式员工人数列表

            # 获取安排完正式员工以后剩余的工作列表
            comb_task_list = result_list[0][5]

            temp_emp_list = None
            try:
                result = CombTasks.get_task_info_by_peroid(cid=cid, did=didArr[0], comb_task_list=comb_task_list,third_rules=third_rules,task_info_for_temp_emp=task_info_for_temp_emp,forecast_day=day,forecastType=schType,timeSize=timeSize)
                no_emp_comb_task_list = CombTasks.get_temp_emp_list(result=result,cid=cid,did=didArr[0],work_date=day,
                                                                    task_all_info=task_all_info,timeSize=timeSize)
                temp_emp_list = Mapping.select_task_to_temp_emp2(no_emp_comb_task_list=no_emp_comb_task_list, work_date=day,
                                                                task_all_info=task_all_info,timeSize=timeSize)
            except Exception as e:
                infoLog.info('虚拟员工排班失败')
                infoLog.info('虚拟员工排班失败原因：%s' % e)
                infoLog.error('虚拟员工排班失败原因：%s' % e)

            temp_emp_workTime = 0
            for t_emp in temp_emp_list:
                temp_emp_workTime += t_emp.dayWorkTime
            print('临时员工的工作总时长为（分钟）：%d' % temp_emp_workTime)
            print('聘用临时工人数为：%d' % len(temp_emp_list))

            # 获取工作记录,用于第二天进行排班校验
            emp_record_list = result_list[0][3]

            # 用于输出员工未排班人员信息
            emp_of_no_work = list(emp_record_list)

            # 合并员工列表
            emp_record_list.extend(temp_emp_list)


            for e in emp_record_list:

                workUnit = []
                allWorkTime = 0
                for task in e.tasks:

                    for i in range(len(task.taskId)):
                        task_id = task.taskId[i]
                        if task_id == 'break':
                            workTime = 0
                        else:
                            workTime = DateTimeProcess.worktime_interval(start_time=task.start[i],
                                                                          end_time=task.end[i],
                                                                          timeSize=timeSize)

                        allWorkTime += workTime
                        workUnit.append({
                            "type": "task",
                            "outId": task_id,
                            "shiftId": "",
                            "startTime": (day + " " + task.start[i]),
                            "endTime": (day + " " + task.end[i]),
                            "workTime": workTime
                        })

                # 工作记录
                emp_work_dict = {
                    "eid":e.eid,
                    "did":e.did,
                    "schDay":day,
                    "allWorkTime":e.dayWorkTime,
                    "workUnit":workUnit
                }
                cal.append(emp_work_dict)

        end_Time = datetime.datetime.now()
        diff = (end_Time - start_Time).seconds
        print("算法耗时为：%f" % diff)

        return_data = {
            "schemes":[
                {"worktime":""}
            ],
            "applyId":applyId,
            "cal":cal
        }

        # 未排班原因
        reasonList = []
        for e in emp_of_no_work:
            if len(e.tasks) == 0:
                reasonList.append({
                    "eid":e.eid,
                    "day":raw_data['start'],
                    "reason": ', '.join(list(map(lambda x:str(x),list(e.forbid_rule_set)))) ,
                })

        # 回调新增统计数据
        return_reason = {
            "scheduledNum": result_list[0][1],
            "notScheduledNum": len(emps) - result_list[0][1],
            "reasonList": reasonList,

        }

        infoLog.info("未排班原因 ： %s" % return_reason)
        return return_data,pbDay_realnums,return_reason

    @staticmethod
    def repeated_trials(cid: str, task_all_info: Dict, shiftData: Dict, legalityBids: List, emps: List,
                        emp_rule_dict: Dict, emp_matchpro: Tuple, employee_records: Dict, forecast_day: str,
                        timeSize: int,all_forecast_days:List[str],quotient_set:set,callbackData:Dict,
                        ratio_of_cycles:float,emp_info_tuple,now_restEid_list):
        comb_tasks_list, emp_list = ComTaskEmpMappingService.get_emp_tasks_info(cid=cid, shiftData=shiftData,
                                                                                legalityBids=legalityBids, emps=emps,
                                                                                forecast_day=forecast_day,
                                                                                task_all_info=task_all_info,
                                                                                emp_matchpro=emp_matchpro,
                                                                                employee_records=employee_records,
                                                                                timeSize=timeSize,emp_info_tuple=emp_info_tuple)
        # print('comb_tasks_list, emp_list', comb_tasks_list, emp_list)
        return Mapping.random_emp_to_comb_tasks(comb_tasks_list=comb_tasks_list, emp_list=emp_list,
                                                emp_rule_dict=emp_rule_dict, emp_matchpro=emp_matchpro,
                                                forecast_day=forecast_day, timeSize=timeSize,
                                                all_forecast_days=all_forecast_days,quotient_set=quotient_set,
                                                callbackData=callbackData,ratio_of_cycles=ratio_of_cycles,now_restEid_list=now_restEid_list,task_all_info=task_all_info)




if __name__ == '__main__':

    raw_data = {"scheme":"worktime","emps":[{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"115716","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"228364","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"235454","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"235460","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"246260","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"195186","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"195199","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"246276","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"246277","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"246282","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"246284","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"195223","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"246288","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"246289","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"246290","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"195237","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"195249","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"195382","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"195385","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"228277","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"114438","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"112459","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"112262","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"111642","hireType":"full","specialTime":[{"startTime":"2019-12-01 19:00","endTime":"2019-12-02 00:00"},{"startTime":"2019-12-01 22:00","endTime":"2019-12-02 00:00"}]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"111612","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"111569","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"110578","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"110576","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"114961","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"112585","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"111596","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"110645","hireType":"full","specialTime":[]},{"legalityBidArr":["2020051818104803214133bbd0000051"],"eid":"110567","hireType":"full","specialTime":[]}],"legalityBids":[],"start":"2019-12-02","bizStartTime":"08:00","timestr":"2020-05-22 09:52:23.100","accessToken":"C57BEC02EB883ECFBAD3A1CB33BBC509","token":"0944ccb725085f262df661885f8f227a","recalculation":True,"schType":"0","applyId":"20200522095222924030139c30000014","callbackProgressUrl":"https://hrec.woqu365.com/forward_webfront/api/schedule-didi/sch/monitor/progress/callback?cod=y1zDxN9NQ_z1bPYzQTzpHQ","calRelyon":"wtForecast","didArr":[6978],"timeInterval":"30","end":"2019-12-02","callbackUrl":"https://hrec.woqu365.com/forward_webfront/api/schedule-didi/sch/cal/callback?cod=y1zDxN9NQ_z1bPYzQTzpHQ","cid":50000735,"bizEndTime":"00:00"}
    s = set()
    #s.add(1.0)
    res = PBResultService_L.task_schType(raw_data,None,["2020-01-01","2020-01-01"],s)
    print(res)