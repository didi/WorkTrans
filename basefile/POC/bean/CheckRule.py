'''
create by liyabin
'''

from typing import Dict,Tuple,List,Set
from POC.bean.Employee import Employee
from POC.bean.CombTasks import CombTasks
import datetime,calendar
import numpy as np
from utils.myLogger import infoLog


# 校验规则
class CheckRule:



    @staticmethod
    def get_tasks_from_combtasks(tasks: CombTasks):
        '''
        从CombTasks中拆出任务
        worktimeList = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        taskName_list = ['开早（厨房）', '开早（厨房）', '开早（厨房）', '吃饭', '设备周清', '设备周清', '设备周清', '吃饭', '设备周清', '设备周清', '设备周清',
                         '设备周清', '设备周清', '设备周清', '设备周清', '设备周清']
        :return:
        '''
        worktimeList = tasks.worktimeList
        taskName_list = tasks.taskName_list
        b = []
        if len(worktimeList) == 48:
            b = ['00:00', '00:30', '01:00', '01:30', '02:00', '02:30', '03:00', '03:30', '04:00', '04:30', '05:00',
                 '05:30', '06:00', '06:30', '07:00', '07:30', '08:00', '08:30', '09:00', '09:30', '10:00', '10:30',
                 '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00',
                 '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30',
                 '22:00', '22:30', '23:00', '23:30', '00:00']
        elif len(worktimeList) == 96:
            b = ['00:00', '00:15', '00:30', '00:45', '01:00', '01:15', '01:30', '01:45', '02:00', '02:15', '02:30',
                 '02:45', '03:00', '03:15', '03:30', '03:45', '04:00', '04:15', '04:30', '04:45', '05:00', '05:15',
                 '05:30', '05:45', '06:00', '06:15', '06:30', '06:45', '07:00', '07:15', '07:30', '07:45', '08:00',
                 '08:15', '08:30', '08:45', '09:00', '09:15', '09:30', '09:45', '10:00', '10:15', '10:30', '10:45',
                 '11:00', '11:15', '11:30', '11:45', '12:00', '12:15', '12:30', '12:45', '13:00', '13:15', '13:30',
                 '13:45', '14:00', '14:15', '14:30', '14:45', '15:00', '15:15', '15:30', '15:45', '16:00', '16:15',
                 '16:30', '16:45', '17:00', '17:15', '17:30', '17:45', '18:00', '18:15', '18:30', '18:45', '19:00',
                 '19:15', '19:30', '19:45', '20:00', '20:15', '20:30', '20:45', '21:00', '21:15', '21:30', '21:45',
                 '22:00', '22:15', '22:30', '22:45', '23:00', '23:15', '23:30', '23:45', '00:00']
        elif len(worktimeList) == 24:
            b = ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00',
                 '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00',
                 '22:00', '23:00', '00:00']

        taskDict = {}

        j = 0
        lastname = ''
        starttime = ''
        endtime = ''
        for inx, i in enumerate(worktimeList):
            if i == 1:
                taskname = taskName_list[j]
                if lastname == '':
                    starttime = b[inx]
                    lastname = taskname
                if taskname != lastname:
                    endtime = b[inx + 1]
                    if lastname not in taskDict:
                        taskDict[lastname] = '%s-%s' % (starttime, endtime)
                    else:
                        old = taskDict.get(lastname)
                        new = ('%s+%s-%s' % (old, starttime, endtime))
                        taskDict[lastname] = new
                    starttime = b[inx + 1]
                    lastname = taskname
                else:
                    endtime = b[inx + 1]
                j += 1
        if lastname not in taskDict:
            taskDict[lastname] = '%s-%s' % (starttime, endtime)
        else:
            old = taskDict.get(lastname)
            new = ('%s+%s-%s' % (old, starttime, endtime))
            taskDict[lastname] = new
        return taskDict

    @staticmethod
    def check_skill_and_cert_requirements(emp: Employee, tasks: CombTasks,forecast_day:str,task_all_info:Dict):
        '''
        校验技能、证书是否满足
        :param emp:
        :param tasks:
        :return:
        '''

        isMatch = True
        rule_str = ''

        taskDict = CheckRule.get_tasks_from_combtasks(tasks)

        for i,taskSkillBid in enumerate(tasks.taskSkillBid_list):
            skillNum = tasks.skillNum_list[i]
            if taskSkillBid == 'break':
                continue
            
            if taskSkillBid in emp.skill:
                j = emp.skill.index(taskSkillBid)
                emp_skillNum = emp.skillNum[j]
                if ((int(float(emp_skillNum)) < int(float(skillNum)))):
                    isMatch = False
                    taskName = ''
                    for taskBid in task_all_info:
                        taskBidDict = task_all_info[taskBid]
                        if taskBidDict['taskSkillBids'].find(taskSkillBid) >= 0 and taskBidDict['taskName'] in tasks.taskName_list:
                            taskName = taskBidDict['taskName']
                    rule_str = '%s:%s.员工完成%s任务的技能值不够' %(taskName,taskDict.get(taskName,'时间-miss'),taskName)
            else:
                isMatch = False
                taskName=''

                for taskBid in task_all_info:
                    taskBidDict = task_all_info[taskBid]
                    if taskBidDict['taskSkillBids'].find(taskSkillBid) >= 0 and taskBidDict['taskName'] in tasks.taskName_list:
                        taskName = taskBidDict['taskName']
                rule_str = '%s:%s.员工缺少完成%s任务的技能' %(taskName, taskDict.get(taskName, '时间-miss'), taskName)

        for cert in tasks.cert_list:
            if cert == '':
                continue
            if cert not in emp.cret_closingdate.keys():
                isMatch = False
                rule_str = '证书不符'
            elif emp.cret_closingdate[cert] < datetime.datetime.strptime(forecast_day,"%Y-%m-%d"):
                isMatch = False
                rule_str = '证书无效'

        return isMatch,rule_str

    @staticmethod
    def check_worktime_rule(emp: Employee, emp_rule_dict:Dict, worktime_minutes: int, forecast_day: str,break_rule_num:int,break_rule_list:List,taskName_list:List):
        '''
        检测员工日工时 从字典中读取  加载一次
        :param emp:
        :param forecast_day:
        :return:
        '''

        cid = emp.cid
        eid = emp.eid

        bids = emp.bids
        forecast_day = datetime.datetime.strptime(forecast_day, "%Y-%m-%d")

        for bid in bids:
            emp_compliance_key = cid + "-" + bid

            for rule_d in emp_rule_dict.get(emp_compliance_key, []):

                ruleType = rule_d["ruleType"]
                ruletag = rule_d["ruletag"]

                # 班次工时 合规性
                if (ruleType == "timerule" and ruletag == "shiftTime"):

                    startDate = rule_d["startDate"]
                    timeRange = rule_d["timeRange"]
                    cycle = rule_d["cycle"]

                    # 天工时
                    if (cycle == "day" and forecast_day >= datetime.datetime.strptime(str(startDate),'%Y-%m-%d')):
                        ruleCpType = rule_d["ruleCpType"]
                        ruleCpNum = rule_d["ruleCpNum"]

                        if (ruleCpType == "lt" and (emp.dayWorkTime + worktime_minutes) < int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                infoLog.info("(%s)违反天工作时长小于%s的规则" %('-'.join(taskName_list),ruleCpNum))
                                rule_str = "(%s)违反天工作时长小于%s的规则" %('-'.join(taskName_list),ruleCpNum)
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False

                        if (ruleCpType == "gt" and (emp.dayWorkTime + worktime_minutes) > int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                infoLog.info("(%s)违反天工作时长大于%s的规则" % ('-'.join(taskName_list), ruleCpNum))
                                rule_str = "(%s)违反天工作时长大于%s的规则" % ('-'.join(taskName_list), ruleCpNum)
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False

                        if (ruleCpType == "ge" and (emp.dayWorkTime + worktime_minutes) >= int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                infoLog.info("(%s)违反天工作时长大于等于%s的规则" % ('-'.join(taskName_list), ruleCpNum))
                                rule_str = "(%s)违反天工作时长大于等于%s的规则" % ('-'.join(taskName_list), ruleCpNum)
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False

                        if (ruleCpType == "eq" and (emp.dayWorkTime + worktime_minutes) == int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                infoLog.info("(%s)违反天工作时长等于%s的规则" % ('-'.join(taskName_list), ruleCpNum))
                                rule_str = "(%s)违反天工作时长等于%s的规则" % ('-'.join(taskName_list), ruleCpNum)
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False

                        if (ruleCpType == "le" and (emp.dayWorkTime + worktime_minutes) <= int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                infoLog.info("(%s)违反天工作时长小于等于%s的规则" % ('-'.join(taskName_list), ruleCpNum))
                                rule_str = "(%s)违反天工作时长小于等于%s的规则" % ('-'.join(taskName_list), ruleCpNum)
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False

                    # 周工时
                    if(cycle == "week" and forecast_day >= datetime.datetime.strptime(str(startDate),'%Y-%m-%d')):
                        ruleCpType = rule_d["ruleCpType"]
                        ruleCpNum = rule_d["ruleCpNum"]

                        if (ruleCpType == "gt" and (emp.weekWorkTime + worktime_minutes) > int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                infoLog.info("%s违反周工作时长大于%s的规则" % ('-'.join(taskName_list), ruleCpNum))
                                rule_str = "(%s)违反周工作时长大于%s的规则" % ('-'.join(taskName_list), ruleCpNum)
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False

                        if (ruleCpType == "ge" and (emp.weekWorkTime + worktime_minutes) >= int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                infoLog.info("%s违反周工作时长大于等于%s的规则" % ('-'.join(taskName_list), ruleCpNum))
                                rule_str = "(%s)违反周工作时长大于等于%s的规则" % ('-'.join(taskName_list), ruleCpNum)
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False

                        if (ruleCpType == "eq" and (emp.weekWorkTime + worktime_minutes) == int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                infoLog.info("%s违反周工作时长等于%s的规则" % ('-'.join(taskName_list), ruleCpNum))
                                rule_str = "(%s)违反周工作时长等于%s的规则" % ('-'.join(taskName_list), ruleCpNum)
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False

                        if (ruleCpType == "le" and (emp.weekWorkTime + worktime_minutes) <= int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                infoLog.info("%s违反周工作时长小于等于%s的规则" % ('-'.join(taskName_list), ruleCpNum))
                                rule_str = "(%s)违反周工作时长小于等于%s的规则" % ('-'.join(taskName_list), ruleCpNum)
                                emp.forbid_rule_set.add(rule_str)

                                return 0, False

                        if (ruleCpType == "lt" and (emp.weekWorkTime + worktime_minutes) < int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                infoLog.info("%s违反周工作时长小于%s的规则" % ('-'.join(taskName_list), ruleCpNum))
                                rule_str = "(%s)违反周工作时长小于%s的规则" % ('-'.join(taskName_list), ruleCpNum)
                                emp.forbid_rule_set.add(rule_str)

                                return 0, False
                    # 月工时
                    if(cycle == "month"):
                        # 获取预测日期该月的天数
                        days = 0
                        for i in range(0, int(timeRange)):
                            days += calendar.monthrange(forecast_day.year, forecast_day.month + i)[1]
                        if forecast_day >= datetime.datetime.strptime(str(startDate),'%Y-%m-%d'):
                            ruleCpType = rule_d["ruleCpType"]
                            ruleCpNum = rule_d["ruleCpNum"]

                            if (ruleCpType == "gt" and (emp.monthWorkTime + worktime_minutes) > int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    infoLog.info("%s违反月工作时长大于%s的规则" % ('-'.join(taskName_list), ruleCpNum))
                                    rule_str = "(%s)违反月工作时长大于%s的规则" % ('-'.join(taskName_list), ruleCpNum)
                                    emp.forbid_rule_set.add(rule_str)

                                    return 0, False

                            elif (ruleCpType == "ge" and (emp.monthWorkTime + worktime_minutes) >= int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    infoLog.info("%s违反月工作时长等于%s的规则" % ('-'.join(taskName_list), ruleCpNum))
                                    rule_str = "(%s)违反月工作时长等于%s的规则" % ('-'.join(taskName_list), ruleCpNum)
                                    emp.forbid_rule_set.add(rule_str)

                                    return 0, False
                            elif (ruleCpType == "eq" and (emp.monthWorkTime + worktime_minutes) == int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    infoLog.info("%s违反月工作时长等于%s的规则" % ('-'.join(taskName_list), ruleCpNum))
                                    rule_str = "(%s)违反月工作时长等于%s的规则" % ('-'.join(taskName_list), ruleCpNum)
                                    emp.forbid_rule_set.add(rule_str)

                                    return 0, False
                            elif (ruleCpType == "le" and (emp.monthWorkTime + worktime_minutes) <= int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    infoLog.info("%s违反月工作时长小于等于%s的规则" % ('-'.join(taskName_list), ruleCpNum))
                                    rule_str = "(%s)违反周工作时长小于等于%s的规则" % ('-'.join(taskName_list), ruleCpNum)
                                    emp.forbid_rule_set.add(rule_str)

                                    return 0, False
                            elif (ruleCpType == "lt" and (emp.monthWorkTime + worktime_minutes) < int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    infoLog.info("%s违反月工作时长小于%s的规则" % ('-'.join(taskName_list), ruleCpNum))
                                    rule_str = "(%s)违反月工作时长小于%s的规则" % ('-'.join(taskName_list), ruleCpNum)
                                    emp.forbid_rule_set.add(rule_str)

                                    return 0, False
        return break_rule_num,True

    @staticmethod
    def check_shift_len(emp:Employee,task:CombTasks,emp_rule_dict:Dict,forecast_day:str,break_rule_num:int,break_rule_list:List):
        '''
        班次长度
        :param emp:
        :param emp_rule_dict:
        :param forecast_day:
        :return:
        '''
        cid = emp.cid
        eid = emp.eid
        bids = emp.bids

        forecast_day = datetime.datetime.strptime(forecast_day, "%Y-%m-%d")

        for bid in bids:
            emp_compliance_key = cid + "-" + bid
            #print("eid,check_shift_len ---- ", eid)
            for rule_d in emp_rule_dict.get(emp_compliance_key, []):

                ruleType = rule_d["ruleType"]
                ruletag = rule_d["ruletag"]

                # 班次长度 合规性
                if (ruleType == "shiftrule" and ruletag == "shiftLen"):

                    startDate = rule_d["startDate"]
                    timeRange = rule_d["timeRange"]
                    cycle = rule_d["cycle"]

                    # day班次长度
                    if (cycle == "day" and forecast_day >= datetime.datetime.strptime(str(startDate),'%Y-%m-%d')):
                        ruleCpType = rule_d["ruleCpType"]
                        ruleCpNum = rule_d["ruleCpNum"]
                        if (ruleCpType == "lt" and task.worktime_minutes < int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                start = task.start[0]
                                end = task.end[-1]
                                t_name = '-'.join(task.taskName_list)
                                rule_str = "班次开始结束(%s-%s)任务列表(%s)长度(%s) 违反天班次长度小于%s的规则" % (start,end,t_name,task.worktime_minutes,ruleCpNum)
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "le" and task.worktime_minutes <= int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                start = task.start[0]
                                end = task.end[-1]
                                t_name = '-'.join(task.taskName_list)
                                rule_str = "班次开始结束(%s-%s)任务列表(%s)长度(%s) 违反天班次长度小于等于%s的规则" % (
                                start, end, t_name, task.worktime_minutes, ruleCpNum)
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "eq" and task.worktime_minutes == int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                start = task.start[0]
                                end = task.end[-1]
                                t_name = '-'.join(task.taskName_list)
                                rule_str = "班次开始结束(%s-%s)任务列表(%s)长度(%s) 违反天班次长度等于%s的规则" % (
                                    start, end, t_name, task.worktime_minutes, ruleCpNum)
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "ge" and task.worktime_minutes >= int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                start = task.start[0]
                                end = task.end[-1]
                                t_name = '-'.join(task.taskName_list)
                                rule_str = "班次开始结束(%s-%s)任务列表(%s)长度(%s) 违反天班次长度大于等于%s的规则" % (
                                    start, end, t_name, task.worktime_minutes, ruleCpNum)
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "gt" and task.worktime_minutes > int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                start = task.start[0]
                                end = task.end[-1]
                                t_name = '-'.join(task.taskName_list)
                                rule_str = "班次开始结束(%s-%s)任务列表(%s)长度(%s) 违反天班次长度大于%s的规则" % (
                                    start, end, t_name, task.worktime_minutes, ruleCpNum)
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
        return break_rule_num,True

    @staticmethod
    def check_shift_interval(emp:Employee,task:CombTasks,emp_rule_dict:Dict,forecast_day:str,timeSize:int,break_rule_num:int,break_rule_list:List):
        '''
        班次间隔
        :param emp:
        :param task:
        :param emp_rule_dict:
        :param forecast_day:
        :return:
        '''
        cid = emp.cid
        # eid = emp.eid
        bids = emp.bids
        forecast_day = datetime.datetime.strptime(forecast_day, "%Y-%m-%d")

        for bid in bids:
            emp_compliance_key = cid + "-" + bid

            # 该员工没有排任务时
            if(len(emp.tasks) == 0):
                return 0,True

            # 该员工存在已排任务，在考虑以下步骤
            for rule_d in emp_rule_dict.get(emp_compliance_key, []):
                ruleType = rule_d["ruleType"]
                ruletag = rule_d["ruletag"]

                if(ruleType == "shiftrule" and ruletag == 'interval'):
                    startDate = rule_d["startDate"]
                    timeRange = rule_d["timeRange"]
                    cycle = rule_d["cycle"]

                    if (cycle == "day" and forecast_day >= datetime.datetime.strptime(str(startDate),'%Y-%m-%d')):
                        ruleCpType = rule_d["ruleCpType"]
                        ruleCpNum = rule_d["ruleCpNum"]

                        if (ruleCpType == "le"):

                            matrix_emp_time = np.array(emp.available_timeList)
                            matrix_task_worktime = np.array(task.worktimeList)
                            # 如果员工可用时间中 不包含工作要求的时间 则不可用 否则 可用

                            result_matrix = np.bitwise_and(matrix_emp_time, matrix_task_worktime)
                            if ((result_matrix == matrix_task_worktime).all()):
                                index = CheckRule.search_start_end_index(task.worktimeList)
                                start_index = index["start"]
                                end_index = index["end"]

                                # 多个任务结合，形成总时间列表
                                matrix_all_task_worktime_list = np.array([0] *(24*60//timeSize))
                                for t_task in emp.tasks:
                                    matrix_t_task_worktime = np.array(t_task.worktimeList)
                                    matrix_all_task_worktime_list = np.bitwise_or(matrix_all_task_worktime_list,matrix_t_task_worktime)

                                all_task_worktime_list = matrix_all_task_worktime_list.tolist()

                                start_distance = CheckRule.looking_forward_1(all_task_timeList=all_task_worktime_list,start_index=start_index)
                                end_distance = CheckRule.looking_for_back_1(all_task_timeList=all_task_worktime_list,end_index=end_index)

                                if(start_distance <= int(ruleCpNum)//timeSize or end_distance <= int(ruleCpNum)//timeSize):
                                    caution = rule_d["caution"]
                                    if caution == 'hint' or caution == 'warning':
                                        break_rule_num += 1
                                        break_rule_list.append(rule_d)
                                    elif caution == "forbid":

                                        rule_str = "违反班次间隔小于等于%s的规则" % (ruleCpNum)
                                        emp.forbid_rule_set.add(rule_str)
                                        return 0, False

                            else:
                                return 0, False

                        elif (ruleCpType == "lt"):

                            matrix_emp_time = np.array(emp.available_timeList)
                            matrix_task_worktime = np.array(task.worktimeList)
                            # 如果员工可用时间中 不包含工作要求的时间 则不可用 否则 可用

                            result_matrix = np.bitwise_and(matrix_emp_time, matrix_task_worktime)
                            if ((result_matrix == matrix_task_worktime).all()):
                                index = CheckRule.search_start_end_index(task.worktimeList)
                                start_index = index["start"]
                                end_index = index["end"]

                                # 多个任务结合，形成总时间列表
                                matrix_all_task_worktime_list = np.array([0] *(24*60//timeSize))
                                for t_task in emp.tasks:
                                    matrix_t_task_worktime = np.array(t_task.worktimeList)
                                    matrix_all_task_worktime_list = np.bitwise_or(matrix_all_task_worktime_list,matrix_t_task_worktime)

                                all_task_worktime_list = matrix_all_task_worktime_list.tolist()

                                start_distance = CheckRule.looking_forward_1(all_task_timeList=all_task_worktime_list,start_index=start_index)
                                end_distance = CheckRule.looking_for_back_1(all_task_timeList=all_task_worktime_list,end_index=end_index)

                                if start_distance < int(ruleCpNum)//timeSize or end_distance < int(ruleCpNum)//timeSize :
                                    caution = rule_d["caution"]
                                    if caution == 'hint' or caution == 'warning':
                                        break_rule_num += 1
                                        break_rule_list.append(rule_d)
                                    elif caution == "forbid":
                                        rule_str = "违反班次间隔小于%s的规则" % (ruleCpNum)
                                        emp.forbid_rule_set.add(rule_str)
                                        return 0, False

                            else:
                                return 0, False

                        elif ruleCpType == "ge":

                            matrix_emp_time = np.array(emp.available_timeList)
                            matrix_task_worktime = np.array(task.worktimeList)
                            # 如果员工可用时间中 不包含工作要求的时间 则不可用 否则 可用

                            result_matrix = np.bitwise_and(matrix_emp_time, matrix_task_worktime)
                            if ((result_matrix == matrix_task_worktime).all()):
                                index = CheckRule.search_start_end_index(task.worktimeList)
                                start_index = index["start"]
                                end_index = index["end"]

                                # 多个任务结合，形成总时间列表
                                matrix_all_task_worktime_list = np.array([0] *(24*60//timeSize))
                                for t_task in emp.tasks:
                                    matrix_t_task_worktime = np.array(t_task.worktimeList)
                                    matrix_all_task_worktime_list = np.bitwise_or(matrix_all_task_worktime_list,matrix_t_task_worktime)

                                all_task_worktime_list = matrix_all_task_worktime_list.tolist()

                                start_distance = CheckRule.looking_forward_1(all_task_timeList=all_task_worktime_list,start_index=start_index)
                                end_distance = CheckRule.looking_for_back_1(all_task_timeList=all_task_worktime_list,end_index=end_index)

                                if(start_distance >= int(ruleCpNum)//timeSize or end_distance >= int(ruleCpNum)//timeSize):
                                    caution = rule_d["caution"]
                                    if caution == 'hint' or caution == 'warning':
                                        break_rule_num += 1
                                        break_rule_list.append(rule_d)
                                    elif caution == "forbid":
                                        rule_str = "违反班次间隔大于等于%s的规则" % (ruleCpNum)
                                        emp.forbid_rule_set.add(rule_str)
                                        return 0, False

                            else:
                                return 0, False

                        elif ruleCpType == "gt":

                            matrix_emp_time = np.array(emp.available_timeList)
                            matrix_task_worktime = np.array(task.worktimeList)
                            # 如果员工可用时间中 不包含工作要求的时间 则不可用 否则 可用

                            result_matrix = np.bitwise_and(matrix_emp_time, matrix_task_worktime)
                            if ((result_matrix == matrix_task_worktime).all()):
                                index = CheckRule.search_start_end_index(task.worktimeList)
                                start_index = index["start"]
                                end_index = index["end"]

                                # 多个任务结合，形成总时间列表
                                matrix_all_task_worktime_list = np.array([0] *(24*60//timeSize))
                                for t_task in emp.tasks:
                                    matrix_t_task_worktime = np.array(t_task.worktimeList)
                                    matrix_all_task_worktime_list = np.bitwise_or(matrix_all_task_worktime_list,matrix_t_task_worktime)

                                all_task_worktime_list = matrix_all_task_worktime_list.tolist()

                                start_distance = CheckRule.looking_forward_1(all_task_timeList=all_task_worktime_list,start_index=start_index)
                                end_distance = CheckRule.looking_for_back_1(all_task_timeList=all_task_worktime_list,end_index=end_index)

                                if start_distance > int(ruleCpNum)//timeSize or end_distance > int(ruleCpNum)//timeSize :
                                    caution = rule_d["caution"]
                                    if caution == 'hint' or caution == 'warning':
                                        break_rule_num += 1
                                        break_rule_list.append(rule_d)
                                    elif caution == "forbid":
                                        rule_str = "违反班次间隔大于%s的规则" % (ruleCpNum)
                                        emp.forbid_rule_set.add(rule_str)
                                        return 0, False

                            else:
                                return 0, False
        return break_rule_num,True

    @staticmethod
    def search_start_end_index(timeList:List):
        '''
        寻找某个工作的开始结束时间的列表索引值
        :param timeList:
        :return:
        '''
        start = 0
        end = 0
        for i in range(len(timeList)):
            if (timeList[i] != 0):
                start = i
                for j in range(i, len(timeList)):
                    if timeList[j] == 0:
                        end = j - 1
                        break
                    elif (j + 1 == len(timeList) and timeList[j] == 1):
                        end = j
                        break
            if (start != 0):
                break

        return {"start":start,"end":end}

    @staticmethod
    def looking_forward_0(available_timeList:List, start_index: int):
        '''
        向前找0 的 格子数
        :param available_timeList:
        :param start_index:
        :param ruleCpNum:
        :return:
        '''
        if(start_index >= len(available_timeList)):
            print("在寻找班次间隔过程中，存在数组越界")

        for i in range(start_index, -1, -1):

            if (available_timeList[i] == 0):
                return start_index - i
        return start_index

    @staticmethod
    def looking_for_back_0(available_timeList, end_index: int):
        '''
        向前后找0 的 格子数
        :param available_timeList:
        :param end_index:
        :return:
        '''
        for i in range(end_index, len(available_timeList)):
            if (available_timeList[i] == 0):
                return i - end_index
        return len(available_timeList) - end_index

    @staticmethod
    def looking_forward_1(all_task_timeList: List, start_index: int):
        '''
        向前找1 的 格子数
        :param available_timeList:
        :param start_index:
        :param ruleCpNum:
        :return:
        '''
        # if (start_index >= len(all_task_timeList)):
        #     print("在寻找班次间隔过程中，存在数组越界")
        #
        # for i in range(start_index, -1, -1):
        #
        #     if (all_task_timeList[i] == 1):
        #         return start_index - i - 1
        # # 表示该任务前方没有任务
        # return -1

        if (start_index >= len(all_task_timeList)):
            print("在寻找班次间隔过程中，存在数组越界")

        for i in range(start_index, -1, -1):

            if (all_task_timeList[i] == 1):
                return start_index - i
        return start_index


    @staticmethod
    def looking_for_back_1(all_task_timeList:List, end_index: int):
        '''
        向前后找1 的 格子数
        :param available_timeList:
        :param end_index:
        :return:
        '''
        # for i in range(end_index, len(all_task_timeList)):
        #     if (all_task_timeList[i] == 1):
        #         return i - end_index - 1
        # # 表示该任后方没有任务
        # return -1

        for i in range(end_index, len(all_task_timeList)):
            if (all_task_timeList[i] == 1):
                return i - end_index
        return len(all_task_timeList) - end_index
        # -1 表示 该任务被安排上没任务
        # return -1


    @staticmethod
    def check_schShiftNum(emp:Employee,emp_rule_dict:Dict,forecast_day:str,break_rule_num:int,break_rule_list:List):
        '''
        检查已排班个数
        :param emp:
        :param task:
        :param emp_rule_dict:
        :param forecast_day:
        :param timeSize:
        :return:
        '''
        cid = emp.cid
        eid = emp.eid
        bids = emp.bids
        forecast_day = datetime.datetime.strptime(forecast_day, "%Y-%m-%d")

        for bid in bids:
            emp_compliance_key = cid + "-" + bid
            for rule_d in emp_rule_dict.get(emp_compliance_key, []):
                ruleType = rule_d["ruleType"]
                ruletag = rule_d["ruletag"]

                if (ruleType == "shiftrule" and ruletag == 'schShiftNum'):
                    startDate = rule_d["startDate"]
                    timeRange = rule_d["timeRange"]
                    cycle = rule_d["cycle"]

                    if (cycle == "day" and forecast_day >= datetime.datetime.strptime(str(startDate),'%Y-%m-%d')):
                        ruleCpType = rule_d["ruleCpType"]
                        ruleCpNum = rule_d["ruleCpNum"]

                        if (ruleCpType == "lt" and emp.dayShiftNum +1 < int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                rule_str = "违反天班次个数小于%s的规则" % (ruleCpNum)
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "le" and emp.dayShiftNum+1 <= int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                rule_str = "违反天班次个数小于等于%s的规则" % (ruleCpNum)
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "eq" and emp.dayShiftNum+1 == int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":

                                rule_str = "违反天班次个数等于%s的规则" % (ruleCpNum)
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "gt" and emp.dayShiftNum+1 > int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":

                                rule_str = "违反天班次个数大于%s的规则" % (ruleCpNum)
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "ge" and emp.dayShiftNum+1 >= int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":

                                rule_str = "违反天班次个数大于等于%s的规则" % (ruleCpNum)
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False

                    elif (cycle == "week" and forecast_day >= datetime.datetime.strptime(str(startDate),'%Y-%m-%d')):
                        ruleCpType = rule_d["ruleCpType"]
                        ruleCpNum = rule_d["ruleCpNum"]

                        if (ruleCpType == "lt" and emp.weekShiftNum +1 < int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                rule_str = "违反周班次个数小于%s的规则" % (ruleCpNum)
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "le" and emp.weekShiftNum +1<= int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                rule_str = "违反周班次个数小于等于%s的规则" % (ruleCpNum)
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "eq" and emp.weekShiftNum +1== int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":

                                rule_str = "违反周班次个数等于%s的规则" % (ruleCpNum)
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "gt" and emp.weekShiftNum +1> int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":

                                rule_str = "违反周班次个数大于%s的规则" % (ruleCpNum)
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "ge" and emp.weekShiftNum +1>= int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":

                                rule_str = "违反周班次个数大于等于%s的规则" % (ruleCpNum)
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                    # 月排班个数
                    elif (cycle == "month"):
                        # 获取周期内的天数
                        days = 0
                        for i in range(0, int(timeRange)):
                            days += calendar.monthrange(forecast_day.year, forecast_day.month + i)[1]

                        if forecast_day >= datetime.datetime.strptime(str(startDate),'%Y-%m-%d'):
                            ruleCpType = rule_d["ruleCpType"]
                            ruleCpNum = rule_d["ruleCpNum"]

                            if (ruleCpType == "lt" and emp.weekShiftNum +1< int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":

                                    rule_str = "违反月班次个数小于%s的规则" % (ruleCpNum)
                                    emp.forbid_rule_set.add(rule_str)
                                    return 0, False
                            elif (ruleCpType == "le" and emp.weekShiftNum +1<= int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    rule_str = "违反月班次个数小于等于%s的规则" % (ruleCpNum)
                                    emp.forbid_rule_set.add(rule_str)
                                    return 0, False
                            elif (ruleCpType == "eq" and emp.weekShiftNum +1== int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    rule_str = "违反月班次个数等于%s的规则" % (ruleCpNum)
                                    emp.forbid_rule_set.add(rule_str)
                                    return 0, False
                            elif ruleCpType == "gt" and emp.weekShiftNum + 1 > int(ruleCpNum):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    rule_str = "违反月班次个数大于%s的规则" % (ruleCpNum)
                                    emp.forbid_rule_set.add(rule_str)
                                    return 0, False
                            elif ruleCpType == "ge" and emp.weekShiftNum + 1 >= int(ruleCpNum):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    rule_str = "违反月班次个数大于等于%s的规则" %(ruleCpNum)
                                    emp.forbid_rule_set.add(rule_str)
                                    return 0, False
        return break_rule_num,True

    @staticmethod
    def check_schDayNumCon(emp:Employee,emp_rule_dict:Dict,forecast_day:str,break_rule_num:int,break_rule_list:List):
        '''
        检查员工连续排班天数
        :param emp:
        :param emp_rule_dict:
        :param forecast_day:
        :return:
        '''
        cid = emp.cid
        # eid = emp.eid
        bids = emp.bids

        forecast_day_str = forecast_day
        forecast_day = datetime.datetime.strptime(forecast_day, "%Y-%m-%d")

        for bid in bids:
            emp_compliance_key = cid + "-" + bid
            for rule_d in emp_rule_dict.get(emp_compliance_key, []):
                ruleType = rule_d["ruleType"]
                ruletag = rule_d["ruletag"]

                if (ruleType == "daysrule" and ruletag == 'schDayNumCon'):
                    startDate = rule_d["startDate"]
                    timeRange = rule_d["timeRange"]
                    cycle = rule_d["cycle"]

                    if (cycle == "week" and forecast_day >= datetime.datetime.strptime(str(startDate), '%Y-%m-%d')):
                        ruleCpType = rule_d["ruleCpType"]
                        ruleCpNum = rule_d["ruleCpNum"]

                        # 临时连续工作日期表
                        # temp_work_list = emp.work_date_list
                        # temp_work_list.extend([forecast_day_str])
                        # temp_work_list.sort()
                        # schDayNumCon = Employee.search_max_len_dateStr(temp_work_list)

                        if (ruleCpType == "lt" and emp.schDayNumCon_week < int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                infoLog.info('eid:%s,日期：%s违反连续工作天数规则-%s' % (emp.eid,forecast_day_str,cycle))
                                rule_str = "违反周员工连续排班天数小于%s的规则" %ruleCpNum
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif ruleCpType == "le" and emp.schDayNumCon_week <= int(ruleCpNum):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                infoLog.info('eid:%s,日期：%s违反连续工作天数规则-%s' % (emp.eid, forecast_day_str, cycle))
                                rule_str = "违反周员工连续排班天数小于等于%s的规则" % ruleCpNum
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "eq" and emp.schDayNumCon_week == int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":

                                infoLog.info('eid:%s,日期：%s违反连续工作天数规则-%s' % (emp.eid, forecast_day_str, cycle))
                                rule_str = "违反周员工连续排班天数等于%s的规则" % ruleCpNum
                                emp.forbid_rule_set.add(rule_str)
                                return False
                        elif (ruleCpType == "gt" and emp.schDayNumCon_week > int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":

                                infoLog.info('eid:%s,日期：%s违反连续工作天数规则-%s' % (emp.eid, forecast_day_str, cycle))
                                rule_str = "违反周员工连续排班天数大于%s的规则" % ruleCpNum
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "ge" and emp.schDayNumCon_week >= int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":

                                infoLog.info('eid:%s,日期：%s违反连续工作天数规则-%s' % (emp.eid, forecast_day_str, cycle))
                                rule_str = "违反周员工连续排班天数大于等于%s的规则" % ruleCpNum
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False

                    elif (cycle == "month"):
                        # 获取周期内的天数
                        days = 0
                        for i in range(0, int(timeRange)):
                            days += calendar.monthrange(forecast_day.year, forecast_day.month + i)[1]

                        if (forecast_day >= datetime.datetime.strptime(str(startDate), '%Y-%m-%d')):
                            ruleCpType = rule_d["ruleCpType"]
                            ruleCpNum = rule_d["ruleCpNum"]

                            # 临时连续工作日期表
                            # temp_work_list = emp.work_date_list
                            # temp_work_list.extend([forecast_day_str])
                            # temp_work_list.sort()
                            # schDayNumCon = Employee.search_max_len_dateStr(temp_work_list)

                            if (ruleCpType == "lt" and emp.schDayNumCon_month < int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":

                                    infoLog.info('eid:%s,日期：%s违反连续工作天数规则-%s' % (emp.eid, forecast_day_str, cycle))
                                    rule_str = "违反月员工连续排班小于%s的规则" % ruleCpNum
                                    emp.forbid_rule_set.add(rule_str)
                                    return 0, False
                            elif (ruleCpType == "le" and emp.schDayNumCon_month <= int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":

                                    infoLog.info('eid:%s,日期：%s违反连续工作天数规则-%s' % (emp.eid, forecast_day_str, cycle))
                                    rule_str = "违反月员工连续排班小于等于%s的规则" % ruleCpNum
                                    emp.forbid_rule_set.add(rule_str)
                                    return 0, False

                            elif (ruleCpType == "eq" and emp.schDayNumCon_month == int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    infoLog.info('eid:%s,日期：%s违反连续工作天数规则-%s' % (emp.eid, forecast_day_str, cycle))
                                    rule_str = "违反月员工连续排班等于%s的规则" % ruleCpNum
                                    emp.forbid_rule_set.add(rule_str)
                                    return 0, False
                            elif (ruleCpType == "gt" and emp.schDayNumCon_month > int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    infoLog.info('eid:%s,日期：%s违反连续工作天数规则-%s' % (emp.eid, forecast_day_str, cycle))
                                    rule_str = "违反月员工连续排班大于%s的规则" % ruleCpNum
                                    emp.forbid_rule_set.add(rule_str)
                                    return 0, False
                            
                            elif (ruleCpType == "ge" and emp.schDayNumCon_month >= int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    infoLog.info('eid:%s,日期：%s违反连续工作天数规则-%s' % (emp.eid, forecast_day_str, cycle))
                                    rule_str = "违反月员工连续排班大于等于%s的规则" % ruleCpNum
                                    emp.forbid_rule_set.add(rule_str)
                                    return 0, False

        return break_rule_num,True

    @staticmethod
    def check_restNumCon(emp:Employee,emp_rule_dict:Dict,forecast_day:str,break_rule_num:int,break_rule_list:List):
        '''
        检查连续休息天数
        :param emp:
        :param emp_rule_dict:
        :param forecast_day:
        :return:
        '''
        cid = emp.cid
        # eid = emp.eid
        bids = emp.bids
        forecast_day = datetime.datetime.strptime(forecast_day, "%Y-%m-%d")

        for bid in bids:
            emp_compliance_key = cid + "-" + bid
            for rule_d in emp_rule_dict.get(emp_compliance_key, []):
                ruleType = rule_d["ruleType"]
                ruletag = rule_d["ruletag"]

                if (ruleType == "daysrule" and ruletag == 'restNumCon'):
                    startDate = rule_d["startDate"]
                    timeRange = rule_d["timeRange"]
                    cycle = rule_d["cycle"]

                    if (cycle == "week" and forecast_day >= datetime.datetime.strptime(str(startDate), '%Y-%m-%d')):
                        ruleCpType = rule_d["ruleCpType"]
                        ruleCpNum = rule_d["ruleCpNum"]

                        if (ruleCpType == "lt" and emp.restNumCon < int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                rule_str = "违反周员工连续休息天数小于%s的规则" % ruleCpNum
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "le" and emp.restNumCon <= int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                rule_str = "违反周员工连续休息天数小于等于%s的规则" % ruleCpNum
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "eq" and emp.restNumCon == int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                rule_d_copy = dict(rule_d)
                                rule_str = "违反周员工连续休息天数等于%s的规则" % ruleCpNum
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "gt" and emp.restNumCon > int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                rule_str = "违反周员工连续休息天数大于%s的规则" % ruleCpNum
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "ge" and emp.restNumCon >= int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                rule_str = "违反周员工连续休息天数大于等于%s的规则" % ruleCpNum
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False

                    elif (cycle == "month"):
                        # 获取周期内的天数
                        days = 0
                        for i in range(0, int(timeRange)):
                            days += calendar.monthrange(forecast_day.year, forecast_day.month + i)[1]

                        if(forecast_day >= datetime.datetime.strptime(str(startDate), '%Y-%m-%d')):
                            ruleCpType = rule_d["ruleCpType"]
                            ruleCpNum = rule_d["ruleCpNum"]

                            if (ruleCpType == "lt" and emp.restNumCon < int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    rule_str = "违反月员工连续休息天数小于%s的规则" % ruleCpNum
                                    emp.forbid_rule_set.add(rule_str)
                                    return 0, False
                            elif (ruleCpType == "le" and emp.restNumCon <= int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    rule_str = "违反月员工连续休息天数小于等于%s的规则" % ruleCpNum
                                    emp.forbid_rule_set.add(rule_str)
                                    return 0, False
                            elif (ruleCpType == "eq" and emp.restNumCon == int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    rule_str = "违反月员工连续休息天数等于%s的规则" % ruleCpNum
                                    emp.forbid_rule_set.add(rule_str)
                                    return 0, False
                            elif (ruleCpType == "gt" and emp.restNumCon > int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    rule_str = "违反月员工连续休息天数大于%s的规则" % ruleCpNum
                                    emp.forbid_rule_set.add(rule_str)
                                    return 0, False
                            elif (ruleCpType == "ge" and emp.restNumCon >= int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    rule_str = "违反月员工连续休息天数大于等于%s的规则" % ruleCpNum
                                    emp.forbid_rule_set.add(rule_str)
                                    return 0, False
        return break_rule_num,True

    @staticmethod
    def check_noSchNum(emp: Employee, emp_rule_dict: Dict, forecast_day: str,break_rule_num:int,break_rule_list:List):
        '''
        检查未排班天数
        :param emp:
        :param emp_rule_dict:
        :param forecast_day:
        :return:
        '''
        cid = emp.cid
        # eid = emp.eid
        bids = emp.bids
        forecast_day = datetime.datetime.strptime(forecast_day, "%Y-%m-%d")

        for bid in bids:
            emp_compliance_key = cid + "-" + bid
            for rule_d in emp_rule_dict.get(emp_compliance_key, []):
                ruleType = rule_d["ruleType"]
                ruletag = rule_d["ruletag"]

                if (ruleType == "daysrule" and ruletag == 'noSchNum'):
                    startDate = rule_d["startDate"]
                    timeRange = rule_d["timeRange"]
                    cycle = rule_d["cycle"]

                    if (cycle == "week" and forecast_day >= datetime.datetime.strptime(str(startDate), '%Y-%m-%d')):
                        ruleCpType = rule_d["ruleCpType"]
                        ruleCpNum = rule_d["ruleCpNum"]

                        if (ruleCpType == "lt" and emp.noSchNum < int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":

                                rule_str = "违反周员工未排班天数小于%s的规则" % ruleCpNum
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "le" and emp.noSchNum <= int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                rule_str = "违反周员工未排班天数小于等于%s的规则" % ruleCpNum
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "eq" and emp.noSchNum == int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                rule_str = "违反周员工未排班天数等于%s的规则" % ruleCpNum
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "gt" and emp.noSchNum > int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                rule_str = "违反周员工未排班天数大于%s的规则" % ruleCpNum
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "ge" and emp.noSchNum >= int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                rule_str = "违反周员工未排班天数大于等于%s的规则" % ruleCpNum
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False

                    elif (cycle == "month"):
                        # 获取周期内的天数
                        days = 0
                        for i in range(0, int(timeRange)):
                            days += calendar.monthrange(forecast_day.year, forecast_day.month + i)[1]

                        if( forecast_day >= datetime.datetime.strptime(str(startDate), '%Y-%m-%d')):
                            ruleCpType = rule_d["ruleCpType"]
                            ruleCpNum = rule_d["ruleCpNum"]

                            if (ruleCpType == "lt" and emp.noSchNum < int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    rule_str = "违反月员工未排班天数小于%s的规则" % ruleCpNum
                                    emp.forbid_rule_set.add(rule_str)
                                    return 0, False
                            elif (ruleCpType == "le" and emp.noSchNum <= int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    rule_str = "违反月员工未排班天数小于等于%s的规则" % ruleCpNum
                                    emp.forbid_rule_set.add(rule_str)
                                    return 0, False
                            elif (ruleCpType == "eq" and emp.noSchNum == int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    rule_str = "违反月员工未排班天数等于%s的规则" % ruleCpNum
                                    emp.forbid_rule_set.add(rule_str)
                                    return 0, False
                            elif (ruleCpType == "gt" and emp.noSchNum > int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    rule_str = "违反月员工未排班天数大于%s的规则" % ruleCpNum
                                    emp.forbid_rule_set.add(rule_str)
                                    return 0, False
                            elif (ruleCpType == "ge" and emp.noSchNum >= int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    rule_str = "违反月员工未排班天数大于等于%s的规则" % ruleCpNum
                                    emp.forbid_rule_set.add(rule_str)
                                    return 0, False
        return break_rule_num,True

    @staticmethod
    def check_restNum(emp: Employee, emp_rule_dict: Dict, forecast_day: str,break_rule_num:int,break_rule_list:List):
        '''
        检查休息天数
        :param emp:
        :param emp_rule_dict:
        :param forecast_day:
        :return:
        '''
        cid = emp.cid
        # eid = emp.eid
        bids = emp.bids
        forecast_day = datetime.datetime.strptime(forecast_day, "%Y-%m-%d")

        for bid in bids:
            emp_compliance_key = cid + "-" + bid
            for rule_d in emp_rule_dict.get(emp_compliance_key, []):
                ruleType = rule_d["ruleType"]
                ruletag = rule_d["ruletag"]

                if (ruleType == "daysrule" and ruletag == 'restNum'):
                    startDate = rule_d["startDate"]
                    timeRange = rule_d["timeRange"]
                    cycle = rule_d["cycle"]

                    if (cycle == "week" and forecast_day >= datetime.datetime.strptime(str(startDate), '%Y-%m-%d')):
                        ruleCpType = rule_d["ruleCpType"]
                        ruleCpNum = rule_d["ruleCpNum"]

                        if (ruleCpType == "lt" and emp.restNum < int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                rule_str = "违反周员工休息天数小于%s的规则" % ruleCpNum
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "le" and emp.restNum <= int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                rule_str = "违反周员工休息天数小于等于%s的规则" % ruleCpNum
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "eq" and emp.restNum == int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                rule_str = "违反周员工休息天数等于%s的规则" % ruleCpNum
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "gt" and emp.restNum > int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                rule_str = "违反周员工休息天数大于%s的规则" % ruleCpNum
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "ge" and emp.restNum >= int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                rule_str = "违反周员工休息天数大于等于%s的规则" % ruleCpNum
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                    elif (cycle == "month"):
                        # 获取周期内的天数
                        days = 0
                        for i in range(0, int(timeRange)):
                            days += calendar.monthrange(forecast_day.year, forecast_day.month + i)[1]

                        if(forecast_day >= datetime.datetime.strptime(str(startDate), '%Y-%m-%d')):
                            ruleCpType = rule_d["ruleCpType"]
                            ruleCpNum = rule_d["ruleCpNum"]

                            if (ruleCpType == "lt" and emp.restNum < int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    rule_str = "违反月员工休息天数小于%s的规则" % ruleCpNum
                                    emp.forbid_rule_set.add(rule_str)
                                    return 0, False
                            elif (ruleCpType == "le" and emp.restNum <= int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    rule_str = "违反月员工休息天数小于等于%s的规则" % ruleCpNum
                                    emp.forbid_rule_set.add(rule_str)
                                    return 0, False
                            elif (ruleCpType == "eq" and emp.restNum == int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    rule_str = "违反月员工休息天数等于%s的规则" % ruleCpNum
                                    emp.forbid_rule_set.add(rule_str)
                                    return 0, False
                            elif (ruleCpType == "gt" and emp.restNum > int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    rule_str = "违反月员工休息天数大于%s的规则" % ruleCpNum
                                    emp.forbid_rule_set.add(rule_str)
                                    return 0, False
                            elif (ruleCpType == "ge" and emp.restNum >= int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    rule_str = "违反月员工休息天数大于等于%s的规则" % ruleCpNum
                                    emp.forbid_rule_set.add(rule_str)
                                    return 0, False
        return break_rule_num,True

    @staticmethod
    def check_schNumSame(task:CombTasks,emp:Employee,emp_rule_dict:Dict,forecast_day:str,break_rule_num:int,break_rule_list:List):
        '''
        检查相同排班天数
        :param emp:
        :param emp_rule_dict:
        :param forecast_day:
        :param break_rule_num:
        :param break_rule_list:
        :return:
        '''
        cid = emp.cid
        # eid = emp.eid
        bids = emp.bids
        forecast_day = datetime.datetime.strptime(forecast_day, "%Y-%m-%d")

        for bid in bids:
            emp_compliance_key = cid + "-" + bid
            for rule_d in emp_rule_dict.get(emp_compliance_key, []):
                ruleType = rule_d["ruleType"]
                ruletag = rule_d["ruletag"]

                if (ruleType == "daysrule" and ruletag == 'schNumSame'):
                    startDate = rule_d["startDate"]
                    timeRange = rule_d["timeRange"]
                    cycle = rule_d["cycle"]

                    if (cycle == "week" and forecast_day >= datetime.datetime.strptime(str(startDate), '%Y-%m-%d')):
                        ruleCpType = rule_d["ruleCpType"]
                        ruleCpNum = rule_d["ruleCpNum"]

                        starttime = task.start[0]
                        endtime = task.end[-1]

                        # 包含将要安排工作的开始结束时间的key
                        keys = [key for key in emp.schNumSame if starttime +'-' + endtime in key]

                        for k in keys:
                            if (ruleCpType == "eq" and emp.schNumSame[k] == int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    rule_str = "违反周员工相同排班天数等于%s的规则" % ruleCpNum
                                    emp.forbid_rule_set.add(rule_str)
                                    return 0, False
                            elif (ruleCpType == "gt" and emp.schNumSame[k] > int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    rule_str = "违反周员工相同排班天数大于%s的规则" % ruleCpNum
                                    emp.forbid_rule_set.add(rule_str)
                                    return 0, False
                            elif (ruleCpType == "ge" and emp.schNumSame[k] >= int(ruleCpNum)):
                                caution = rule_d["caution"]
                                if caution == 'hint' or caution == 'warning':
                                    break_rule_num += 1
                                    break_rule_list.append(rule_d)
                                elif caution == "forbid":
                                    rule_str = "违反周员工相同排班天数大于等于%s的规则" % ruleCpNum
                                    emp.forbid_rule_set.add(rule_str)
                                    return 0, False
                    elif (cycle == "month"):
                        # 获取周期内的天数
                        days = 0
                        for i in range(0, int(timeRange)):
                            days += calendar.monthrange(forecast_day.year, forecast_day.month + i)[1]

                        if (forecast_day >= datetime.datetime.strptime(str(startDate), '%Y-%m-%d')):
                            ruleCpType = rule_d["ruleCpType"]
                            ruleCpNum = rule_d["ruleCpNum"]

                            starttime = task.start[0]
                            endtime = task.end[-1]

                            # 包含将要安排工作的开始结束时间的key
                            keys = [key for key in emp.schNumSame if starttime + '-' + endtime in key]

                            for k in keys:
                                if (ruleCpType == "eq" and emp.schNumSame[k] == int(ruleCpNum)):
                                    caution = rule_d["caution"]
                                    if caution == 'hint' or caution == 'warning':
                                        break_rule_num += 1
                                        break_rule_list.append(rule_d)
                                    elif caution == "forbid":
                                        rule_str = "违反月员工相同排班天数等于%s的规则" % ruleCpNum
                                        emp.forbid_rule_set.add(rule_str)
                                        return 0, False
                                elif (ruleCpType == "gt" and emp.schNumSame[k] > int(ruleCpNum)):
                                    caution = rule_d["caution"]
                                    if caution == 'hint' or caution == 'warning':
                                        break_rule_num += 1
                                        break_rule_list.append(rule_d)
                                    elif caution == "forbid":
                                        rule_str = "违反月员工相同排班天数大于%s的规则" % ruleCpNum
                                        emp.forbid_rule_set.add(rule_str)
                                        return 0, False
                                elif (ruleCpType == "ge" and emp.schNumSame[k] >= int(ruleCpNum)):
                                    caution = rule_d["caution"]
                                    if caution == 'hint' or caution == 'warning':
                                        break_rule_num += 1
                                        break_rule_list.append(rule_d)
                                    elif caution == "forbid":
                                        rule_str = "违反月员工相同排班天数大于等于%s的规则" % ruleCpNum
                                        emp.forbid_rule_set.add(rule_str)
                                        return 0, False
        return break_rule_num, True

    @staticmethod
    def check_length_of_task(emp:Employee,task:CombTasks,emp_rule_dict:Dict,forecast_day:str,break_rule_num:int,break_rule_list:List):
        '''
        任务长度
        :param emp:
        :param task:
        :param emp_rule_dict:
        :param forecast_day:
        :param break_rule_num:
        :param break_rule_list:
        :return:
        '''
        cid = emp.cid
        # eid = emp.eid
        bids = emp.bids
        forecast_day = datetime.datetime.strptime(forecast_day, "%Y-%m-%d")

        for bid in bids:
            emp_compliance_key = cid + "-" + bid
            #print("eid,check_shift_len ---- ", eid)
            for rule_d in emp_rule_dict.get(emp_compliance_key, []):
                ruleType = rule_d["ruleType"]
                ruletag = rule_d["ruletag"]

                # 任务长度  合规性  规则暂定为taskLen
                if (ruleType == "shiftrule" and ruletag == "taskLen"):

                    startDate = rule_d["startDate"]
                    timeRange = rule_d["timeRange"]
                    cycle = rule_d["cycle"]

                    # day任务长度
                    if (cycle == "day" and forecast_day >= datetime.datetime.strptime(str(startDate),'%Y-%m-%d')):
                        ruleCpType = rule_d["ruleCpType"]
                        ruleCpNum = rule_d["ruleCpNum"]

                        # 统计员工已有任务个数
                        task_nums = sum([len(t.start) for t in emp.tasks])

                        if (ruleCpType == "lt" and task_nums + len(task.start) < int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                rule_str = "违反天任务长度（班次内任务个数）小于%s的规则" % ruleCpNum
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "le" and task_nums + len(task.start) <= int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                rule_str = "违反天任务长度（班次内任务个数）小于等于%s的规则" % ruleCpNum
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "eq" and task_nums + len(task.start) == int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                rule_str = "违反天任务长度（班次内任务个数）等于%s的规则" % ruleCpNum
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "ge" and task_nums + len(task.start) >= int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                rule_str = "违反天任务长度（班次内任务个数）大于等于%s的规则" % ruleCpNum
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
                        elif (ruleCpType == "gt" and task_nums + len(task.start) > int(ruleCpNum)):
                            caution = rule_d["caution"]
                            if caution == 'hint' or caution == 'warning':
                                break_rule_num += 1
                                break_rule_list.append(rule_d)
                            elif caution == "forbid":
                                rule_str = "违反天任务长度（班次内任务个数）大于%s的规则" % ruleCpNum
                                emp.forbid_rule_set.add(rule_str)
                                return 0, False
        return break_rule_num,True
