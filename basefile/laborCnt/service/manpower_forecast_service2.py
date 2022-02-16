#!/usr/bin/env python
# encoding: utf-8

"""
@author: sunsong
@contact: sunsong@didiglobal.com
@file: manpower_forecast_service.py
@time: 2019/9/16 8:37 下午
@desc:
"""
import copy
import threading
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Union, Tuple
import pandas as pd

from laborCnt.model.manpower_forecast_db import ManPowerForecastDB
from laborCnt.algorithm.manpower_planner import Planner
from utils.dateUtils import DateUtils
from utils.task import DirectTask, InDirectTask, FixedTask
from utils.myLogger import infoLog


class ManPowerForecastService:

    @staticmethod
    def manpower_forecast(cid: str, bid: str, time_interval: int, did_arr: List[int], forecast_date_start: str,
                          forecast_date_end: str, shift_mod: List[Dict[str, Any]], combi_rule: List[Dict[str, Any]],
                          shiftsplitrule: List[Dict[str, Any]], save_method: int = 0, debug: bool = False, **kw) \
            -> Dict[str, Union[int, str]]:
        """
        劳动力人数预测主函数 by sunsong
        :param time_interval: 时间粒度 分钟
        :param cid: cid
        :param bid: legacy 现在为forecast type 影响取数
        :param did_arr: did列表
        :param forecast_date_start: 开始日期 包含
        :param forecast_date_end: 结束日期 包含
        :param shift_mod: 班次模板
        :param combi_rule: 组合规则
        :param shiftsplitrule: 拆分规则
        :param save_method: 0 同步 1 异步
        :param debug: 调试模式
        :return:
        """
        infoLog.info('ManPowerForecast Working Path: ' + str(os.getcwd()))

        # 特殊公司（喜茶 华为等） 特殊处理
        if str(cid) in ['50000735', '50000895', '60000039', '50000863']:
            with_break = True
            multiple_cal = True
            pseudo_gaussian = True
            min_shift_len = 60
            max_shift_len = ManPowerForecastDB.get_max_shift_length_from_sch_compliance(cid, forecast_date_start)
            if max_shift_len % int(time_interval) != 0:
                max_shift_len = (max_shift_len // int(time_interval)) * int(time_interval)
            if str(cid) == '50000863':
                max_break_count = 5
            else:
                max_break_count = 3
            priority_task_list = ManPowerForecastDB.get_open_shutdown_task_id_list(cid, str(did_arr[0]))
        else:
            with_break: bool = kw.get('with_break', False)
            multiple_cal: bool = kw.get('multiple_cal', False)
            pseudo_gaussian = False
            min_shift_len = 60
            max_shift_len = 480
            max_break_count = 3
            priority_task_list = []

        if debug:
            task_name_dict = ManPowerForecastDB.get_task_id_list(cid, str(did_arr[0]))
            task_name_dict['break'] = '休息'
            task_name_dict[''] = ''
        else:
            task_name_dict = {}

        multiple_cal_times: int = kw.get('multiple_cal_times', 20)  # 多次计算次数

        save_result = {'code': 0, 'result': '未处理', 'data': None}

        # 获取开始日期到结束日期之间所有日期罗列的列表
        date_arr: List[str] = DateUtils.get_date_array(forecast_date_start, forecast_date_end)

        # 组合规则处理
        combine_rules: List[str] = []
        if combi_rule:
            for item in combi_rule:
                # TODO: did判定
                if 'combiRuleData' in item:
                    rule_data = item['combiRuleData']
                    for i in rule_data:
                        if 'ruleData' in i:
                            rule: str = i['ruleData']
                            if len(rule.split(',')) > 1:
                                combine_rules.append(rule)

        # 拆分规则处理
        interval_rules: List[Tuple[str, int, bool]] = []
        working_hour_rules: List[Tuple[str, int, bool]] = []
        shift_num_rules: List[Tuple[str, int, bool]] = []
        task_count_rules: List[Tuple[str, int, bool]] = []
        fill_coef_rules: List[Tuple[str, float, bool]] = []
        shift_len_rules = []
        is_cross_day: bool = False
        if shiftsplitrule:
            # TODO: did判定
            for item in shiftsplitrule:
                if 'shiftsplitData' in item:
                    shift_split_data = item['shiftsplitData']
                    for i in shift_split_data:
                        if 'ruleCalType' in i:
                            rule_cal_type = i['ruleCalType']
                            if rule_cal_type == 'interval':
                                interval_rules.append((i['ruleCpType'], int(i['ruleCpNum']), i['dayFusion']))
                            elif rule_cal_type == 'shiftNum':
                                shift_num_rules.append((i['ruleCpType'], int(i['ruleCpNum']), i['dayFusion']))
                            elif rule_cal_type == 'worktime':
                                working_hour_rules.append((i['ruleCpType'], int(i['ruleCpNum']), i['dayFusion']))
                            elif rule_cal_type == 'shiftLen':
                                shift_len_rules.append((i['ruleCpType'], int(i['ruleCpNum']), i['dayFusion']))
                            elif rule_cal_type == 'fillCoefficient':
                                fill_coef_rules.append((i['ruleCpType'], float(i['ruleCpNum']), i['dayFusion']))
                            elif rule_cal_type == 'taskCount':
                                task_count_rules.append((i['ruleCpType'], int(i['ruleCpNum']), i['dayFusion']))
                        if 'dayFusion' in i:
                            day_fusion = i['dayFusion']
                            is_cross_day = is_cross_day or day_fusion
        # 班次模板规则处理
        shift_mod_rules = []
        if shift_mod:
            for item in shift_mod:
                shift_mod_data = item.get('shiftModData', [])
                # TODO: did判定
                if shift_mod_data:
                    for template in shift_mod_data:
                        shift_start = template.get('shiftStart', '')
                        shift_end = template.get('shiftEnd', '')
                        is_cross_day = template.get('isCrossDay', False)
                        if shift_start and shift_end:
                            shift_mod_rules.append((shift_start, shift_end, is_cross_day))

        # 读取所有任务信息
        fix_task_dict, direct_task_dict, indirect_task_dict, min_fix_task_dict, min_direct_task_dict, \
        min_indirect_task_dict, max_fix_task_dict, max_direct_task_dict, max_indirect_task_dict = \
            ManPowerForecastDB.get_task_info_by_peroid2(cid, str(did_arr[0]), forecast_date_start, forecast_date_end,
                                                        bid)

        res_arr: List[Dict] = []
        planner_dict: Dict[str, Tuple[Planner, str, str]] = {}
        min_planner_dict: Dict[str, Tuple[Planner, str, str]] = {}
        max_planner_dict: Dict[str, Tuple[Planner, str, str]] = {}

        result_flag = True
        result_reason = ''
        for date in date_arr:
            """
            对每天分别进行计算
            """
            infoLog.info('starting planner for date: ' + str(date) + '...')

            # 读取每天的任务列表
            fixed_tasks: List[FixedTask] = fix_task_dict.get(date, [])
            direct_tasks: List[DirectTask] = direct_task_dict.get(date, [])
            indirect_tasks: List[InDirectTask] = indirect_task_dict.get(date, [])
            # 任务预测值的上下限 用来生成最大最小矩阵用
            fixed_tasks_min: List[FixedTask] = min_fix_task_dict.get(date, [])
            direct_tasks_min: List[DirectTask] = min_direct_task_dict.get(date, [])
            indirect_tasks_min: List[InDirectTask] = min_indirect_task_dict.get(date, [])
            fixed_tasks_max: List[FixedTask] = max_fix_task_dict.get(date, [])
            direct_tasks_max: List[DirectTask] = max_direct_task_dict.get(date, [])
            indirect_tasks_max: List[InDirectTask] = max_indirect_task_dict.get(date, [])

            if debug:
                print("******************")
                print("date: " + str(date))
                """
                print("db")
                sum_work_time = 0
                work_time = 0
                for task in fixed_tasks:
                    work_time += task.work_time
                print("fixed_tasks work time: " + str(work_time))
                sum_work_time += work_time
                work_time = 0
                for task in direct_tasks:
                    work_time += task.work_time
                print("direct tasks work time: " + str(work_time))
                sum_work_time += work_time
                work_time = 0
                for task in indirect_tasks:
                    work_time += task.work_time
                print("indirect tasks work time: " + str(work_time))
                sum_work_time += work_time
                print("total tasks work time from db: " + str(sum_work_time))
                """

            # 获取开始结束时间 TODO: 改为传入参数更为准确
            start_time, end_time = DateUtils.get_start_time_and_end_time(fixed_tasks, direct_tasks, is_cross_day)

            if not multiple_cal:
                """
                如果只需要计算一次
                """
                planner = Planner(start_time, end_time, int(time_interval), fixed_tasks, direct_tasks, indirect_tasks,
                                  combine_rules, False, interval_rules, working_hour_rules, shift_num_rules,
                                  shift_len_rules, fill_coef_rules, task_count_rules, shift_mod_rules, True, True,
                                  debug=debug, with_break=with_break, priority_task_list=priority_task_list,
                                  max_break_count=max_break_count)
                planner_min = Planner(start_time, end_time, int(time_interval), fixed_tasks_min, direct_tasks_min,
                                      indirect_tasks_min, combine_rules, False, interval_rules, working_hour_rules,
                                      shift_num_rules, shift_len_rules, fill_coef_rules, task_count_rules,
                                      shift_mod_rules, True, True, with_break=with_break,
                                      priority_task_list=priority_task_list, max_break_count=max_break_count)
                planner_max = Planner(start_time, end_time, int(time_interval), fixed_tasks_max, direct_tasks_max,
                                      indirect_tasks_max, combine_rules, False, interval_rules, working_hour_rules,
                                      shift_num_rules, shift_len_rules, fill_coef_rules, task_count_rules,
                                      shift_mod_rules, True, True, with_break=with_break,
                                      priority_task_list=priority_task_list, max_break_count=max_break_count)
            else:
                """
                如果需要多次计算
                """
                planner_list: List[Planner] = []
                if not pseudo_gaussian:
                    """
                    如果不需要高斯分布
                    """
                    for i in range(multiple_cal_times):
                        planner_list.append(Planner(start_time, end_time, int(time_interval), fixed_tasks, direct_tasks,
                                                    indirect_tasks, combine_rules, False, interval_rules,
                                                    working_hour_rules, shift_num_rules, shift_len_rules,
                                                    fill_coef_rules,
                                                    task_count_rules, shift_mod_rules, True, True, debug=debug,
                                                    with_break=with_break, priority_task_list=priority_task_list,
                                                    max_break_count=max_break_count))
                else:
                    """
                    模拟高斯分布
                    """
                    for i in range(multiple_cal_times):
                        tmp_matrix = []
                        matrix = []
                        original_planner = Planner(start_time, end_time, int(time_interval), fixed_tasks, direct_tasks,
                                                   indirect_tasks, combine_rules, False, interval_rules,
                                                   working_hour_rules, shift_num_rules, shift_len_rules,
                                                   fill_coef_rules, task_count_rules, shift_mod_rules, True, True,
                                                   debug=False, with_break=with_break,
                                                   priority_task_list=priority_task_list,
                                                   max_break_count=max_break_count)
                        new_fixed_tasks = copy.deepcopy(fixed_tasks)
                        new_direct_tasks = copy.deepcopy(direct_tasks)
                        new_indirect_tasks = copy.deepcopy(indirect_tasks)

                        break_count = [0 for _ in range(original_planner.time_block_length)]

                        # 优先排开铺打烊任务
                        for j in range(max_shift_len, 450, -int(time_interval)):
                            # 正排
                            tmp_matrix = []
                            new_shift_len_rules = [('ge', j, True), ('le', max_shift_len, True)]
                            planner = Planner(start_time, end_time, int(time_interval), new_fixed_tasks,
                                              new_direct_tasks, new_indirect_tasks, combine_rules, False,
                                              interval_rules, working_hour_rules, shift_num_rules, new_shift_len_rules,
                                              fill_coef_rules, task_count_rules, shift_mod_rules, True, True,
                                              debug=debug, with_break=with_break,
                                              priority_task_list=priority_task_list, max_break_count=max_break_count,
                                              only_generate_priority_tasks=True, prev_no_break_time=150,
                                              break_count=break_count)
                            now_matrix = planner.get_full_matrix()
                            for line in now_matrix:
                                if is_line_meet_req(line, j, max_shift_len, int(time_interval)):
                                    overlapped_task_list = [i for i in list(set(line)) if i in priority_task_list]
                                    if overlapped_task_list:
                                        matrix.append(line)
                                    else:
                                        tmp_matrix.append(line)
                                else:
                                    tmp_matrix.append(line)
                            if not tmp_matrix:
                                break
                            else:
                                new_fixed_tasks, new_direct_tasks, new_indirect_tasks = \
                                    convert_matrix_to_tasks(tmp_matrix, original_planner)

                            break_count = [0 for _ in range(original_planner.time_block_length)]
                            for line in matrix:
                                for k in range(len(line)):
                                    task_bid = line[k]
                                    if task_bid == 'break':
                                        break_count[k] = break_count[k] + 1

                            # 逆排
                            tmp_matrix = []
                            r_fixed_tasks = reverse_task_list(new_fixed_tasks, start_time, end_time)
                            r_direct_tasks = reverse_task_list(new_direct_tasks, start_time, end_time)
                            planner = Planner(start_time, end_time, int(time_interval), r_fixed_tasks,
                                              r_direct_tasks, new_indirect_tasks, combine_rules, False,
                                              interval_rules, working_hour_rules, shift_num_rules, new_shift_len_rules,
                                              fill_coef_rules, task_count_rules, shift_mod_rules, True, True,
                                              debug=debug, with_break=with_break,
                                              priority_task_list=priority_task_list, max_break_count=max_break_count,
                                              only_generate_priority_tasks=True, prev_no_break_time=150,
                                              break_count=break_count)
                            now_matrix = planner.get_full_matrix()
                            for line in now_matrix:
                                if is_line_meet_req(line, j, max_shift_len, int(time_interval)):
                                    overlapped_task_list = [i for i in list(set(line)) if i in priority_task_list]
                                    if overlapped_task_list:
                                        matrix.append(line[::-1])
                                    else:
                                        tmp_matrix.append(line[::-1])
                                else:
                                    tmp_matrix.append(line[::-1])
                            if not tmp_matrix:
                                break
                            else:
                                new_fixed_tasks, new_direct_tasks, new_indirect_tasks = \
                                    convert_matrix_to_tasks(tmp_matrix, original_planner)

                            break_count = [0 for _ in range(original_planner.time_block_length)]
                            for line in matrix:
                                for k in range(len(line)):
                                    task_bid = line[k]
                                    if task_bid == 'break':
                                        break_count[k] = break_count[k] + 1

                        # 正常排班
                        for j in range(max_shift_len, min_shift_len - int(time_interval), -int(time_interval)):
                            # 正排
                            tmp_matrix = []
                            new_shift_len_rules = [('ge', j, True), ('le', max_shift_len, True)]
                            planner = Planner(start_time, end_time, int(time_interval), new_fixed_tasks,
                                              new_direct_tasks, new_indirect_tasks, combine_rules, False,
                                              interval_rules, working_hour_rules, shift_num_rules, new_shift_len_rules,
                                              fill_coef_rules, task_count_rules, shift_mod_rules, True, True,
                                              debug=debug, with_break=with_break,
                                              priority_task_list=priority_task_list, max_break_count=max_break_count,
                                              break_count=break_count)
                            now_matrix = planner.get_full_matrix()
                            for line in now_matrix:
                                if is_line_meet_req(line, j, max_shift_len, int(time_interval)):
                                    matrix.append(line)
                                else:
                                    tmp_matrix.append(line)
                            if not tmp_matrix:
                                break
                            else:
                                new_fixed_tasks, new_direct_tasks, new_indirect_tasks = \
                                    convert_matrix_to_tasks(tmp_matrix, original_planner)

                            break_count = [0 for _ in range(original_planner.time_block_length)]
                            for line in matrix:
                                for k in range(len(line)):
                                    task_bid = line[k]
                                    if task_bid == 'break':
                                        break_count[k] = break_count[k] + 1

                            # 逆排
                            tmp_matrix = []
                            r_fixed_tasks = reverse_task_list(new_fixed_tasks, start_time, end_time)
                            r_direct_tasks = reverse_task_list(new_direct_tasks, start_time, end_time)
                            planner = Planner(start_time, end_time, int(time_interval), r_fixed_tasks,
                                              r_direct_tasks, new_indirect_tasks, combine_rules, False,
                                              interval_rules, working_hour_rules, shift_num_rules, new_shift_len_rules,
                                              fill_coef_rules, task_count_rules, shift_mod_rules, True, True,
                                              debug=debug, with_break=with_break,
                                              priority_task_list=priority_task_list, max_break_count=max_break_count)
                            now_matrix = planner.get_full_matrix()
                            for line in now_matrix:
                                if is_line_meet_req(line, j, max_shift_len, int(time_interval)):
                                    matrix.append(line[::-1])
                                else:
                                    tmp_matrix.append(line[::-1])
                            if not tmp_matrix:
                                break
                            else:
                                new_fixed_tasks, new_direct_tasks, new_indirect_tasks = \
                                    convert_matrix_to_tasks(tmp_matrix, original_planner)

                            break_count = [0 for _ in range(original_planner.time_block_length)]
                            for line in matrix:
                                for k in range(len(line)):
                                    task_bid = line[k]
                                    if task_bid == 'break':
                                        break_count[k] = break_count[k] + 1

                        if tmp_matrix:
                            for line in tmp_matrix:
                                matrix.append(line)
                        original_planner.matrix = matrix
                        planner_list.append(original_planner)

                # 评分 拿到评价最好的排班结果
                planner = get_better_planner(planner_list, time_interval=int(time_interval), cid=cid, did=did_arr[0])
                planner_min = Planner(start_time, end_time, int(time_interval), fixed_tasks_min, direct_tasks_min,
                                      indirect_tasks_min, combine_rules, False, interval_rules, working_hour_rules,
                                      shift_num_rules, shift_len_rules, fill_coef_rules, task_count_rules,
                                      shift_mod_rules, True, True, with_break=with_break,
                                      priority_task_list=priority_task_list, max_break_count=max_break_count)
                planner_max = Planner(start_time, end_time, int(time_interval), fixed_tasks_max, direct_tasks_max,
                                      indirect_tasks_max, combine_rules, False, interval_rules, working_hour_rules,
                                      shift_num_rules, shift_len_rules, fill_coef_rules, task_count_rules,
                                      shift_mod_rules, True, True, with_break=with_break,
                                      priority_task_list=priority_task_list, max_break_count=max_break_count)

            if debug:
                # pd.DataFrame(planner.get_full_matrix()).to_csv(date + '_full.csv')
                # pd.DataFrame(planner_min.get_full_matrix()).to_csv(date + '_min.csv')
                # pd.DataFrame(planner_max.get_full_matrix()).to_csv(date + '_max.csv')
                # pd.DataFrame(planner.debug_matrix).to_csv(date + '_fill.csv')

                task_name_matrix = []
                for line in planner.get_full_matrix():
                    new_line = []
                    for t in line:
                        new_line.append(task_name_dict.get(t, t))
                    task_name_matrix.append(new_line)
                pd.DataFrame(task_name_matrix).to_csv(date + '_full.csv')

                print_task_matrix_detail(planner.get_full_matrix(), task_name_dict)

                """
                print("matrix")
                matrix = planner.get_full_matrix()
                f_list = planner.fixed_tasks_list
                d_list = planner.direct_tasks_list
                i_list = planner.indirect_tasks_list
                block_length = planner.block_length
                f_work_time = 0
                d_work_time = 0
                i_work_time = 0
                for line in matrix:
                    for task in line:
                        if task:
                            if task != 'break':
                                if task in f_list:
                                    f_work_time += block_length
                                elif task in d_list:
                                    d_work_time += block_length
                                elif task in i_list:
                                    i_work_time += block_length
                                else:
                                    print('task err: ' + task)
                print("fixed_tasks work time: " + str(f_work_time))
                print("direct tasks work time: " + str(d_work_time))
                print("indirect tasks work time: " + str(i_work_time))
                print("total tasks work time from matrix: " + str(f_work_time + d_work_time + i_work_time))
                """

            # planner 如果失败
            if not planner.matrix_flag:
                result_flag = False
                result_reason = planner.fail_reason
                break

            # 最小人力planner 如果失败
            if not planner_min.matrix_flag:
                result_flag = False
                result_reason = planner_min.fail_reason
                break

            # 最大人力planner 如果失败
            if not planner_max.matrix_flag:
                result_flag = False
                result_reason = planner.fail_reason
                break

            planner_dict[date] = (planner, start_time, end_time)
            min_planner_dict[date] = (planner_min, start_time, end_time)
            max_planner_dict[date] = (planner_max, start_time, end_time)

            res_dict = planner.to_dict_new(planner_min.get_full_matrix(), planner_max.get_full_matrix())

            res_arr.append({
                date: res_dict
            })

        # 异步处理matrix insert
        if result_flag:
            if save_method == 1:
                # 异步
                insert_thread_list = []
                for date in planner_dict:
                    item = planner_dict[date]
                    planner = item[0]
                    start_time = item[1]
                    end_time = item[2]
                    t = threading.Thread(target=insert_matrix,
                                         args=(cid, str(did_arr[0]), bid, 'full', date, start_time,
                                               end_time, planner))
                    insert_thread_list.append(t)
                for date in min_planner_dict:
                    item = min_planner_dict[date]
                    planner = item[0]
                    start_time = item[1]
                    end_time = item[2]
                    t = threading.Thread(target=insert_matrix, args=(cid, str(did_arr[0]), bid, 'min', date, start_time,
                                                                     end_time, planner))
                    insert_thread_list.append(t)
                for date in max_planner_dict:
                    item = max_planner_dict[date]
                    planner = item[0]
                    start_time = item[1]
                    end_time = item[2]
                    t = threading.Thread(target=insert_matrix, args=(cid, str(did_arr[0]), bid, 'max', date, start_time,
                                                                     end_time, planner))
                    insert_thread_list.append(t)

                for t in insert_thread_list:
                    t.start()
            else:
                # 同步
                for date in planner_dict:
                    item = planner_dict[date]
                    planner = item[0]
                    start_time = item[1]
                    end_time = item[2]
                    ManPowerForecastDB.insert_matrix_ss(cid, str(did_arr[0]), bid, 'full', date, start_time, end_time,
                                                        planner.get_full_matrix())
                for date in min_planner_dict:
                    item = min_planner_dict[date]
                    planner = item[0]
                    start_time = item[1]
                    end_time = item[2]
                    ManPowerForecastDB.insert_matrix_ss(cid, str(did_arr[0]), bid, 'min', date, start_time, end_time,
                                                        planner.get_full_matrix())
                for date in max_planner_dict:
                    item = max_planner_dict[date]
                    planner = item[0]
                    start_time = item[1]
                    end_time = item[2]
                    ManPowerForecastDB.insert_matrix_ss(cid, str(did_arr[0]), bid, 'max', date, start_time, end_time,
                                                        planner.get_full_matrix())

        if result_flag:
            save_result['code'] = 100
            save_result['result'] = '成功'
            save_result["data"] = {
                'manpowers': res_arr
            }
        else:
            save_result['code'] = 108
            save_result['result'] = '预测失败，原因：' + result_reason
            save_result["data"] = {
                'manpowers': []
            }

        return save_result

    @staticmethod
    def manpower_forecast_recal(cid: str, bid: str, time_interval: int, did_arr: List[int], forecast_date_start: str,
                                forecast_date_end: str, shift_mod: List[Dict[str, Any]],
                                combi_rule: List[Dict[str, Any]], shiftsplitrule: List[Dict[str, Any]],
                                direct_task_dict_in: Dict[str, List[DirectTask]],
                                fixed_task_dict_in: Dict[str, List[FixedTask]],
                                indirect_task_dict_in: Dict[str, List[InDirectTask]], recal: bool = False,
                                debug: bool = False) \
            -> Tuple[bool, str, Dict[str, Tuple[List[List[str]], str, str]]]:
        """
        劳动力人数迭代计算 by sunsong
        :param recal:
        :param indirect_task_dict_in:
        :param fixed_task_dict_in:
        :param direct_task_dict_in:
        :param debug:
        :param time_interval: 时间粒度
        :param cid:
        :param bid:
        :param did_arr:
        :param forecast_date_start:
        :param forecast_date_end:fo
        :param shift_mod:
        :param combi_rule:
        :param shiftsplitrule:
        :param: debug:
        :return: Tuple[是否成功，失败原因，矩阵dict：[日期 -> (矩阵，start_time, end_time)]
        """

        # 喜茶判断
        if str(cid) in ['50000735', '50000895', '60000039', '50000863']:
            with_break = True
            priority_task_list = ManPowerForecastDB.get_open_shutdown_task_id_list(cid, str(did_arr[0]))
        else:
            with_break = False
            priority_task_list = []

        date_arr = DateUtils.get_date_array(forecast_date_start, forecast_date_end)

        # 组合规则
        combine_rules: List[str] = []
        if combi_rule:
            for item in combi_rule:
                # TODO: did判定
                if 'combiRuleData' in item:
                    rule_data = item['combiRuleData']
                    for i in rule_data:
                        if 'ruleData' in i:
                            rule: str = i['ruleData']
                            if len(rule.split(',')) > 1:
                                combine_rules.append(rule)

        # 拆分规则
        interval_rules: List[Tuple[str, int, bool]] = []
        working_hour_rules: List[Tuple[str, int, bool]] = []
        shift_num_rules: List[Tuple[str, int, bool]] = []
        task_count_rules: List[Tuple[str, int, bool]] = []
        fill_coef_rules: List[Tuple[str, float, bool]] = []
        shift_len_rules = []
        is_cross_day: bool = False
        if shiftsplitrule:
            # TODO: did判定
            for item in shiftsplitrule:
                if 'shiftsplitData' in item:
                    shift_split_data = item['shiftsplitData']
                    for i in shift_split_data:
                        if 'ruleCalType' in i:
                            rule_cal_type = i['ruleCalType']
                            if rule_cal_type == 'interval':
                                interval_rules.append((i['ruleCpType'], int(i['ruleCpNum']), i['dayFusion']))
                            elif rule_cal_type == 'shiftNum':
                                shift_num_rules.append((i['ruleCpType'], int(i['ruleCpNum']), i['dayFusion']))
                            elif rule_cal_type == 'worktime':
                                working_hour_rules.append((i['ruleCpType'], int(i['ruleCpNum']), i['dayFusion']))
                            elif rule_cal_type == 'shiftLen':
                                shift_len_rules.append((i['ruleCpType'], int(i['ruleCpNum']), i['dayFusion']))
                            elif rule_cal_type == 'fillCoefficient':
                                fill_coef_rules.append((i['ruleCpType'], float(i['ruleCpNum']), i['dayFusion']))
                            elif rule_cal_type == 'taskCount':
                                task_count_rules.append((i['ruleCpType'], int(i['ruleCpNum']), i['dayFusion']))
                        if 'dayFusion' in i:
                            day_fusion = i['dayFusion']
                            is_cross_day = is_cross_day or day_fusion
        # 班次模板规则
        shift_mod_rules = []
        if shift_mod:
            for item in shift_mod:
                shift_mod_data = item.get('shiftModData', [])
                # TODO: did判定
                if shift_mod_data:
                    for template in shift_mod_data:
                        shift_start = template.get('shiftStart', '')
                        shift_end = template.get('shiftEnd', '')
                        is_cross_day = template.get('isCrossDay', False)
                        if shift_start and shift_end:
                            shift_mod_rules.append((shift_start, shift_end, is_cross_day))

        fix_task_dict_db, direct_task_dict_db, indirect_task_dict_db, _, _, _, _, _, _ = \
            ManPowerForecastDB.get_task_info_by_peroid2(cid, str(did_arr[0]), forecast_date_start,
                                                        forecast_date_end,
                                                        bid)

        if not recal:
            fix_task_dict = fix_task_dict_db
            direct_task_dict = direct_task_dict_db
            indirect_task_dict = indirect_task_dict_db
        else:
            fix_task_dict = fixed_task_dict_in
            direct_task_dict = direct_task_dict_in
            indirect_task_dict = indirect_task_dict_in

        planner_dict: Dict[str, Tuple[List[List[str]], str, str]] = {}

        result_flag = True
        result_reason = ''
        for date in date_arr:
            fixed_tasks = fix_task_dict.get(date, [])
            direct_tasks = direct_task_dict.get(date, [])
            indirect_tasks = indirect_task_dict.get(date, [])

            fixed_tasks_db = fix_task_dict_db.get(date, [])
            direct_tasks_db = direct_task_dict_db.get(date, [])

            start_time, end_time = DateUtils.get_start_time_and_end_time(fixed_tasks_db, direct_tasks_db, is_cross_day)
            planner = Planner(start_time, end_time, int(time_interval), fixed_tasks, direct_tasks, indirect_tasks,
                              combine_rules, False, interval_rules, working_hour_rules, shift_num_rules,
                              shift_len_rules, fill_coef_rules, task_count_rules, shift_mod_rules, True, True,
                              with_break=with_break, priority_task_list=priority_task_list)

            if debug:
                pd.DataFrame(planner.get_full_matrix()).to_csv(date + '_full_recal.csv')

            # planner 如果失败
            if not planner.matrix_flag:
                result_flag = False
                result_reason = planner.fail_reason
                break

            planner_dict[date] = (planner.get_full_matrix(), start_time, end_time)

        if result_flag:
            return True, '', planner_dict
        else:
            return False, result_reason, {}


def insert_matrix(cid: str, did: str, forecastType, method: str, date: str, start_time: str, end_time: str,
                  planner: Planner):
    """
    insert
    """
    ManPowerForecastDB.insert_matrix_ss(cid, did, forecastType, method, date, start_time, end_time,
                                        planner.get_full_matrix())


def get_better_planner(planner_list: List[Planner], **kw) -> Planner:
    """
    评分函数
    :param planner_list:
    :param kw:
    :return:
    """
    block_length: int = kw.get('time_interval', 30)
    cid: str = str(kw.get('cid', ''))
    did: str = str(kw.get('did', ''))

    score_list: List[float] = [0 for _ in planner_list]  # 总得分
    matrix_list: List[List[List[str]]] = []
    for planner in planner_list:
        matrix_list.append(planner.get_full_matrix())

    # 人力数
    manpower_num: List[int] = []
    for matrix in matrix_list:
        manpower_num.append(-len(matrix))  # 人力越少越好，用负数表示
    manpower_score = average_score(manpower_num, 20)

    # 班次长度
    eight_hour_shift_num: List[int] = []
    nine_hour_shift_num: List[int] = []
    seven_hour_shift_num: List[int] = []
    for matrix in matrix_list:
        eight_hour_shift: int = 0
        nine_hour_shift: int = 0
        seven_hour_shift: int = 0
        for line in matrix:
            # TODO: 默认班次数为1，如果班次数更多 此处需要修改
            new_line: List[str] = []
            for task in line:
                if task:
                    if task != 'break':
                        new_line.append(task)
            task_num = len(new_line)
            work_time = task_num * block_length
            if work_time / 60 <= 9:
                if work_time / 60 >= 8.5:
                    nine_hour_shift += 1
                elif work_time / 60 >= 7.5:
                    eight_hour_shift += 1
                elif work_time / 60 >= 6.5:
                    seven_hour_shift += 1
        eight_hour_shift_num.append(eight_hour_shift)
        nine_hour_shift_num.append(nine_hour_shift)
        seven_hour_shift_num.append(seven_hour_shift)
    eight_hour_shift_score = average_score(eight_hour_shift_num, 20)
    nine_hour_shift_score = average_score(nine_hour_shift_num, 15)
    seven_hour_shift_score = average_score(seven_hour_shift_num, 10)

    # 任务长度
    below_two_hours_shift_num: List[int] = []
    for matrix in matrix_list:
        below_two_hours_shift: int = 0
        for line in matrix:
            last_bid: str = ''
            task_len: int = 0
            for bid in line:
                if not bid:
                    if last_bid:
                        last_bid = ''
                        if task_len > 0:
                            if task_len * block_length < 120:
                                below_two_hours_shift += 1
                        task_len = 0
                    else:
                        task_len = 0
                else:
                    if bid == last_bid:
                        task_len += 1
                    else:
                        last_bid = bid
                        if task_len > 0:
                            if task_len * block_length < 120:
                                below_two_hours_shift += 1
                        task_len = 1
            if task_len > 0:
                if task_len * block_length < 120:
                    below_two_hours_shift += 1
        below_two_hours_shift_num.append(-below_two_hours_shift)  # 小于2小时班次越少越好，用负数
    task_length_score = average_score(below_two_hours_shift_num, 20)

    # 任务个数
    task_num_below_four_num: List[int] = []
    for matrix in matrix_list:
        task_num_below_four: int = 0
        for line in matrix:
            new_line = list(set(line))
            if '' in new_line:
                new_line.remove('')
            if 'break' in new_line:
                new_line.remove('break')
            if len(new_line) < 4:
                task_num_below_four += 1
        task_num_below_four_num.append(task_num_below_four)
    task_num_socre = average_score(task_num_below_four_num, 20)

    # 休息集中度
    break_time_beyond_two_num: List[int] = []
    for planner in planner_list:
        break_count = planner.break_count
        break_time_beyond_two: int = 0
        for i in break_count:
            if i > 2:
                break_time_beyond_two += 1
        break_time_beyond_two_num.append(-break_time_beyond_two)  # 休息集中越多越差，用负数
    break_count_score = average_score(break_time_beyond_two_num, 20)

    # 开铺 打烊任务优先8小时
    open_shutdown_task_list = ManPowerForecastDB.get_open_shutdown_task_id_list(cid, did)
    open_shutdown_task_priority: List[int] = []
    for matrix in matrix_list:
        deviation = 0
        for line in matrix:
            task_list = list(set([bid for bid in line if (bid != '' and bid != 'break')]))
            flag = False
            for bid in task_list:
                if bid in open_shutdown_task_list:
                    flag = True
                    break
            if not flag:
                continue
            shift_length = len([bid for bid in line if (bid != '' and bid != 'break')])
            if shift_length == 16:
                continue
            else:
                deviation += abs(16 - shift_length)
        open_shutdown_task_priority.append(-deviation)  # 不等于8小时班次越多越差，用负数
    if str(cid) in ['50000735', '50000895', '60000039', '50000863']:
        # 极大增加这几个cid的开铺打烊权重
        open_shutdown_task_priority_score = average_score(open_shutdown_task_priority, 100)
    else:
        open_shutdown_task_priority_score = average_score(open_shutdown_task_priority, 20)

    for i in range(len(score_list)):
        score_list[i] = manpower_score[i] + eight_hour_shift_score[i] + nine_hour_shift_score[i] + \
                        seven_hour_shift_score[i] + task_length_score[i] + task_num_socre[i] + break_count_score[i] + \
                        open_shutdown_task_priority_score[i]

    infoLog.info('score list: ' + str(score_list))
    infoLog.info('max socre is: ' + str(max(score_list)))
    return planner_list[score_list.index(max(score_list))]


def average_score(score_list: List[Union[int, float]], average: float = 20) -> List[float]:
    """
    将输入变为平均分为设定值的分数列表输出
    :param score_list:
    :param average:
    :return:
    """
    total: float = average * len(score_list)
    score_total: float = sum(score_list)
    diff_total = total - score_total
    diff_ave = diff_total / len(score_list)
    result = copy.deepcopy(score_list)
    for i in range(len(result)):
        result[i] = result[i] + diff_ave
    return result


def is_line_meet_req(line_item: List[str], min_len: int, max_len: int, time_interval: int) -> bool:
    """
    line是否符合规定
    :param line_item:
    :param min_len:
    :param max_len:
    :param time_interval:
    :return:
    """
    shift_len = 0
    for task in line_item:
        if not task:
            if shift_len:
                break
            else:
                continue
        else:
            shift_len += 1
    if min_len <= shift_len * time_interval <= max_len:
        return True
    return False


def convert_matrix_to_tasks(matrix: List[List[str]], planner: Planner) -> \
        Tuple[List[FixedTask], List[DirectTask], List[InDirectTask]]:
    """
    矩阵转化为任务
    :param matrix:
    :param planner:
    :return:
    """
    fixed_tasks_list = planner.fixed_tasks_list
    direct_tasks_list = planner.direct_tasks_list
    indirect_tasks_list = planner.indirect_tasks_list
    block_length = planner.block_length

    fixed_tasks: List[FixedTask] = []
    direct_tasks: List[DirectTask] = []
    indirect_tasks: List[InDirectTask] = []

    for line in matrix:
        for block in range(len(line)):
            task = line[block]
            if task:
                if task != 'break':
                    if task in fixed_tasks_list:
                        start_time = planner.block_to_time(block)
                        end_time = planner.block_to_time(block + 1)
                        original_fixed_tasks = planner.fixed_tasks
                        fill_coef = 1
                        discard = False
                        task_min_work_time = block_length
                        task_max_work_time = 480
                        for ft in original_fixed_tasks:
                            if ft.bid == task:
                                fill_coef = ft.fill_coef
                                discard = ft.discard
                                task_min_work_time = ft.task_min_time
                                task_max_work_time = ft.task_max_time
                                break
                        ft = FixedTask(task, start_time, end_time, block_length, fill_coef, discard,
                                       task_min_work_time, task_max_work_time)
                        fixed_tasks.append(ft)
                    elif task in direct_tasks_list:
                        start_time = planner.block_to_time(block)
                        end_time = planner.block_to_time(block + 1)
                        original_direct_tasks = planner.direct_tasks
                        fill_coef = 1
                        discard = False
                        task_min_work_time = block_length
                        task_max_work_time = 480
                        for dt in original_direct_tasks:
                            if dt.bid == task:
                                fill_coef = dt.fill_coef
                                discard = dt.discard
                                task_min_work_time = dt.task_min_time
                                task_max_work_time = dt.task_max_time
                                break
                        dt = DirectTask(task, start_time, end_time, block_length, fill_coef, discard,
                                        task_min_work_time, task_max_work_time)
                        direct_tasks.append(dt)
                    elif task in indirect_tasks_list:
                        it = InDirectTask(task, block_length)
                        indirect_tasks.append(it)
                    else:
                        infoLog.warning('wrong task: ' + str(task))

    return fixed_tasks, direct_tasks, indirect_tasks


def reverse_task_list(task_list: List[Union[DirectTask, FixedTask]], start_time: str, end_time: str) -> \
        List[Union[DirectTask, FixedTask]]:
    """
    反向task list
    :param task_list:
    :param start_time:
    :param end_time:
    :return:
    """
    res_list = []

    for task in task_list:
        task_start_time = task.start_time
        task_end_time = task.end_time
        task_start_time_new, task_end_time_new = reverse_time_str(start_time, end_time, task_start_time, task_end_time)
        task_new = copy.deepcopy(task)
        task_new.start_time = task_start_time_new
        task_new.end_time = task_end_time_new
        res_list.append(task_new)

    return res_list


def reverse_time_str(start_time: str, end_time: str, task_start_time: str, task_end_time: str) -> Tuple[str, str]:
    """
    转换时间字符串
    :param start_time:
    :param end_time:
    :param task_start_time:
    :param task_end_time:
    :return:
    """
    start_time_dt = datetime.strptime(start_time, '%H:%M')
    end_time_dt = datetime.strptime(end_time, '%H:%M')
    task_start_time_dt = datetime.strptime(task_start_time, '%H:%M')
    task_end_time_dt = datetime.strptime(task_end_time, '%H:%M')
    if end_time_dt > task_start_time_dt:
        task_end_time_dt_new = start_time_dt + (end_time_dt - task_start_time_dt)
    else:
        task_end_time_dt_new = start_time_dt + (end_time_dt - task_start_time_dt + timedelta(days=1))
    if end_time_dt > task_end_time_dt:
        task_start_time_dt_new = start_time_dt + (end_time_dt - task_end_time_dt)
    else:
        task_start_time_dt_new = start_time_dt + (end_time_dt - task_end_time_dt + timedelta(days=1))
    return task_start_time_dt_new.strftime('%H:%M'), task_end_time_dt_new.strftime('%H:%M')


def print_task_matrix_detail(matrix: List[List[str]], task_name_dict: Dict[str, str]):
    """
    打印详情
    :param matrix:
    :param task_name_dict:
    :return:
    """
    for line in matrix:
        m = 0
        for t in line:
            if t != '':
                m += 1
        v = ','.join(list(map(lambda x: task_name_dict.get(x, '..' + x + '..'), line)))
        print(m, v)


def test():
    raw_data = {"token": "001581ac2096f86709fa30cae323f95f", "timestr": "2020-09-07 17:40:35.950228", "cid": 60000039,
                "didArr": [6508], "forecastType": "0", "forecastDateStart": "2020-09-14",
                "forecastDateEnd": "2020-09-20", "timeInterval": "30",
                "shift_mod_list": [{"shiftModbid": "", "didArr": [6508], "shiftModData": []}], "combirule": [
            {"combiruleBid": "", "didArr": [6508], "combiRuleData": [{
                                                                         "ruleData": "20200730164510032140439a80043074,20200730164439989140439a80042602,20200730164436406140439a80042549,20200730164459189140439a80042907,2020073016452320914043be50043295,2020073016443556514043be50042535,20200730164505136140439a80042995,20200730164444198140439a80042673,2020073016450597814043be50043016,20200730164443637140439a80042669,20200730164434494140439a80042510,2020073017133654514043be50056253,20200730164506825140439a80043022,2020073016451143514043be50043105,20200730164513530140439a80043135,20200730171336830140439a80056256,2020073016451266414043be50043124,2020073016443725114043be50042567,20200730164514083140439a80043149,2020073016443230514043be50042481,2020073016450768414043be50043044"}]}],
                "shiftsplitrule": [{"shiftsplitbid": "", "didArr": [6508], "shiftsplitData": [
                    {"ruleCalType": "worktime", "ruleCpType": "le", "ruleCpNum": "480", "dayFusion": 1},
                    {"ruleCalType": "shiftLen", "ruleCpType": "ge", "ruleCpNum": "210", "dayFusion": 1},
                    {"ruleCalType": "shiftLen", "ruleCpType": "le", "ruleCpNum": "480", "dayFusion": 1},
                    {"ruleCalType": "interval", "ruleCpType": "ge", "ruleCpNum": "0", "dayFusion": 1},
                    {"ruleCalType": "shiftNum", "ruleCpType": "le", "ruleCpNum": "1", "dayFusion": 1},
                    {"ruleCalType": "fillCoefficient", "ruleCpType": "eq", "ruleCpNum": "0.8", "dayFusion": 1},
                    {"ruleCalType": "taskCount", "ruleCpType": "le", "ruleCpNum": "4", "dayFusion": 1}]}]}

    cid: str = raw_data['cid']
    bid: str = raw_data['forecastType']
    did_arr: List[int] = raw_data['didArr']
    forecast_date_start: str = raw_data['forecastDateStart']
    forecast_date_end: str = raw_data['forecastDateEnd']
    shift_mod: List[Dict[str, Any]] = raw_data.get('shiftMod', [])
    combi_rule: List[Dict[str, Any]] = raw_data.get('combirule', [])
    shiftsplitrule = raw_data['shiftsplitrule']
    timeInterval = int(raw_data['timeInterval'])
    save_method: int = 1

    now = datetime.now()
    save_result = ManPowerForecastService.manpower_forecast(cid, bid, timeInterval, did_arr, forecast_date_start,
                                                            forecast_date_end, shift_mod, combi_rule, shiftsplitrule,
                                                            save_method, True)
    print('forecast used time is ' + str((datetime.now() - now).seconds) + ' seconds.')
    print(save_result)


if __name__ == '__main__':
    test()
