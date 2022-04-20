'''
create by liyabin
'''
import json
from typing import Dict,Tuple,List
import random
from POC.bean.TemporaryEmployee import TemporaryEmployee
from POC.bean.CheckRule import CheckRule
from POC.bean.CheckTempEmpRule import CheckTempEmpRule
from POC.bean.ShiftPriority import ShiftPriority
from utils.myLogger import infoLog
from config.settings import settings

class Mapping:

    @staticmethod
    def random_emp_to_comb_tasks(comb_tasks_list: List, emp_list: List, emp_rule_dict: Dict, emp_matchpro: Tuple,
                                 forecast_day: str,timeSize:int,all_forecast_days:List[str],quotient_set:set,
                                 callbackData:Dict,ratio_of_cycles:float,now_restEid_list,task_all_info:Dict):
        '''
        仅考虑组合任务 和 人之间的匹配 不考虑任务之间的连续性 考虑了员工的优先级
        :param comb_tasks_dict:
        :param emp_skill_dict:
        :return:
        '''
        # 重新排序
        #random.shuffle(comb_tasks_list)
        #增加一个班次排人优先级的方法

        tasks_priority_list=settings['tasks_priority_list']
        comb_tasks_list=ShiftPriority.init_shift_priority(comb_tasks_list,tasks_priority_list)



        # 打乱顺序
        random.shuffle(emp_list)

        # 存储任务-员工的组合
        task_emp_dict = {}

        # 进度条已完成比例
        # quotient_set = set()
        cycle_length = len(all_forecast_days)
        finish_rate = all_forecast_days.index(forecast_day) / cycle_length

        for comb_tasks in comb_tasks_list:

            # 如果任务长度小于1小时跳过
            #if(sum(comb_tasks.worktimeList) <= (60//timeSize) ):continue

            task_emp_dict[comb_tasks.shiftId + "-" + comb_tasks.taskCombination] = []
            tasks_set = set()
            taskSkillBid_list = getattr(comb_tasks, 'taskSkillBid_list')
            for taskSkillBid in taskSkillBid_list:
                tasks_set.add(taskSkillBid)

            '''
            临时处理---吃饭任务的技能为"break"
            '''
            if "break" in tasks_set:
                tasks_set.remove("break")

            # 计数
            num = 0
            # 员工列表
            employees = []

            for emp in emp_list:
                if emp.eid in now_restEid_list:#遇到随机休息的员工则跳过不排他

                    emp.forbid_rule_set.add("算法控制员工休息")
                    continue
                emp_skills_set = set(getattr(emp, "skill"))

                # 违反规则计数
                break_rule_num = 0
                # 存储违反规则名称
                break_rule_list = []

                # 存储拒绝排班集合
                forbid_rule_set = set()

                #flag0_0 = tasks_set.issubset(emp_skills_set)

                #if (flag0_0):

                flag0_1,rule_str = CheckRule.check_skill_and_cert_requirements(emp=emp, tasks=comb_tasks, forecast_day=forecast_day,task_all_info=task_all_info)
                if not flag0_1:
                    emp.forbid_rule_set.add(rule_str)


                num1, flag1 = CheckRule.check_worktime_rule(emp=emp, emp_rule_dict=emp_rule_dict,worktime_minutes=comb_tasks.worktime_minutes,forecast_day=forecast_day,break_rule_num=break_rule_num,break_rule_list=break_rule_list,taskName_list=comb_tasks.taskName_list)
                num2, flag2 = CheckRule.check_shift_len(emp=emp,task=comb_tasks,emp_rule_dict=emp_rule_dict, forecast_day=forecast_day,break_rule_num=break_rule_num,break_rule_list=break_rule_list) #比如班次过短这个人不能排在这个位置
                num3, flag3 = CheckRule.check_shift_interval(emp=emp, task=comb_tasks, emp_rule_dict=emp_rule_dict, forecast_day=forecast_day, timeSize=timeSize,break_rule_num=break_rule_num,break_rule_list=break_rule_list)
                num4, flag4 = CheckRule.check_schShiftNum(emp=emp,emp_rule_dict=emp_rule_dict,forecast_day=forecast_day,break_rule_num=break_rule_num,break_rule_list=break_rule_list)
                num5, flag5 = CheckRule.check_schDayNumCon(emp=emp,emp_rule_dict=emp_rule_dict,forecast_day=forecast_day,break_rule_num=break_rule_num,break_rule_list=break_rule_list)
                num6, flag6 = CheckRule.check_restNumCon(emp=emp, emp_rule_dict=emp_rule_dict,forecast_day=forecast_day,break_rule_num=break_rule_num,break_rule_list=break_rule_list)
                num7, flag7 = CheckRule.check_noSchNum(emp=emp, emp_rule_dict=emp_rule_dict,forecast_day=forecast_day,break_rule_num=break_rule_num,break_rule_list=break_rule_list)
                num8, flag8 = CheckRule.check_restNum(emp=emp, emp_rule_dict=emp_rule_dict, forecast_day=forecast_day,break_rule_num=break_rule_num,break_rule_list=break_rule_list)

                num9, flag9 = CheckRule.check_schNumSame(task=comb_tasks,emp=emp,emp_rule_dict=emp_rule_dict,forecast_day=forecast_day,break_rule_num=break_rule_num,break_rule_list=break_rule_list)
                num10, flag10 = CheckRule.check_length_of_task(emp=emp,task=comb_tasks,emp_rule_dict=emp_rule_dict,forecast_day=forecast_day,break_rule_num=break_rule_num,break_rule_list=break_rule_list)


                if(flag0_1 and flag1 and flag2 and flag3 and flag4 and flag5 and flag6 and flag7 and flag8 and flag9 and flag10):

                    break_rule_num = num1 + num2  + num3+ num4 + num5 + num6 + num7 + num8  + num9 + num10
                    # 添加元组 （违反次数，员工）
                    employees.append((break_rule_num,emp,break_rule_list,forbid_rule_set))

                #else:
                #    emp.forbid_rule_set.add("Step2:技能值或证书不符合")


            # 将员工按weight进行排序
            employees.sort(key=lambda x: x[1].weight,reverse=False)
            for break_rule_num,e,break_rule_list,forbid_rule_set in employees:
                matix_emp_time = np.array(e.available_timeList)
                matix_task_worktime = np.array(comb_tasks.worktimeList)
                # 如果员工可用时间中 不包含工作要求的时间 则不可用 否则 可用

                result_matrix = np.bitwise_and(matix_emp_time, matix_task_worktime)

                flag_time = (result_matrix == matix_task_worktime).all()

                if not flag_time:
                    e.forbid_rule_set.add("班次对应的员工时间不可用")

                elif (flag_time):

                    # 去掉员工相应的可用时间
                    matix_emp_time = np.bitwise_xor(matix_emp_time, matix_task_worktime).tolist()
                    e.available_timeList = matix_emp_time


                    if ("缺人" in comb_tasks.employees):
                        comb_tasks.employees.remove("缺人")
                    # 更改对象相应的域
                    comb_tasks.employees.append(e)

                    # 给员工添加工时时，修改匹配属性的优先级
                    e.set_worktime(workTime=comb_tasks.worktime_minutes, emp_matchpro=emp_matchpro)
                    e.set_did(comb_tasks.did)
                    e.tasks.append(comb_tasks)
                    # 更新班次个数
                    e.set_shift_num()
                    # 添加员工违反软约束的个数
                    e.set_break_rule_num(break_rule_num)
                    # 添加违反的约束
                    e.set_break_rule_list(break_rule_list)

                    '''
                    进度条
                    '''
                    comb_tasks.scheduling_completed()
                    # 计算任务排班完成度
                    rate = sum([1 for comb_tasks in comb_tasks_list if comb_tasks.done is True]) / len(comb_tasks_list) / cycle_length
                    all_rate = (finish_rate + rate) * ratio_of_cycles

                    quotient = all_rate // 0.2
                    if quotient:

                        if quotient not in quotient_set:
                            quotient_set.add(quotient)
                            print('完成度：%f' % (all_rate))
                            callbackData['percentage'] = round(all_rate * 100,2)

                            callbackProgressUrl = callbackData.get('callbackProgressUrl','')
                            if "http://" in callbackProgressUrl or "https://" in callbackProgressUrl:
                                callbackProgressUrl = callbackProgressUrl
                            else:
                                callbackProgressUrl = "http://" + callbackProgressUrl

                            infoLog.info('排班进度回调：%f' % round(all_rate * 100,2))
                            headers = {'content-type': 'application/json'}

                            json.dumps(callbackData).encode('utf-8')
                            response = requests.post(url=callbackProgressUrl, json=callbackData, headers=headers)
                            html_code = response.status_code
                            print('排班进度回调接口喔趣返回：{}'.format(html_code))
                            infoLog.info('排班进度回调接口喔趣返回：{}'.format(html_code))
                            print('排班进度回调接口喔趣返回数据：{}'.format(response.text))
                            infoLog.info('排班进度回调接口喔趣返回数据：{}'.format(response.text))

                    '''
                    结束
                    '''

                    # 打印/返回结果
                    task_emp_dict[comb_tasks.shiftId + "-" + comb_tasks.taskCombination].append(e)

                    # 计数，控制每个任务分配的人数
                    num += 1
                    if (num >= int(comb_tasks.combinationVal)): break

            if (num < int(comb_tasks.combinationVal)):
                emp_diff_num = int(comb_tasks.combinationVal) - num
                for i in range(emp_diff_num):
                    task_emp_dict[comb_tasks.shiftId + "-" + comb_tasks.taskCombination].append("缺人")


        # 任务需要的人数
        task_need_emp_num = 0
        for task in comb_tasks_list:
            task_need_emp_num += int(task.combinationVal)

        # 员工的总工作时长 --- 间接算出 员工满足率
        dayWorkTime_minutes = 0
        for e_i in emp_list:
            dayWorkTime_minutes += e_i.dayWorkTime

        # 正式员工违反软约束的个数
        all_break_rule_num = 0
        for e_j in emp_list:
            all_break_rule_num += e_j.break_rule_num

        # 正式工违反的约束个数
        all_break_rule_list = []
        for e_l in emp_list:
            all_break_rule_list.extend(e_l.break_rule_list)

        # 安排上任务的员工个数
        working_emp_num = 0
        for e_k in emp_list:
            if(len(e_k.tasks) > 0):
                working_emp_num += 1

        # for obj in comb_tasks_list:
        #     print('+++++++++')
        #     print('\n'.join(['%s:%s' % item for item in obj.__dict__.items()]))
        #     print('++++++++++++++++++')

        # 缺少任务量的个数，员工集合，任务-员工字典，员工集合，任务需要的人数，任务组合列表,违反约束的内容
        return dayWorkTime_minutes, working_emp_num, all_break_rule_num, emp_list, task_need_emp_num, comb_tasks_list,all_break_rule_list

    @staticmethod
    def select_task_to_temp_emp(comb_task_list: List, work_date: str,task_all_info:Dict,comb_rule_info:Tuple, shift_split_rule_info: Tuple,
                                timeSize: int) -> List:
        '''
        生成临时工 工作时间表
        :param comb_task_list:
        :param work_date:
        :param shift_split_rule_info:
        :param timeSize:
        :return:
        '''

        temp_emp_list = []
        temp_eid = -1
        for task in comb_task_list:

            # 如果任务长度小于1小时跳过
            # if (sum(task.worktimeList) <= (60 // timeSize)): continue

            # 校验班次长度规则
            if(CheckTempEmpRule.check_shiftLen(task=task, shift_split_rule_info=shift_split_rule_info) is False):
                continue

            if ("缺人" in task.employees):
                task.employees.remove("缺人")

            emp_diff = int(task.combinationVal) - len(task.employees)

            while (emp_diff > 0):

                # 遍历已有员工是否能够分配该任务
                for t_e in temp_emp_list:

                    if(CheckTempEmpRule.check_shiftLen(task=task,shift_split_rule_info=shift_split_rule_info)
                        and CheckTempEmpRule.check_interval(temp_emp=t_e,task=task,shift_split_rule_info=shift_split_rule_info,timeSize=timeSize)
                        and CheckTempEmpRule.check_shiftNum(temp_emp=t_e,task=task,shift_split_rule_info=shift_split_rule_info)
                        and CheckTempEmpRule.check_workTime(temp_emp=t_e,task=task,shift_split_rule_info=shift_split_rule_info,timeSize=timeSize)
                        and CheckTempEmpRule.check_comb_rule(temp_emp=t_e,task=task,comb_rule_info=comb_rule_info,task_all_info=task_all_info)
                    ):

                        matix_emp_time = np.array(t_e.available_timeList)
                        matix_task_worktime = np.array(task.worktimeList)
                        # 如果员工可用时间中 不包含工作要求的时间 则不可用 否则 可用

                        result_matrix = np.bitwise_and(matix_emp_time, matix_task_worktime)
                        if ((result_matrix == matix_task_worktime).all()):
                            # 去掉员工相应的可用时间
                            matix_emp_time = np.bitwise_xor(matix_emp_time, matix_task_worktime).tolist()
                            t_e.available_timeList = matix_emp_time

                            # 更改对象相应的域
                            task.employees.append(t_e)
                            t_e.set_worktime(workTime=task.worktime_minutes)
                            t_e.set_did(task.did)
                            t_e.tasks.append(task)
                            # 更新班次个数
                            t_e.set_shift_num()

                            emp_diff -= 1
                            if (emp_diff == 0): break


                if (emp_diff != 0):
                    temp_emp = TemporaryEmployee(cid=task.cid,eid=str(temp_eid),work_date=work_date,
                                                 dayWorkTime=0,available_timeList=[1] * (24 * 60 // timeSize),
                                                 tasks=[],dayShiftNum=0)

                    matix_emp_time = np.array(temp_emp.available_timeList)
                    matix_task_worktime = np.array(task.worktimeList)

                    # 去掉员工相应的可用时间
                    matix_emp_time = np.bitwise_xor(matix_emp_time, matix_task_worktime).tolist()
                    temp_emp.available_timeList = matix_emp_time

                    # 更改对象相应的域
                    task.employees.append(temp_emp)
                    temp_emp.set_worktime(workTime=task.worktime_minutes)
                    temp_emp.tasks.append(task)

                    # 添加到临时员工列表
                    temp_emp_list.append(temp_emp)

                    temp_eid -= 1
                    emp_diff -= 1

        return temp_emp_list


    @staticmethod
    def select_task_to_temp_emp2(no_emp_comb_task_list: List, work_date: str,task_all_info:Dict,timeSize: int) -> List:
        temp_emp_list = []
        temp_eid = -1
        for task in no_emp_comb_task_list:

            if ("缺人" in task.employees):
                task.employees.remove("缺人")

            emp_diff = int(task.combinationVal) - len(task.employees)

            while (emp_diff > 0):


                temp_emp = TemporaryEmployee(cid=task.cid, eid=str(temp_eid), work_date=work_date,
                                             dayWorkTime=0, available_timeList=[1] * (24 * 60 // timeSize),
                                             tasks=[], dayShiftNum=0)

                # 更改对象相应的域
                task.employees.append(temp_emp)
                temp_emp.set_worktime(workTime=task.worktime_minutes)
                temp_emp.tasks.append(task)

                # 添加到临时员工列表
                temp_emp_list.append(temp_emp)

                temp_eid -= 1
                emp_diff -= 1

        return temp_emp_list


if __name__ == '__main__':

    pass

