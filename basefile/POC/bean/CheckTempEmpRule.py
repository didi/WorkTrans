from typing import Dict,Tuple,List,Set
from POC.bean.Employee import Employee
from POC.bean.TemporaryEmployee import TemporaryEmployee
from POC.bean.CombTasks import CombTasks
import datetime,calendar
from POC.bean.CheckRule import CheckRule


class CheckTempEmpRule:
    @staticmethod
    def check_shiftNum(temp_emp: TemporaryEmployee, task: CombTasks, shift_split_rule_info: Tuple):
        '''
        班次个数
        :param temp_emp:
        :param task:
        :param shift_split_rule_info:
        :return:
        '''
        for shift_split_rule in shift_split_rule_info:
            cid = shift_split_rule[0]

            if (cid == temp_emp.cid):
                did = shift_split_rule[1]
                ruleCalType = shift_split_rule[2]
                ruleCpType = shift_split_rule[3]
                ruleCpNum = float(shift_split_rule[4])
                dayFusion = shift_split_rule[5]

                # 班次个数
                if (ruleCalType == 'shiftNum' and ruleCpType == 'lt'):
                    if not (temp_emp.dayShiftNum + 1 < ruleCpNum):
                        return False

                    else:
                        continue

                if (ruleCalType == 'shiftNum' and ruleCpType == 'le'):
                    if not (temp_emp.dayShiftNum + 1 <= ruleCpNum):
                        return False

                    else:
                        continue
        return True

    @staticmethod
    def check_workTime(temp_emp: TemporaryEmployee, task: CombTasks, shift_split_rule_info: Tuple, timeSize: int):
        '''
        劳动工时
        :param temp_emp:
        :param task:
        :param shift_split_rule_info:
        :param timeSize:
        :return:
        '''
        for shift_split_rule in shift_split_rule_info:
            cid = shift_split_rule[0]

            if (cid == temp_emp.cid):
                did = shift_split_rule[1]
                ruleCalType = shift_split_rule[2]
                ruleCpType = shift_split_rule[3]
                ruleCpNum = float(shift_split_rule[4])
                dayFusion = shift_split_rule[5]

                # 工作时长
                if (ruleCalType == 'worktime' and ruleCpType == 'lt'):
                    if not (temp_emp.dayWorkTime + task.worktime_minutes < ruleCpNum):
                        return False
                    else:
                        continue


                if (ruleCalType == 'worktime' and ruleCpType == 'le'):
                    if not (temp_emp.dayWorkTime + task.worktime_minutes <= ruleCpNum):

                        return False
                    else:
                        continue
        return True

    @staticmethod
    def check_interval(temp_emp: TemporaryEmployee, task: CombTasks, shift_split_rule_info: Tuple, timeSize: int):
        '''
        班次间隔
        :param temp_emp:
        :param task:
        :param shift_split_rule_info:
        :param timeSize:
        :return:
        '''
        for shift_split_rule in shift_split_rule_info:
            cid = shift_split_rule[0]

            if (cid == temp_emp.cid):
                did = shift_split_rule[1]
                ruleCalType = shift_split_rule[2]
                ruleCpType = shift_split_rule[3]
                ruleCpNum = float(shift_split_rule[4])
                dayFusion = shift_split_rule[5]

                # 班次间隔

                if (ruleCalType == 'interval' and ruleCpType == 'lt'):
                    matrix_emp_time = np.array(temp_emp.available_timeList)
                    matrix_task_worktime = np.array(task.worktimeList)
                    # 如果员工可用时间中 不包含工作要求的时间 则不可用 否则 可用

                    result_matrix = np.bitwise_and(matrix_emp_time, matrix_task_worktime)
                    if ((result_matrix == matrix_task_worktime).all()):
                        index = CheckRule.search_start_end_index(task.worktimeList)
                        start_index = index["start"]
                        end_index = index["end"]

                        # 多个任务结合，形成总时间列表
                        matrix_all_task_worktime_list = np.array([0] * (24 * 60 // timeSize))
                        for t_task in temp_emp.tasks:
                            matrix_t_task_worktime = np.array(t_task.worktimeList)
                            matrix_all_task_worktime_list = np.bitwise_or(matrix_all_task_worktime_list,
                                                                          matrix_t_task_worktime)

                        all_task_worktime_list = matrix_all_task_worktime_list.tolist()

                        start_distance = CheckTempEmpRule.looking_forward_1(all_task_timeList=all_task_worktime_list,
                                                                     start_index=start_index)
                        end_distance = CheckTempEmpRule.looking_for_back_1(all_task_timeList=all_task_worktime_list,
                                                                    end_index=end_index)

                        if(start_distance == -1):
                            if(end_distance >= (int(ruleCpNum) // timeSize)):
                                return False
                        elif(end_distance == -1):
                            if (start_distance >= (int(ruleCpNum) // timeSize)):
                                return False
                        else:
                            if(start_distance >= (int(ruleCpNum) // timeSize) or end_distance >= (int(ruleCpNum) // timeSize)):
                                return False
                    else:
                        return False



                elif (ruleCalType == 'interval' and ruleCpType == 'le'):
                    matrix_emp_time = np.array(temp_emp.available_timeList)
                    matrix_task_worktime = np.array(task.worktimeList)
                    # 如果员工可用时间中 不包含工作要求的时间 则不可用 否则 可用

                    result_matrix = np.bitwise_and(matrix_emp_time, matrix_task_worktime)
                    if ((result_matrix == matrix_task_worktime).all()):
                        index = CheckRule.search_start_end_index(task.worktimeList)
                        start_index = index["start"]
                        end_index = index["end"]

                        # 多个任务结合，形成总时间列表
                        matrix_all_task_worktime_list = np.array([0] * (24 * 60 // timeSize))
                        for t_task in temp_emp.tasks:
                            matrix_t_task_worktime = np.array(t_task.worktimeList)
                            matrix_all_task_worktime_list = np.bitwise_or(matrix_all_task_worktime_list,
                                                                          matrix_t_task_worktime)

                        all_task_worktime_list = matrix_all_task_worktime_list.tolist()

                        start_distance = CheckTempEmpRule.looking_forward_1(all_task_timeList=all_task_worktime_list,
                                                                     start_index=start_index)
                        end_distance = CheckTempEmpRule.looking_for_back_1(all_task_timeList=all_task_worktime_list,
                                                                    end_index=end_index)

                        if (start_distance == -1):
                            if (end_distance > (int(ruleCpNum) // timeSize)):
                                return False
                        elif (end_distance == -1):
                            if (start_distance > (int(ruleCpNum) // timeSize)):
                                return False
                        else:
                            if (start_distance > (int(ruleCpNum) // timeSize) or end_distance > (
                                    int(ruleCpNum) // timeSize)):
                                return False

                    else:
                        return False

                if (ruleCalType == 'interval' and ruleCpType == 'gt'):
                    matrix_emp_time = np.array(temp_emp.available_timeList)
                    matrix_task_worktime = np.array(task.worktimeList)
                    # 如果员工可用时间中 不包含工作要求的时间 则不可用 否则 可用

                    result_matrix = np.bitwise_and(matrix_emp_time, matrix_task_worktime)
                    if ((result_matrix == matrix_task_worktime).all()):
                        index = CheckRule.search_start_end_index(task.worktimeList)
                        start_index = index["start"]
                        end_index = index["end"]

                        # 多个任务结合，形成总时间列表
                        matrix_all_task_worktime_list = np.array([0] * (24 * 60 // timeSize))
                        for t_task in temp_emp.tasks:
                            matrix_t_task_worktime = np.array(t_task.worktimeList)
                            matrix_all_task_worktime_list = np.bitwise_or(matrix_all_task_worktime_list,
                                                                          matrix_t_task_worktime)

                        all_task_worktime_list = matrix_all_task_worktime_list.tolist()

                        start_distance = CheckTempEmpRule.looking_forward_1(all_task_timeList=all_task_worktime_list,
                                                                     start_index=start_index)
                        end_distance = CheckTempEmpRule.looking_for_back_1(all_task_timeList=all_task_worktime_list,
                                                                    end_index=end_index)

                        if (start_distance == -1):
                            if (end_distance <= (int(ruleCpNum) // timeSize)):
                                return False
                        elif (end_distance == -1):
                            if (start_distance <= (int(ruleCpNum) // timeSize)):
                                return False
                        else:
                            if (start_distance <= (int(ruleCpNum) // timeSize) or end_distance <= (
                                    int(ruleCpNum) // timeSize)):
                                return False

                    else:
                        return False

                elif (ruleCalType == 'interval' and ruleCpType == 'ge'):
                    matrix_emp_time = np.array(temp_emp.available_timeList)
                    matrix_task_worktime = np.array(task.worktimeList)
                    # 如果员工可用时间中 不包含工作要求的时间 则不可用 否则 可用

                    result_matrix = np.bitwise_and(matrix_emp_time, matrix_task_worktime)
                    if ((result_matrix == matrix_task_worktime).all()):
                        index = CheckRule.search_start_end_index(task.worktimeList)
                        start_index = index["start"]
                        end_index = index["end"]

                        # 多个任务结合，形成总时间列表
                        matrix_all_task_worktime_list = np.array([0] * (24 * 60 // timeSize))
                        for t_task in temp_emp.tasks:
                            matrix_t_task_worktime = np.array(t_task.worktimeList)
                            matrix_all_task_worktime_list = np.bitwise_or(matrix_all_task_worktime_list,
                                                                          matrix_t_task_worktime)

                        all_task_worktime_list = matrix_all_task_worktime_list.tolist()

                        start_distance = CheckTempEmpRule.looking_forward_1(all_task_timeList=all_task_worktime_list,
                                                                     start_index=start_index)
                        end_distance = CheckTempEmpRule.looking_for_back_1(all_task_timeList=all_task_worktime_list,
                                                                    end_index=end_index)

                        if (start_distance == -1):
                            if (end_distance < (int(ruleCpNum) // timeSize)):
                                return False
                        elif (end_distance == -1):
                            if (start_distance < (int(ruleCpNum) // timeSize)):
                                return False
                        else:
                            if (start_distance < (int(ruleCpNum) // timeSize) or end_distance < (
                                    int(ruleCpNum) // timeSize)):
                                return False

                    else:
                        return False

        return True

    @staticmethod
    def looking_forward_1(all_task_timeList: List, start_index: int):
        '''
        向前找0 的 格子数
        :param available_timeList:
        :param start_index:
        :param ruleCpNum:
        :return:
        '''
        if (start_index >= len(all_task_timeList)):
            print("在寻找班次间隔过程中，存在数组越界")

        for i in range(start_index, -1, -1):

            if (all_task_timeList[i] == 1):
                return start_index - i - 1
        # 表示该任务前方没有任务
        return -1

    @staticmethod
    def looking_for_back_1(all_task_timeList:List, end_index: int):
        '''
        向前后找0 的 格子数
        :param available_timeList:
        :param end_index:
        :return:
        '''
        for i in range(end_index, len(all_task_timeList)):
            if (all_task_timeList[i] == 1):
                return i - end_index - 1
        # 表示该任后方没有任务
        return -1


    @staticmethod
    def check_shiftLen(task: CombTasks, shift_split_rule_info: Tuple):
        '''
        检查剩余任务的班次长度
        :param task:
        :param shift_split_rule_info:
        :param timeSize:
        :return:
        '''
        for shift_split_rule in shift_split_rule_info:
            cid = shift_split_rule[0]
            did = shift_split_rule[1]
            if(cid == task.cid and did == task.did):

                ruleCalType = shift_split_rule[2]
                ruleCpType = shift_split_rule[3]
                ruleCpNum = float(shift_split_rule[4])
                dayFusion = shift_split_rule[5]

                # 班次长度
                if (ruleCalType == 'shiftLen' and ruleCpType == 'lt' and task.worktime_minutes >= ruleCpNum):
                    return False

                if (ruleCalType == 'shiftLen' and ruleCpType == 'le'):
                    if not (task.worktime_minutes <= ruleCpNum):
                        return False

                if (ruleCalType == 'shiftLen' and ruleCpType == 'ge'):
                    if not (task.worktime_minutes >= ruleCpNum):
                        return False

                if (ruleCalType == 'shiftLen' and ruleCpType == 'gt'):
                    if not (task.worktime_minutes > ruleCpNum):
                        return False

            else:
                return False

        return True

    @staticmethod
    def check_shift_split_rule(temp_emp: TemporaryEmployee, task: CombTasks, shift_split_rule_info: Tuple, timeSize: int):
        '''
        校验临时员工 的 规则
        :param temp_emp:
        :param shift_split_rule_info:
        :return:
        '''
        for shift_split_rule in shift_split_rule_info:
            cid = shift_split_rule[0]

            if (cid == temp_emp.cid):
                did = shift_split_rule[1]
                ruleCalType = shift_split_rule[2]
                ruleCpType = shift_split_rule[3]
                ruleCpNum = int(shift_split_rule[4])
                dayFusion = shift_split_rule[5]

                # 班次个数
                if (ruleCalType == 'shiftNum' and ruleCpType == 'lt'):
                    if not (temp_emp.dayShiftNum + 1 < ruleCpNum):
                        return False

                    else:
                        continue

                elif (ruleCalType == 'shiftNum' and ruleCpType == 'le'):
                    if not (temp_emp.dayShiftNum + 1 <= ruleCpNum):
                        return False

                    else:
                        continue

                # 工作时长
                if (ruleCalType == 'worktime' and ruleCpType == 'lt'):
                    if not (temp_emp.dayWorkTime + task.worktime_minutes < ruleCpNum):
                        return False
                    else:
                        continue


                elif (ruleCalType == 'worktime' and ruleCpType == 'le'):
                    if not (temp_emp.dayWorkTime + task.worktime_minutes <= ruleCpNum):

                        return False
                    else:
                        continue

                # 班次间隔

                if (ruleCalType == 'interval' and ruleCpType == 'lt'):
                    matrix_emp_time = np.array(temp_emp.available_timeList)
                    matrix_task_worktime = np.array(task.worktimeList)
                    # 如果员工可用时间中 不包含工作要求的时间 则不可用 否则 可用

                    result_matrix = np.bitwise_and(matrix_emp_time, matrix_task_worktime)
                    if ((result_matrix == matrix_task_worktime).all()):
                        index = CheckRule.search_start_end_index(task.worktimeList)
                        start_index = index["start"]
                        end_index = index["end"]

                        # 多个任务结合，形成总时间列表
                        matrix_all_task_worktime_list = np.array([0] * (24 * 60 // timeSize))
                        for t_task in temp_emp.tasks:
                            matrix_t_task_worktime = np.array(t_task.worktimeList)
                            matrix_all_task_worktime_list = np.bitwise_or(matrix_all_task_worktime_list,
                                                                          matrix_t_task_worktime)

                        all_task_worktime_list = matrix_all_task_worktime_list.tolist()

                        start_distance = CheckRule.looking_forward_1(all_task_timeList=all_task_worktime_list,
                                                                     start_index=start_index)
                        end_distance = CheckRule.looking_for_back_1(all_task_timeList=all_task_worktime_list,
                                                                    end_index=end_index)

                        if  (start_distance >= (int(ruleCpNum) // timeSize) and end_distance >= (int(ruleCpNum) // timeSize)):
                            return False
                    else:
                        return False



                elif (ruleCalType == 'interval' and ruleCpType == 'le'):
                    matrix_emp_time = np.array(temp_emp.available_timeList)
                    matrix_task_worktime = np.array(task.worktimeList)
                    # 如果员工可用时间中 不包含工作要求的时间 则不可用 否则 可用

                    result_matrix = np.bitwise_and(matrix_emp_time, matrix_task_worktime)
                    if ((result_matrix == matrix_task_worktime).all()):
                        index = CheckRule.search_start_end_index(task.worktimeList)
                        start_index = index["start"]
                        end_index = index["end"]

                        # 多个任务结合，形成总时间列表
                        matrix_all_task_worktime_list = np.array([0] * (24 * 60 // timeSize))
                        for t_task in temp_emp.tasks:
                            matrix_t_task_worktime = np.array(t_task.worktimeList)
                            matrix_all_task_worktime_list = np.bitwise_or(matrix_all_task_worktime_list,
                                                                          matrix_t_task_worktime)

                        all_task_worktime_list = matrix_all_task_worktime_list.tolist()

                        start_distance = CheckRule.looking_forward_1(all_task_timeList=all_task_worktime_list,
                                                                     start_index=start_index)
                        end_distance = CheckRule.looking_for_back_1(all_task_timeList=all_task_worktime_list,
                                                                    end_index=end_index)

                        if(start_distance > (int(ruleCpNum) // timeSize) and end_distance > (int(ruleCpNum) // timeSize)):
                            return False

                    else:
                        return False

                elif (ruleCalType == 'interval' and ruleCpType == 'gt'):
                    matrix_emp_time = np.array(temp_emp.available_timeList)
                    matrix_task_worktime = np.array(task.worktimeList)
                    # 如果员工可用时间中 不包含工作要求的时间 则不可用 否则 可用

                    result_matrix = np.bitwise_and(matrix_emp_time, matrix_task_worktime)
                    if ((result_matrix == matrix_task_worktime).all()):
                        index = CheckRule.search_start_end_index(task.worktimeList)
                        start_index = index["start"]
                        end_index = index["end"]

                        # 多个任务结合，形成总时间列表
                        matrix_all_task_worktime_list = np.array([0] * (24 * 60 // timeSize))
                        for t_task in temp_emp.tasks:
                            matrix_t_task_worktime = np.array(t_task.worktimeList)
                            matrix_all_task_worktime_list = np.bitwise_or(matrix_all_task_worktime_list,
                                                                          matrix_t_task_worktime)

                        all_task_worktime_list = matrix_all_task_worktime_list.tolist()

                        start_distance = CheckRule.looking_forward_1(all_task_timeList=all_task_worktime_list,
                                                                     start_index=start_index)
                        end_distance = CheckRule.looking_for_back_1(all_task_timeList=all_task_worktime_list,
                                                                    end_index=end_index)

                        if (start_distance <= (int(ruleCpNum) // timeSize) and end_distance <= (int(ruleCpNum) // timeSize)):
                            return False

                    else:
                        return False

                if (ruleCalType == 'interval' and ruleCpType == 'ge'):
                    matrix_emp_time = np.array(temp_emp.available_timeList)
                    matrix_task_worktime = np.array(task.worktimeList)
                    # 如果员工可用时间中 不包含工作要求的时间 则不可用 否则 可用

                    result_matrix = np.bitwise_and(matrix_emp_time, matrix_task_worktime)
                    if ((result_matrix == matrix_task_worktime).all()):
                        index = CheckRule.search_start_end_index(task.worktimeList)
                        start_index = index["start"]
                        end_index = index["end"]

                        # 多个任务结合，形成总时间列表
                        matrix_all_task_worktime_list = np.array([0] * (24 * 60 // timeSize))
                        for t_task in temp_emp.tasks:
                            matrix_t_task_worktime = np.array(t_task.worktimeList)
                            matrix_all_task_worktime_list = np.bitwise_or(matrix_all_task_worktime_list,
                                                                          matrix_t_task_worktime)

                        all_task_worktime_list = matrix_all_task_worktime_list.tolist()

                        start_distance = CheckRule.looking_forward_1(all_task_timeList=all_task_worktime_list,
                                                                     start_index=start_index)
                        end_distance = CheckRule.looking_for_back_1(all_task_timeList=all_task_worktime_list,
                                                                    end_index=end_index)

                        if (start_distance < (int(ruleCpNum) // timeSize) and end_distance < (int(ruleCpNum) // timeSize)):
                            return False

                    else:
                        return False

        return True

    @staticmethod
    def check_comb_rule(temp_emp: TemporaryEmployee, task: CombTasks, task_all_info: Dict, comb_rule_info: Tuple):
        '''
        检查 组合规则
        :param temp_emp:
        :param task:
        :param comb_rule_info:
        :return:
        '''
        # 获取间接任务的taskBid
        indirectwh = ''
        for task_dict in task_all_info.values():
            if (task_dict["taskType"] == "indirectwh"):
                indirectwh = task_dict['taskBid']

        for comb_rule in comb_rule_info:
            cid = comb_rule[0]

            if (cid == temp_emp.cid):

                # 获取员工已经安排上的任务
                emp_task_list = []
                for task_ in temp_emp.tasks:
                    emp_task_list.extend(task_.taskId)

                # 添加 当前需要安排的任务
                emp_task_list.extend(task.taskId)
                task_set = set(emp_task_list)
                # 删除 间接任务
                if (indirectwh in task_set):
                    task_set.remove(indirectwh)

                # 组织规则 列表
                comb_rule_list = comb_rule[2].split(",")
                comb_rule_set = set(comb_rule_list)

                if (task_set.issubset(comb_rule_set)):
                    return True
        return False








