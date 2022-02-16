'''
create by liyabin
'''

from POC.bean.Employee import Employee
from POC.bean.CombTasks import CombTasks
from typing import List,Dict,Tuple
from utils.dateTimeProcess import DateTimeProcess
from POC.algorithm.CombTasksEmpMapping import Mapping
import csv
from POC.service.CombTaskService import CombTaskService
import os

class ComTaskEmpMappingService:
    @staticmethod
    def get_emp_tasks_info(cid: str, shiftData: Dict, legalityBids: List, emps: List, forecast_day: str,
                           task_all_info: Dict, emp_matchpro:Tuple,employee_records: Dict, timeSize: int,emp_info_tuple) -> Tuple[List, List]:
        '''
        :param forecast_day: 预测日期
        :param timeSize: 时间粒度
        :return:
        '''

        #
        comb_tasks_list = CombTasks.get_comb_tasks_info(data=shiftData, forecast_day=forecast_day,
                                                        task_all_info=task_all_info, timeSize=timeSize)

        # 员工字
        emp_list = Employee.get_emp_info_list(cid=cid, legalityBids=legalityBids, emps=emps, forecast_day=forecast_day,
                                              task_all_info=task_all_info,emp_matchpro=emp_matchpro, employee_records=employee_records,
                                              timeSize=timeSize,emp_info_tuple=emp_info_tuple)

        return comb_tasks_list, emp_list

    @staticmethod
    def write_result_to_csv(emp_list: List,emp_matchpro: Tuple, date: str,timeSize:int):

        with open("/Users/didi/PycharmProjects/woqu6/basefile/POC/new2_" + date + ".csv", "w", encoding='utf-8-sig') as csvfile:
        #with open("/home/xiaoju/woqu/basefile/POC/service/new_" + date + ".csv", "w",encoding='utf-8-sig') as csvfile:

            writer = csv.writer(csvfile)
            # 添加标题
            title = ["eid"]
            title.extend(DateTimeProcess.print_timeList_of_day_and_timeSize(timeSize=timeSize))
            writer.writerow(title)

            for emp in emp_list:
                info = ["", ] * (24 * 60 // timeSize + 1)
                info[0] = emp.eid
                for task in emp.tasks:
                    # taskCombination = task.taskCombination

                    timeStrList = []
                    for _ in range(len(task.start)):
                        start = task.start[_]
                        end = task.end[_]

                        start_end = start + "-" + end
                        timeStrList.append(start_end)

                    timeStrList = DateTimeProcess.timeStr_to_timeList(timeStrList, timeSize)

                    # 控制输出的索引
                    taskNameList_index = 0
                    for i in range(len(timeStrList)):
                        if (timeStrList[i] == 1):

                            if taskNameList_index >= len(task.taskName_list): continue

                            info[i + 1] = task.taskName_list[taskNameList_index] #if len(task.taskName_list) > 0  else "休息"
                            taskNameList_index += 1

                writer.writerow(info)

            # for t_e in temp_emp_list:
            #     info = ["", ] * (24 * 60 // timeSize + 1)
            #     info[0] = t_e.eid
            #     for task in t_e.tasks:
            #         # taskCombination = task.taskCombination
            #         #if(task.worktime_minutes <= 60):continue
            #
            #         timeStrList = []
            #         for _ in range(len(task.start)):
            #             start = task.start[_]
            #             end = task.end[_]
            #
            #             start_end = start + "-" + end
            #             timeStrList.append(start_end)
            #
            #         timeStrList = DateTimeProcess.timeStr_to_timeList(timeStrList, timeSize)
            #
            #         # 控制输出的索引
            #         taskNameList_index = 0
            #         for i in range(len(timeStrList)):
            #             if (timeStrList[i] == 1):
            #                 info[i + 1] = task.taskName_list[taskNameList_index]
            #                 taskNameList_index += 1
            #
            #     writer.writerow(info)
        print("已完成")