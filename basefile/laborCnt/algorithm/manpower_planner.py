#!/usr/bin/env python
# encoding: utf-8

"""
@author: sunsong
@contact: sunsong@didiglobal.com
@file: manpower_planner.py
@time: 2020/04/01 2:09 下午
@desc:
"""

from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import random
import copy

from utils.myLogger import infoLog
from utils.task import FixedTask, DirectTask, InDirectTask, FDTask


class Tasks(object):
    """
    班次任务类
    """

    def __init__(self, start_time: str, end_time: str, block_length: int, is_cross_day: bool):
        """
        初始化类
        :param start_time: 班次开始时间 HH:MM
        :param end_time: 班次结束时间 HH:MM
        :param block_length: 粒度 一般为15分钟或30分钟
        :param is_cross_day: 是否跨天
        """
        self.start_time = time_string_formatter(start_time)
        self.end_time = time_string_formatter(end_time)
        self.block_length = block_length
        self.is_cross_day = is_cross_day

        self.length = 0
        self.task_info: List[str] = []
        self.status = False

        self.init_task()

    def __str__(self):
        """
        自定义输出
        :return:
        """
        return str(self.task_info)

    def __repr__(self):
        """
        自定义输出
        :return:
        """
        return str(self.task_info)

    def init_task(self):
        """
        初始化task info list
        :return:
        """
        time_interval = calculate_minute_interval(self.start_time, self.end_time, self.is_cross_day)
        if time_interval % self.block_length == 0:
            self.length = time_interval // self.block_length
        else:
            self.length = time_interval // self.block_length + 1

        self.task_info = ['' for _ in range(self.length)]

    def is_available(self, start_time: str, end_time: str, bid: str, combine_rule_dict: Dict[str, List[str]]) -> bool:
        """
        判断放入的任务是否可放
        :param bid:
        :param combine_rule_dict:
        :param start_time:
        :param end_time:
        :return:
        """
        start_time = time_string_formatter(start_time)
        end_time = time_string_formatter(end_time)
        start_block = calculate_minute_interval(self.start_time, start_time, self.is_cross_day) // self.block_length
        end_block = calculate_minute_interval(self.start_time, end_time, self.is_cross_day) // self.block_length
        if start_block < 0 or end_block < 0 or start_block >= end_block:
            # 不合法的任务
            return False
        if bid not in combine_rule_dict:
            # bid无法与其他任务组合
            return False
        combine_bid_list = combine_rule_dict[bid]
        for exist_bid in self.task_info:
            if exist_bid == bid:
                # 已存在相同bid，无需判断组合规则，跳过
                break
            if exist_bid == '':
                continue
            if exist_bid not in combine_bid_list:
                return False
        for i in range(start_block, end_block):
            if self.task_info[i]:
                return False
        return True

    def put_task(self, bid: str, start_time: str, end_time: str) -> bool:
        """
        放入任务
        :param bid:
        :param start_time:
        :param end_time:
        :return:
        """
        start_time = time_string_formatter(start_time)
        end_time = time_string_formatter(end_time)
        start_block = calculate_minute_interval(self.start_time, start_time, self.is_cross_day) // self.block_length
        end_block = calculate_minute_interval(self.start_time, end_time, self.is_cross_day) // self.block_length
        if start_block < 0 or end_block < 0 or start_block >= end_block:
            # 不合法的任务
            return False
        for i in range(start_block, end_block):
            self.task_info[i] = bid
        return True

    def need_blocks(self) -> int:
        """
        还需要多少 块 任务 才能填满
        :return:
        """
        block_num = 0
        for bid in self.task_info:
            if not bid:
                block_num += 1
        return block_num

    def need_work_time(self) -> int:
        """
        还需要多少工时 才能填满
        :return:
        """
        return self.need_blocks() * self.block_length

    def is_full(self) -> bool:
        """
        是否已满
        :return:
        """
        if not self.status:
            if self.need_blocks():
                self.status = False
            else:
                self.status = True
        return self.status

    def put_indirect_task(self, bid: str, worktime: int):
        """
        放入间接任务
        :param bid:
        :param worktime:
        :return:
        """
        if self.need_work_time() == worktime:
            for i in range(self.length):
                if not self.task_info[i]:
                    self.task_info[i] = bid
            self.status = True
        else:
            for i in range(self.length):
                if not self.task_info[i]:
                    self.task_info[i] = bid
                    worktime -= self.block_length
                    if worktime <= 0:
                        break

    def export_task(self, discard_dict: Dict[str, bool], min_time_dict: Dict[str, int], max_time_dict: Dict[str, int],
                    fill_coef_dict: Dict[str, float], fixed_tasks_list: List[str], direct_tasks_list: List[str],
                    block_length: int) \
            -> List[FDTask]:
        """
        导出自己不完整的task
        :param direct_tasks_list:
        :param fixed_tasks_list:
        :param discard_dict:
        :param min_time_dict:
        :param max_time_dict:
        :param fill_coef_dict:
        :param block_length:
        :return:
        """
        out_task_list: List[FDTask] = []

        start_block = 0
        now_bid = ''
        for i in range(self.length):
            bid = self.task_info[i]
            if not now_bid and not bid:
                # 空
                continue
            if bid == now_bid and i < self.length - 1:
                # 连续
                continue
            if not now_bid and bid and i < self.length - 1:
                # 前面是空的，现在有了
                start_block = i
                now_bid = bid
                continue
            if now_bid and now_bid != bid:
                # 前面是有的，现在变成其他
                end_block = i
                s_time = self.block_to_time(start_block)
                e_time = self.block_to_time(end_block)
                work_time = (end_block - start_block) * self.block_length
                task_length = end_block - start_block
                fill_coef = fill_coef_dict.get(now_bid, 0.5)
                discard = discard_dict.get(now_bid, True)
                task_min_time = min_time_dict.get(now_bid, 0)
                task_max_time = max_time_dict.get(now_bid, 24 * 60)

                if now_bid in fixed_tasks_list:
                    task = FixedTask(now_bid, s_time, e_time, work_time, fill_coef, discard, task_min_time,
                                     task_max_time)
                else:
                    task = DirectTask(now_bid, s_time, e_time, work_time, fill_coef, discard, task_min_time,
                                      task_max_time)
                task.calculate_task_block_length(block_length)
                out_task_list.append(task)
                if not bid:
                    # 如果后面为空
                    now_bid = ''
                else:
                    # 如果后面不为空
                    now_bid = bid
                    start_block = i
                continue
            if bid and now_bid and i == self.length - 1:
                # 最后一个元素, 前面不为空
                end_block = self.length
                s_time = self.block_to_time(start_block)
                e_time = self.block_to_time(end_block)
                work_time = (end_block - start_block) * self.block_length
                # task_length = end_block - start_block
                fill_coef = fill_coef_dict.get(now_bid, 0.5)
                discard = discard_dict.get(now_bid, True)
                task_min_time = min_time_dict.get(now_bid, 0)
                task_max_time = max_time_dict.get(now_bid, 24 * 60)
                if now_bid in fixed_tasks_list:
                    task = FixedTask(now_bid, s_time, e_time, work_time, fill_coef, discard, task_min_time,
                                     task_max_time)
                else:
                    task = DirectTask(now_bid, s_time, e_time, work_time, fill_coef, discard, task_min_time,
                                      task_max_time)
                task.calculate_task_block_length(block_length)
                out_task_list.append(task)
            if bid and not now_bid and i == self.length - 1:
                # 最后一个元素, 前面为空
                end_block = self.length
                start_block = self.length - 1
                s_time = self.block_to_time(start_block)
                e_time = self.block_to_time(end_block)
                work_time = self.block_length
                # task_length = 1
                fill_coef = fill_coef_dict.get(now_bid, 0.5)
                discard = discard_dict.get(now_bid, True)
                task_min_time = min_time_dict.get(now_bid, 0)
                task_max_time = max_time_dict.get(now_bid, 24 * 60)
                if now_bid in fixed_tasks_list:
                    task = FixedTask(now_bid, s_time, e_time, work_time, fill_coef, discard, task_min_time,
                                     task_max_time)
                else:
                    task = DirectTask(now_bid, s_time, e_time, work_time, fill_coef, discard, task_min_time,
                                      task_max_time)
                task.calculate_task_block_length(block_length)
                out_task_list.append(task)
        return out_task_list

    def block_to_time(self, block: int) -> str:
        """
        块编号到时间字符串
        :param block:
        :return:
        """
        start_dt = datetime.strptime(self.start_time, '%H:%M')
        delta = timedelta(minutes=block * self.block_length)
        if not self.is_cross_day or (start_dt + delta).day < 2:
            return (start_dt + delta).strftime('%H:%M')
        else:
            return (start_dt + delta - timedelta(days=1)).strftime('%H:%M')


class Planner(object):
    """
    班次生成
    """

    def __init__(self, start_time: str, end_time: str, block_length: int,
                 fixed_tasks: List[FixedTask], direct_tasks: List[DirectTask],
                 indirect_tasks: List[InDirectTask], combine_rules: List[str], is_cross_day: bool,
                 interval_rules: List[Tuple[str, int, bool]], working_hour_rules: List[Tuple[str, int, bool]],
                 shift_num_rules: List[Tuple[str, int, bool]], shift_length_rules: List[Tuple[str, int, bool]],
                 fill_coef_rules: List[Tuple[str, float, bool]], task_count_rules: List[Tuple[str, int, bool]],
                 shift_template: List[Tuple[str, str, bool]], need_place_indirect_task: bool = False,
                 use_virtual_indirect_task: bool = False, do_init: bool = True, debug: bool = False, **kw):
        """
        初始化函数
        :param start_time: 整体开始时间 HH:MM str
        :param end_time: 整体结束时间 HH:MM str
        :param block_length: 每个时间块的长度 分钟 int
        :param fixed_tasks: 固定任务 List[FixedTask] work_time单位为分钟
        :param direct_tasks: 直接任务 List[DirectTask] work_time单位为分钟
        :param indirect_tasks: 间接任务 List[InDirectTask] work_time单位为分钟
        :param combine_rules: 组合规则 List[rules] rules为逗号分隔的bids 代表可以组合在一起的任务bid
        :param is_cross_day: 是否跨天 True 跨天 False 不跨天
        :param interval_rules: 间隔规则 List[Tuple[比较规则, 数值（分钟）, 是否跨天]]
        :param working_hour_rules: 工时规则 List[Tuple[比较规则, 数值（分钟）, 是否跨天]]
        :param shift_num_rules: 班段个数规则 List[Tuple[比较规则, 数值（个数）, 是否跨天]]
        :param shift_length_rules: 班段长度规则 List[Tuple[比较规则, 数值（个数）, 是否跨天]]
        :param fill_coef_rules: 班次填补系数规则 List[Tuple[比较规则, 数值, 是否跨天]]
        :param task_count_rules: 每日任务个数规则 List[Tuple[比较规则, 数值（个数）, 是否跨天]]
        :param shift_template: 班次模板 List[Tuple[开始时间, 结束时间, 是否跨天]]
        :param need_place_indirect_task: 是否在模板中放入间接工时任务 bool 默认False
        :param use_virtual_indirect_task: 是否在间接任务不够的时候默认填充虚拟间接任务 bool 默认False
        :param with_break: 是否包含休息
        :param do_init: 执行init操作，默认为True
        """
        super(Planner, self).__init__()

        self.BREAK_TASK_NAME: str = 'break'

        self.start_time = start_time
        self.end_time = end_time
        self.block_length = block_length

        self.fixed_tasks = fixed_tasks
        self.direct_tasks = direct_tasks
        self.indirect_tasks = indirect_tasks

        self.combine_rules = combine_rules
        self.is_cross_day = is_cross_day
        self.interval_rules = interval_rules
        self.working_hour_rules = working_hour_rules
        self.shift_num_rules = shift_num_rules
        self.shift_length_rules = shift_length_rules
        self.fill_coef_rules = fill_coef_rules
        self.task_count_rules = task_count_rules

        self.shift_template = shift_template
        self.need_place_indirect_task = need_place_indirect_task
        self.template_dict = {}

        self.use_virtual_indirect_task = use_virtual_indirect_task
        self.fixed_tasks_list = [task.bid for task in fixed_tasks]
        self.direct_tasks_list = [task.bid for task in direct_tasks]
        self.indirect_tasks_list = [task.bid for task in indirect_tasks]

        self.time_block_length = int((datetime.strptime(end_time, '%H:%M') -
                                      datetime.strptime(start_time, '%H:%M')).seconds / 60 / block_length)

        self.temp_fill_block: List[Tuple[int, str]] = []
        self.debug = debug

        self.with_break: bool = kw.get('with_break', False)
        self.break_time: int = kw.get('break_time', 30)
        self.max_break_count: int = kw.get('max_break_count', 2)
        self.prev_no_break_time: int = kw.get('prev_no_break_time', 120)
        self.rear_no_break_time: int = kw.get('rear_no_break_time', 120)
        self.no_break_shift_time: int = kw.get('no_break_shift_time', 360)
        self.priority_task_list: List[str] = kw.get('priority_task_list', [])
        self.only_generate_priority_tasks: bool = kw.get('only_generate_priority_tasks', False)
        self.open_close_max_time: int = kw.get('open_close_max_time', 150)
        self.open_close_max_length: int = self.open_close_max_time // self.block_length

        self.break_length: int = self.break_time // self.block_length
        self.prev_no_break_length: int = self.prev_no_break_time // self.block_length
        self.rear_no_break_length: int = self.rear_no_break_time // self.block_length
        self.break_count = kw.get('break_count', [0 for _ in range(self.time_block_length)])

        self.fd_task_dict_temp = {}
        self.line_item_temp = []
        self.indirect_tasks_temp = {}

        if do_init:
            self.task_preprocess()

            self.fd_tasks: List[FDTask] = self.fixed_tasks + self.direct_tasks
            self.fd_tasks_sort()

            self.fd_task_discard_dict: Dict[str, bool] = {}
            self.fd_task_min_time_dict: Dict[str, int] = {}
            self.fd_task_max_time_dict: Dict[str, int] = {}
            self.fd_task_fill_coef_dict: Dict[str, float] = {}
            self.gen_fd_task_dict()

            self.indirect_task_convert()

            self.max_shift_length_rule = None
            self.min_shift_length_rule = None
            self.max_shift_num_rule = None
            self.min_shift_num_rule = None  # 暂未用到
            self.max_interval_rule = None
            self.min_interval_rule = None
            self.max_working_hour_rule = None
            self.min_working_hour_rule = None  # 暂未用到
            self.fill_coef: float = 0.5
            self.max_task_count = None
            self.min_task_count = None
            self.rules_convert()

            self.matrix_flag = True
            self.fail_reason = ''

            self.matrix = [['' for _ in range(self.time_block_length)]]
            self.matrix_status = [0]
            self.combine_rules_dict: Dict[str, List[str]] = {}
            self.template_matrix = [['' for _ in range(self.time_block_length)]]

            if debug:
                self.debug_matrix = [['' for _ in range(self.time_block_length)]]
                self.debug_template_matrix = [['' for _ in range(self.time_block_length)]]

            self.generate_combine_rules_dict()

            if self.shift_template:
                self.generate_shift_template_dict()
                self.template_dict_to_matrix()

            self.generate_matrix()
            self.modify_matrix()

    def task_preprocess(self):
        """
        任务预处理
        :return:
        """
        for task in self.direct_tasks:
            task.calculate_task_block_length(self.block_length)
        for task in self.fixed_tasks:
            task.calculate_task_block_length(self.block_length)
        for task in self.indirect_tasks:
            task.calculate_task_block_length(self.block_length)

    def gen_fd_task_dict(self):
        """
        生成辅助dict
        :return:
        """
        for task in self.fd_tasks:
            bid = task.bid
            discard = task.discard
            min_time = task.task_min_time
            max_time = task.task_max_time
            fill_coef = task.fill_coef
            # task_type = task.task_type

            self.fd_task_discard_dict[bid] = discard
            self.fd_task_min_time_dict[bid] = min_time
            self.fd_task_max_time_dict[bid] = max_time
            self.fd_task_fill_coef_dict[bid] = fill_coef

    def rules_convert(self):
        """
        规则转换
        :return:
        """
        # 班次长度 shift length rule
        for item in self.shift_length_rules:
            if item[0] == 'lt' or item[0] == 'le':
                self.max_shift_length_rule = (item[0], item[1])
            elif item[0] == 'gt' or item[0] == 'ge':
                self.min_shift_length_rule = (item[0], item[1])

        if not self.min_shift_length_rule:
            # 如果没有最小时长限制，就将其限制为最小格子长度
            self.min_shift_length_rule = ('ge', self.block_length)

        # 班次间隔 interval rule
        for item in self.interval_rules:
            if item[0] == 'lt' or item[0] == 'le':
                self.max_interval_rule = (item[0], item[1])
            elif item[0] == 'gt' or item[0] == 'ge':
                self.min_interval_rule = (item[0], item[1])

        # 班次个数 shift num rule
        for item in self.shift_num_rules:
            if item[0] == 'lt' or item[0] == 'le':
                self.max_shift_num_rule = (item[0], item[1])
            elif item[0] == 'gt' or item[0] == 'ge':
                self.min_shift_num_rule = (item[0], item[1])

        # 工作时长 working hour rule
        for item in self.working_hour_rules:
            if item[0] == 'lt' or item[0] == 'le':
                self.max_working_hour_rule = (item[0], item[1])
            elif item[0] == 'gt' or item[0] == 'ge':
                self.min_working_hour_rule = (item[0], item[1])

        # 填补系数 fill coeffcient rule
        for item in self.fill_coef_rules:
            # 只能是等于
            self.fill_coef = 1 - float(item[1])

        # 每日任务个数 task count rule
        for item in self.task_count_rules:
            if item[0] == 'lt' or item[0] == 'le':
                self.max_task_count = (item[0], item[1])
            elif item[0] == 'gt' or item[0] == 'ge':
                self.min_task_count = (item[0], item[1])

    def max_task_work_time_check(self, bid: str, line_item: List[str], task_length: int = 1) -> bool:
        """
        任务最大长度检测
        :param bid:
        :param line_item:
        :param task_length:
        :return:
        """
        max_task_work_time = self.fd_task_max_time_dict.get(bid, -1)
        if max_task_work_time <= 0:
            return True
        exist_task_num = task_length
        for i in range(self.time_block_length - 1, -1, -1):
            if line_item[i] == bid:
                exist_task_num += 1
        exist_task_work_time = exist_task_num * self.block_length
        if max_task_work_time < exist_task_work_time:
            return False
        return True

    def max_task_count_rule_check(self, bid: str, line_item: List[str], start_block: int, full: bool) -> bool:
        """
        最大任务个数检查
        :param full:
        :param bid:
        :param line_item:
        :param start_block:
        :return:
        """
        if not self.max_task_count:
            return True

        compare_rule = self.max_task_count[0]
        rule_number = self.max_task_count[1]

        exist_task_num = 0
        last_task_bid = ''
        if not full:
            for i in range(start_block):
                task_bid = line_item[i]
                if task_bid != last_task_bid:
                    # 休息任务不算任务，跳过
                    if task_bid == self.BREAK_TASK_NAME:
                        continue
                    if task_bid:
                        exist_task_num += 1
                    last_task_bid = task_bid
            if bid != last_task_bid:
                exist_task_num += 1
        else:
            new_line_item = line_item[:start_block] + [bid] + line_item[start_block + 1:]
            for task_bid in new_line_item:
                if task_bid != last_task_bid:
                    # 休息任务不算任务，跳过
                    if task_bid == self.BREAK_TASK_NAME:
                        continue
                    if task_bid:
                        exist_task_num += 1
                    last_task_bid = task_bid

        if compare_rule == 'lt':
            if exist_task_num >= rule_number:
                return False
        else:
            if exist_task_num > rule_number:
                return False

        return True

    def min_task_count_rule_check(self, bid: str, line_item: List[str], start_block: int, full: bool) -> bool:
        """
        最小任务个数检查
        :param full:
        :param bid:
        :param line_item:
        :param start_block:
        :return:
        """
        if not self.min_task_count:
            return True

        compare_rule = self.max_task_count[0]
        rule_number = self.max_task_count[1]

        exist_task_num = 0
        last_task_bid = ''
        if not full:
            for i in range(start_block):
                task_bid = line_item[i]
                if task_bid != last_task_bid:
                    # 休息任务不算任务，跳过
                    if task_bid == self.BREAK_TASK_NAME:
                        continue
                    if task_bid:
                        exist_task_num += 1
                    last_task_bid = task_bid
            if bid != last_task_bid:
                exist_task_num += 1
        else:
            new_line_item = line_item[:start_block] + [bid] + line_item[start_block + 1:]
            for task_bid in new_line_item:
                if task_bid != last_task_bid:
                    # 休息任务不算任务，跳过
                    if task_bid == self.BREAK_TASK_NAME:
                        continue
                    if task_bid:
                        exist_task_num += 1
                    last_task_bid = task_bid

        if compare_rule == 'gt':
            if exist_task_num <= rule_number:
                return False
        else:
            if exist_task_num < rule_number:
                return False

        return True

    def max_shift_length_rule_check(self, bid: str, line_item: List[str], time_block_length: int, start_block: int) \
            -> bool:
        """
        班次最大长度检查
        :param time_block_length:
        :param bid:
        :param line_item:
        :param start_block:
        :return:
        """
        if not self.max_shift_length_rule:
            return True

        compare_rule = self.max_shift_length_rule[0]
        rule_number = self.max_shift_length_rule[1]

        line_temp: List[str] = [i for i in line_item]
        line_temp[start_block] = bid

        block_len: int = 0
        for i in range(start_block, -1, -1):
            task = line_temp[i]
            if task:
                block_len += 1
            else:
                break

        if block_len == 1:
            # 这行没有其他班次，直接通过
            return True

        worktime = (block_len + time_block_length - 1) * self.block_length

        if compare_rule == 'lt':
            if worktime >= rule_number:
                return False
        else:
            if worktime > rule_number:
                return False

        return True

    def max_shift_length_rule_check_for_indirectwh(self, bid: str, line_item: List[str], start_block: int) -> bool:
        """
        班次最大长度检查 对于非直接任务 也需要向后检查，防止超出最大任务允许长度
        :param bid:
        :param line_item:
        :param start_block:
        :return:
        """
        if not self.max_shift_length_rule:
            return True

        compare_rule = self.max_shift_length_rule[0]
        rule_number = self.max_shift_length_rule[1]

        line_temp: List[str] = [i for i in line_item]
        line_temp[start_block] = bid

        block_len: int = 0
        for i in range(start_block, -1, -1):
            task = line_temp[i]
            if task:
                block_len += 1
            else:
                break

        # 向后检查
        if start_block < len(line_temp) - 1:
            for i in range(start_block + 1, len(line_temp)):
                task = line_temp[i]
                if task:
                    block_len += 1
                else:
                    break

        worktime = block_len * self.block_length

        if compare_rule == 'lt':
            if worktime >= rule_number:
                return False
        else:
            if worktime > rule_number:
                return False

        return True

    def min_shift_length_rule_check_for_indirectwh(self, bid: str, line_item: List[str], start_block: int) -> bool:
        """
        班次最小长度检查
        :param bid:
        :param line_item:
        :param start_block:
        :return:
        """
        if not self.min_shift_length_rule:
            return True

        compare_rule = self.min_shift_length_rule[0]
        rule_number = self.min_shift_length_rule[1]

        line_temp: List[str] = [i for i in line_item]
        line_temp[start_block] = bid

        block_len: int = 0
        for i in range(start_block, -1, -1):
            task = line_temp[i]
            if task:
                block_len += 1
            else:
                break

        # 向后检查
        if start_block < len(line_temp) - 1:
            for i in range(start_block + 1, len(line_temp)):
                task = line_temp[i]
                if task:
                    block_len += 1
                else:
                    break

        worktime = block_len * self.block_length

        if compare_rule == 'gt':
            if worktime <= rule_number:
                return False
        else:
            if worktime < rule_number:
                return False

        return True

    def max_shift_num_rule_check(self, bid: str, line_item: List[str], start_block: int) -> bool:
        """
        班段最大个数检查
        :param start_block:
        :param bid:
        :param line_item:
        :return:
        """
        if not self.max_shift_num_rule:
            return True

        compare_rule = self.max_shift_num_rule[0]
        rule_number = self.max_shift_num_rule[1]

        line_temp: List[str] = [i for i in line_item]
        line_temp[start_block] = bid

        exist_shift = 0
        now_task = ''
        for task in line_temp:
            if task != now_task:
                if now_task:
                    # 如果之前的一段是有任务的
                    if not task:
                        # 一段班次结束
                        now_task = ''
                    else:
                        # 只是换了个任务，没有结束班次
                        now_task = task
                        continue
                else:
                    # 如果之前一段是没有任务的
                    exist_shift += 1
                    now_task = task
            else:
                # 如果任务没变，不做任何事
                continue

        if compare_rule == 'lt':
            if exist_shift >= rule_number:
                return False
        else:
            if exist_shift > rule_number:
                return False

        return True

    def combine_rule_check(self, bid: str, line_item: List[str], start_block: int) -> bool:
        """
        检查组合规则 从开头到start_block 不包含start_block
        :param start_block:
        :param line_item:
        :param bid:
        :return:
        """
        exist_bids: List[str] = [ebid for ebid in list(set(line_item[:start_block])) if ebid and ebid not in
                                 self.indirect_tasks_list]

        if not exist_bids:
            return True

        # 休息任务不需要检查组合规则
        while self.BREAK_TASK_NAME in exist_bids:
            exist_bids.remove(self.BREAK_TASK_NAME)

        if bid in exist_bids:
            return True

        if bid not in self.combine_rules_dict:
            return False

        combine_bids = self.combine_rules_dict[bid]
        for ebid in exist_bids:
            if ebid not in combine_bids:
                return False
        return True

    def combine_rule_check_all(self, bid: str, line_item: List[str]) -> bool:
        """
        检查组合规则 全
        :param line_item:
        :param bid:
        :return:
        """
        exist_bids: List[str] = [ebid for ebid in list(set(line_item)) if ebid and ebid not in self.indirect_tasks_list]

        if not exist_bids:
            return True

        # 休息任务不需要检查组合规则
        while self.BREAK_TASK_NAME in exist_bids:
            exist_bids.remove(self.BREAK_TASK_NAME)

        if bid in exist_bids:
            return True

        if bid not in self.combine_rules_dict:
            return False

        combine_bids = self.combine_rules_dict[bid]
        for ebid in exist_bids:
            if ebid not in combine_bids:
                return False

        return True

    def max_work_time_check(self, line_item: List[str], time_block_length: int) -> bool:
        """
        最大工作时间检测
        :param line_item:
        :param time_block_length:
        :return:
        """
        if not self.max_working_hour_rule:
            return True

        compare_rule = self.max_working_hour_rule[0]
        rule_minutes = self.max_working_hour_rule[1]

        work_time_minute: int = len([i for i in line_item if i]) * self.block_length

        if work_time_minute == 0:
            return True

        work_time_minute += time_block_length * self.block_length

        if compare_rule == 'le':
            if work_time_minute > rule_minutes:
                return False
        else:
            if work_time_minute >= rule_minutes:
                return False

        return True

    def max_interval_check(self, line_item: List[str], start_block: int) -> bool:
        """
        是否已经超出最大间隔 已超出: False 未超出: True
        :param line_item:
        :param start_block:
        :return:
        """
        if not self.max_interval_rule:
            return True

        compare_rule = self.max_interval_rule[0]
        rule_minutes = self.max_interval_rule[1]

        interval_block: int = 0
        for i in range(start_block - 1, -1, -1):
            if not line_item[i]:
                interval_block += 1
            else:
                break

        if not interval_block:
            return True

        if interval_block == start_block:
            # 如果前面都是空的
            return True

        interval_minutes = interval_block * self.block_length

        if compare_rule == 'lt':
            if interval_minutes >= rule_minutes:
                return False
        else:
            if interval_minutes > rule_minutes:
                return False

        return True

    def min_interval_check(self, line_item: List[str], start_block: int) -> bool:
        """
        是否小于最小间隔 小于: False 未小于: True
        :param line_item:
        :param start_block:
        :return:
        """
        interval_block: int = 0
        for i in range(start_block - 1, -1, -1):
            if not line_item[i]:
                interval_block += 1
            else:
                break

        if not interval_block:
            return True

        if interval_block == start_block:
            # 如果前面都是空的
            return True

        interval_minutes = interval_block * self.block_length

        if not self.min_interval_rule:
            # 默认最少间隔60分钟
            compare_rule = 'ge'
            rule_minutes = 60
        else:
            compare_rule = self.min_interval_rule[0]
            rule_minutes = self.min_interval_rule[1]

        if compare_rule == 'gt':
            if interval_minutes <= rule_minutes:
                return False
        else:
            if interval_minutes < rule_minutes:
                return False

        return True

    def min_interval_check_for_indirect(self, line_item: List[str], start_block: int) -> bool:
        """
        是否小于最小间隔 for indirectwh 再进行一次后面的检查 小于: False 未小于: True
        :param line_item:
        :param start_block:
        :return:
        """
        interval_block: int = 0
        for i in range(start_block + 1, len(line_item)):
            if not line_item[i]:
                interval_block += 1
            else:
                break

        if not interval_block:
            return True

        if interval_block == len(line_item) - start_block:
            # 如果后面都是空的
            return True

        interval_minutes = interval_block * self.block_length

        if not self.min_interval_rule:
            # 默认最少间隔60分钟
            compare_rule = 'ge'
            rule_minutes = 60
        else:
            compare_rule = self.min_interval_rule[0]
            rule_minutes = self.min_interval_rule[1]

        if compare_rule == 'gt':
            if interval_minutes <= rule_minutes:
                return False
        else:
            if interval_minutes < rule_minutes:
                return False

        return True

    def template_sort(self):
        """
        对班次模板进行排序，开始时间早的排在前面
        :return:
        """
        if not self.is_cross_day:
            # 无跨天
            self.shift_template: List[Tuple[str, str, bool]] = sorted(self.shift_template,
                                                                      key=lambda x: (time_string_formatter(x[0]),
                                                                                     time_string_formatter(x[1])))
        else:
            # 有跨天
            shift_template_temp: List[Tuple[datetime, datetime, bool]] = []
            start_dt = datetime.strptime(self.start_time, '%H:%M')
            for template in self.shift_template:
                stime = datetime.strptime(time_string_formatter(template[0]), '%H:%M')
                etime = datetime.strptime(time_string_formatter(template[1]), '%H:%M')
                if stime < start_dt:
                    stime = stime + timedelta(days=1)
                if etime < start_dt:
                    etime = etime + timedelta(days=1)
                is_cross_day = template[2]
                shift_template_temp.append((stime, etime, is_cross_day))

            shift_template_temp = sorted(shift_template_temp, key=lambda x: (x[0], x[1]))

            shift_template: List[Tuple[str, str, bool]] = []
            for template in shift_template_temp:
                stime = template[0]
                etime = template[1]
                is_cross_day = template[2]
                if stime.day > 1:
                    stime = stime - timedelta(days=1)
                if etime.day > 1:
                    etime = etime - timedelta(days=1)
                s_str = stime.strftime('%H:%M')
                e_str = etime.strftime('%H:%M')
                shift_template.append((s_str, e_str, is_cross_day))

            self.shift_template = shift_template

    def generate_shift_template_dict(self):
        """
        考虑班次模板
        :return:
        """
        # 存放结果 key: 模板 value: 班次列表
        template_dict: Dict[Tuple[str, str, bool], List[Tasks]] = {}

        # 对班次模板进行预先排序，时间开始早的排在前面
        self.template_sort()

        start_time_dt = datetime.strptime(self.start_time, '%H:%M')

        for template in self.shift_template:
            # 对于每个班次模板
            template_start_time = time_string_formatter(template[0])
            template_end_time = time_string_formatter(template[1])
            is_cross_day = template[2]  # 是否跨天

            template_start_time_dt = datetime.strptime(template_start_time, '%H:%M')
            template_end_time_dt = datetime.strptime(template_end_time, '%H:%M')

            if is_cross_day:
                if template_start_time_dt < start_time_dt:
                    template_start_time_dt = template_start_time_dt + timedelta(days=1)
                if template_end_time_dt < start_time_dt:
                    template_end_time_dt = template_end_time_dt + timedelta(days=1)

            task_temp: List[FDTask] = []  # 暂存班次

            for task in self.fd_tasks:
                bid = task.bid
                task_start_time = time_string_formatter(task.start_time)
                task_end_time = time_string_formatter(task.end_time)
                work_time = int(task.work_time)

                task_start_time_dt = datetime.strptime(task_start_time, '%H:%M')
                task_end_time_dt = datetime.strptime(task_end_time, '%H:%M')

                if is_cross_day:
                    if task_start_time_dt < start_time_dt:
                        task_start_time_dt = task_start_time_dt + timedelta(days=1)
                    if task_end_time_dt < start_time_dt:
                        task_end_time_dt = task_end_time_dt + timedelta(days=1)

                # 人力数
                people_num: int = calculate_people_num(task_start_time, task_end_time, work_time)

                if task_start_time_dt <= template_start_time_dt < template_end_time_dt <= task_end_time_dt:
                    # 任务包含整个模板时间

                    # 切分任务
                    if task_start_time_dt < template_start_time_dt:
                        # 处理前部超出部分
                        new_time_block_length = self.time_to_block(task_start_time, template_start_time)
                        new_work_time = new_time_block_length * people_num * self.block_length
                        new_task = copy.deepcopy(task)
                        new_task.start_time = task_start_time
                        new_task.end_time = template_start_time
                        new_task.work_time = new_work_time
                        new_task.task_block_length = new_time_block_length
                        task_temp.append(new_task)
                    if task_end_time_dt > template_end_time_dt:
                        # 处理后部超出部分
                        new_time_block_length = self.time_to_block(template_end_time, task_end_time)
                        new_work_time = new_time_block_length * people_num * self.block_length
                        new_task = copy.deepcopy(task)
                        new_task.start_time = template_end_time
                        new_task.end_time = task_end_time
                        new_task.work_time = new_work_time
                        new_task.task_block_length = new_time_block_length
                        task_temp.append(new_task)

                    # 任务放入模板
                    task_list: List[Tasks] = template_dict.get(template, [])
                    for i in range(people_num):
                        t = Tasks(template_start_time, template_end_time, self.block_length, is_cross_day)
                        t.put_task(bid, template_start_time, template_end_time)
                        task_list.append(t)
                    template_dict[template] = task_list

                elif task_start_time_dt <= template_start_time_dt < task_end_time_dt < template_end_time_dt:
                    # 任务后部与模板重叠

                    # 切分任务
                    if task_start_time_dt < template_start_time_dt:
                        # 处理前部超出部分
                        new_time_block_length = self.time_to_block(task_start_time, template_start_time)
                        new_work_time = new_time_block_length * people_num * self.block_length
                        split_task = copy.deepcopy(task)
                        split_task.start_time = task_start_time
                        split_task.end_time = template_start_time
                        split_task.work_time = new_work_time
                        split_task.task_block_length = new_time_block_length
                        task_temp.append(split_task)

                    # 任务放入模板
                    task_list: List[Tasks] = template_dict.get(template, [])
                    new_task_flag = False
                    while people_num > 0:
                        if not new_task_flag:
                            put_task_flag = False
                            for i in range(len(task_list)):
                                t_task = task_list[i]
                                if not t_task.is_available(template_start_time, task_end_time, bid,
                                                           self.combine_rules_dict):
                                    continue
                                t_task.put_task(bid, template_start_time, task_end_time)
                                task_list[i] = t_task
                                people_num -= 1
                                put_task_flag = True
                                break
                            if not put_task_flag:
                                new_task_flag = True
                        else:
                            new_task = Tasks(template_start_time, template_end_time, self.block_length, is_cross_day)
                            new_task.put_task(bid, template_start_time, task_end_time)
                            task_list.append(new_task)
                            people_num -= 1
                    template_dict[template] = task_list
                elif template_start_time_dt < task_start_time_dt < template_end_time_dt <= task_end_time_dt:
                    # 任务前部与模板重叠

                    # 切分任务
                    if template_end_time_dt < task_end_time_dt:
                        new_time_block_length = self.time_to_block(template_end_time, task_end_time)
                        new_work_time = new_time_block_length * self.block_length * people_num
                        new_task = copy.deepcopy(task)
                        new_task.start_time = template_end_time
                        new_task.end_time = task_end_time
                        new_task.work_time = new_work_time
                        new_task.task_block_length = new_time_block_length
                        task_temp.append(new_task)
                    # 任务放入模板
                    task_list: List[Tasks] = template_dict.get(template, [])
                    new_task_flag = False
                    while people_num > 0:
                        if not new_task_flag:
                            put_task_flag = False
                            for i in range(len(task_list)):
                                t_task = task_list[i]
                                if not t_task.is_available(task_start_time, template_end_time, bid,
                                                           self.combine_rules_dict):
                                    continue
                                t_task.put_task(bid, task_start_time, template_end_time)
                                task_list[i] = t_task
                                people_num -= 1
                                put_task_flag = True
                                break
                            if not put_task_flag:
                                new_task_flag = True
                        else:
                            new_task = Tasks(template_start_time, template_end_time, self.block_length, is_cross_day)
                            new_task.put_task(bid, task_start_time, template_end_time)
                            task_list.append(new_task)
                            people_num -= 1
                    template_dict[template] = task_list
                elif template_start_time_dt < task_start_time_dt < task_end_time_dt < template_end_time_dt:
                    # 任务在模板内部
                    task_list: List[Tasks] = template_dict.get(template, [])
                    new_task_flag = False
                    while people_num > 0:
                        if not new_task_flag:
                            put_task_flag = False
                            for i in range(len(task_list)):
                                t_task = task_list[i]
                                if not t_task.is_available(task_start_time, task_end_time, bid,
                                                           self.combine_rules_dict):
                                    continue
                                t_task.put_task(bid, task_start_time, task_end_time)
                                task_list[i] = t_task
                                people_num -= 1
                                put_task_flag = True
                                break
                            if not put_task_flag:
                                new_task_flag = True
                        else:
                            new_task = Tasks(template_start_time, template_end_time, self.block_length, is_cross_day)
                            new_task.put_task(bid, task_start_time, task_end_time)
                            task_list.append(new_task)
                            people_num -= 1
                    template_dict[template] = task_list
                else:
                    # 不交叉
                    task_temp.append(task)

            self.fd_tasks = task_temp

        # 间接任务填充
        indirect_task_dict: Dict[str, int] = {}
        total_indirect_task_work_time = 0
        if self.need_place_indirect_task:
            for itask in self.indirect_tasks:
                bid = itask.bid
                work_time = itask.work_time
                total_indirect_task_work_time += work_time
                indirect_task_dict[bid] = work_time

        for template in template_dict:
            task_list = template_dict[template]
            if self.need_place_indirect_task:
                for i in range(len(task_list)):
                    task = task_list[i]
                    if task.is_full():
                        continue
                    need_work_time = task.need_work_time()
                    if total_indirect_task_work_time >= need_work_time:
                        for bid in indirect_task_dict:
                            work_time = indirect_task_dict[bid]
                            if work_time >= need_work_time:
                                task.put_indirect_task(bid, need_work_time)
                                work_time -= need_work_time
                                total_indirect_task_work_time -= need_work_time
                                indirect_task_dict[bid] = work_time
                                break
                            else:
                                task.put_indirect_task(bid, work_time)
                                total_indirect_task_work_time -= work_time
                                indirect_task_dict[bid] = 0
                                need_work_time = task.need_work_time()
                        task_list[i] = task

            # 不完整的template放回fd task池
            new_task_list: List[Tasks] = []
            for task in task_list:
                if task.is_full():
                    new_task_list.append(task)
                else:
                    export_fd_tasks_list = task.export_task(self.fd_task_discard_dict, self.fd_task_min_time_dict,
                                                            self.fd_task_max_time_dict, self.fd_task_fill_coef_dict,
                                                            self.fixed_tasks_list, self.direct_tasks_list,
                                                            self.block_length)
                    for fd_task in export_fd_tasks_list:
                        self.fd_tasks.append(fd_task)

            template_dict[template] = new_task_list

        if self.need_place_indirect_task:
            i_tasks = []
            for bid in indirect_task_dict:
                work_time = indirect_task_dict[bid]
                if work_time:
                    task = InDirectTask(bid, int(work_time))
                    i_tasks.append(task)

            self.indirect_tasks = i_tasks

        self.fd_tasks_sort()
        self.template_dict = template_dict

    def fd_tasks_sort(self):
        """
        对 fd_tasks 排序
        :return:
        """
        if not self.is_cross_day:
            # 不跨天 直接排序
            self.fd_tasks: List[FDTask] = sorted(self.fd_tasks, key=lambda x: (x.start_time, -int(x.task_block_length)))
        else:
            # 跨天 对 start time 转化后排序再转化回来
            fd_tasks_temp = []
            start_time_dt = datetime.strptime(self.start_time, '%H:%M')
            for task in self.fd_tasks:
                task_bid = task.bid
                task_start_time = task.start_time
                task_end_time = task.end_time
                time_block_length = task.task_block_length

                task_start_time_dt = datetime.strptime(task_start_time, '%H:%M')
                task_end_time_dt = datetime.strptime(task_end_time, '%H:%M')

                if task_start_time_dt < start_time_dt:
                    task_start_time_dt = task_start_time_dt + timedelta(days=1)
                if task_end_time_dt < start_time_dt:
                    task_end_time_dt = task_end_time_dt + timedelta(days=1)

                fd_tasks_temp.append((task_bid, task_start_time_dt, task_end_time_dt, time_block_length, task))

            fd_tasks_temp = sorted(fd_tasks_temp, key=lambda x: (x[1], -int(x[3])))

            fd_tasks: List[FDTask] = []
            for task in fd_tasks_temp:
                task_old = task[4]
                fd_tasks.append(task_old)

            self.fd_tasks = fd_tasks

    def get_full_matrix(self) -> List[List[str]]:
        """
        输出完整矩阵 上部为带模板 下部为剩余部分
        :return:
        """
        res: List[List[str]] = []
        for item in self.template_matrix:
            if have_tasks(item):
                res.append(item)
        for item in self.matrix:
            if have_tasks(item):
                res.append(item)
        return res

    def template_dict_to_matrix(self):
        """
        将template dict 转化为 matrix
        :return:
        """
        for template in self.template_dict:
            template_start_time = time_string_formatter(template[0])
            template_end_time = time_string_formatter(template[1])

            start_block = self.time_to_block(self.start_time, template_start_time)
            end_block = self.time_to_block(self.start_time, template_end_time)

            task_list: List[Tasks] = self.template_dict[template]
            for task in task_list:
                task_info = task.task_info
                flag = False
                for line in range(len(self.template_matrix)):
                    item = self.template_matrix[line]
                    if not self.line_available(item, start_block, end_block, task_info):
                        continue
                    for i in range(end_block - start_block):
                        item[start_block + i] = task_info[i]
                    self.template_matrix[line] = item
                    flag = True
                    break
                if not flag:
                    item = ['' for _ in range(self.time_block_length)]
                    for i in range(end_block - start_block):
                        item[start_block + i] = task_info[i]
                    self.template_matrix.append(item)

    def line_available(self, line_item: List[str], start_block: int, end_block: int, task_info: List[str]) -> bool:
        """
        是否能放入
        :param line_item:
        :param start_block:
        :param end_block:
        :param task_info:
        :return:
        """
        # 校验空位
        for i in range(start_block, end_block):
            if line_item[i]:
                return False

        task_info_bids = list(set(task_info))
        exist_bids = list(set([task for task in line_item if task]))

        # 如果不是空行，校验组合规则
        if exist_bids:
            for bid in task_info_bids:
                if bid in exist_bids:
                    # 已存在，无需校验
                    continue
                if bid in self.indirect_tasks_list:
                    # 间接任务，无需校验
                    continue
                else:
                    if bid not in self.combine_rules_dict:
                        return False
                    combine_list = self.combine_rules_dict[bid]
                    for exist_bid in exist_bids:
                        if exist_bid not in combine_list:
                            return False

        # 校验最大工时
        if not self.max_work_time_check(line_item, len(task_info)):
            return False

        return True

    def generate_matrix(self):
        """
        生成矩阵
        :return:
        """
        fd_task_dict: Dict[int, List[str]] = {}
        fd_task_discard_dict: Dict[str, bool] = {}
        fd_task_min_time_dict: Dict[str, int] = {}
        fd_task_max_time_dict: Dict[str, int] = {}
        for task in self.fd_tasks:
            bid = task.bid
            start_time = task.start_time
            end_time = task.end_time
            work_time = int(task.work_time)
            discard = task.discard
            task_min_time = task.task_min_time
            task_max_time = task.task_max_time

            start_block = self.time_to_block(self.start_time, start_time)
            end_block = self.time_to_block(self.start_time, end_time)
            people_num = calculate_people_num(start_time, end_time, work_time)
            for i in range(start_block, end_block):
                task_list: List[str] = fd_task_dict.get(i, [])
                for j in range(people_num):
                    task_list.append(bid)
                fd_task_dict[i] = task_list

            fd_task_discard_dict[bid] = discard
            fd_task_min_time_dict[bid] = task_min_time
            fd_task_max_time_dict[bid] = task_max_time

        indirect_task_dict: Dict[str, int] = {}
        for task in self.indirect_tasks:
            bid = task.bid
            work_time = int(task.work_time)

            people_num = int(work_time / self.block_length)

            old_people_num = indirect_task_dict.get(bid, 0)
            indirect_task_dict[bid] = old_people_num + people_num

        min_shift_length_minutes: int = self.min_shift_length_rule[1]
        if min_shift_length_minutes % self.block_length == 0:
            min_shift_length = min_shift_length_minutes // self.block_length
        else:
            min_shift_length = min_shift_length_minutes // self.block_length + 1

        min_shift_length_compare_rule: str = self.min_shift_length_rule[0]
        if min_shift_length_compare_rule == 'gt':
            min_shift_length += 1

        if self.max_shift_length_rule:
            max_shift_length_minutes: int = self.max_shift_length_rule[1]
            if max_shift_length_minutes % self.block_length == 0:
                max_shift_length = max_shift_length_minutes // self.block_length
            else:
                max_shift_length = max_shift_length_minutes // self.block_length + 1

            max_shift_length_compare_rule: str = self.max_shift_length_rule[0]
            if max_shift_length_compare_rule == 'lt':
                max_shift_length -= 1
        else:
            max_shift_length = self.time_block_length

        not_discard_bid_dict: Dict[int, List[str]] = {}

        last_bid: str = ''

        fd_task_dict_temp_priority = {}

        while fd_task_dict:
            flag = False
            start_block = sorted(fd_task_dict.keys())[0]

            if not self.only_generate_priority_tasks:
                # 正常情况
                task_list = sorted(fd_task_dict[start_block])
                if not task_list:
                    fd_task_dict.pop(start_block)
                    continue

                bid = ''
                if last_bid:
                    if last_bid in task_list:
                        bid = last_bid

                if not bid:
                    if self.priority_task_list:
                        priority_tasks = []
                        for task_bid in self.priority_task_list:
                            if task_bid in task_list:
                                priority_tasks.append(task_bid)
                        if priority_tasks:
                            bid = random.choice(list(set(priority_tasks)))

                if not bid:
                    bid = random.choice(task_list)

                # bid = task_list[0]
            else:
                # 恢复原状
                if start_block > self.open_close_max_length:
                    if fd_task_dict_temp_priority:
                        for i in fd_task_dict_temp_priority:
                            fd_task_dict[i] = fd_task_dict_temp_priority[i]
                    self.only_generate_priority_tasks = False
                    continue

                # 只排priority_task
                task_list = fd_task_dict[start_block]
                p_task_list = [i for i in task_list if i in self.priority_task_list]
                if not p_task_list:
                    fd_task_dict_temp_priority[start_block] = task_list
                    fd_task_dict.pop(start_block)
                    continue

                bid = ''
                if last_bid:
                    if last_bid in task_list:
                        bid = last_bid

                if not bid:
                    bid = random.choice(p_task_list)

            discard = self.fd_task_discard_dict.get(bid, True)

            min_task_time = self.fd_task_min_time_dict.get(bid, 0)
            max_task_time = self.fd_task_max_time_dict.get(bid, 8 * 60)

            max_task_time = max_task_time if max_task_time else 480

            min_task_block_length = min_task_time // self.block_length if min_task_time % self.block_length == 0 else \
                min_task_time // self.block_length + 1
            max_task_block_length = max_task_time // self.block_length if max_task_time % self.block_length == 0 else \
                max_task_time // self.block_length + 1

            for line in range(len(self.matrix)):
                if self.matrix_status[line] == 1:
                    continue
                item = self.matrix[line]
                if not item[start_block]:
                    # 如果格子是空的，可以进行条件判定
                    if start_block == 0:
                        # 放第一个格子，那么需要至少放入最短班段长度
                        time_block_length = min_shift_length
                    else:
                        if item[start_block - 1]:
                            # 前一个格子有task了
                            if bid == item[start_block - 1]:
                                # 如果要填入的task bid和前一个格子是相同的
                                # 不能大于任务最大长度限制
                                task_len = 1
                                for i in range(start_block - 1, -1, -1):
                                    pre_task_bid = item[i]
                                    if pre_task_bid == bid:
                                        task_len += 1
                                    else:
                                        break
                                if task_len > max_task_block_length:
                                    # 已经比最大任务长度要求高了
                                    continue
                                else:
                                    # 否则可以放入一个
                                    time_block_length = 1
                            else:
                                # 如果要填入的task bid和前一个格子是不同的
                                # 需要填入最小任务长度

                                if min_task_time <= self.block_length:
                                    # 没有最小任务长度限制
                                    time_block_length = 1
                                else:
                                    # 1. 如果剩余格子不够最小任务长度了，只能放剩余格子长度 TODO: 其他解法？
                                    if self.time_block_length - start_block < min_task_block_length:
                                        time_block_length = self.time_block_length - start_block
                                    # 2. 剩余格子足够最小任务长度
                                    else:
                                        time_block_length = min_task_block_length
                        else:
                            # 前面是空的，所以至少需要放入最短班段长度
                            time_block_length = min_shift_length

                    # 条件7 剩余长度需要大于最小班段长度
                    if self.time_block_length - start_block < time_block_length:
                        continue

                    # 条件2 最大工时数
                    if not self.max_work_time_check(item, time_block_length):
                        self.matrix_status[line] = 1
                        continue

                    # 条件3 最大间隔时段
                    if not self.max_interval_check(item, start_block):
                        self.matrix_status[line] = 1
                        continue

                    # 条件4 最大班段数
                    if not self.max_shift_num_rule_check(bid, item, start_block):
                        self.matrix_status[line] = 1
                        continue

                    # 条件8 最大任务个数
                    if not self.max_task_count_rule_check(bid, item, start_block, False):
                        self.matrix_status[line] = 1
                        continue

                    # 条件6 最小间隔时段
                    if not self.min_interval_check(item, start_block):
                        continue

                    # 条件5 最大班段长度
                    if not self.max_shift_length_rule_check(bid, item, time_block_length, start_block):
                        continue

                    # 条件1 组合规则需要满足
                    if not self.combine_rule_check(bid, item, start_block):
                        continue

                    # 更多条件添加可以放在这里

                    exist_shift_length = 0
                    for i in range(start_block - 1, -1, -1):
                        if item[i]:
                            exist_shift_length += 1
                        else:
                            break

                    if time_block_length == 1:
                        # 只需放一个的话
                        # 条件验证通过，可以写入
                        flag = True
                        item[start_block] = bid
                        if len(task_list) > 1:
                            task_list.remove(bid)
                            fd_task_dict[start_block] = task_list
                        else:
                            fd_task_dict.pop(start_block)
                        self.matrix[line] = item
                        if self.debug:
                            self.debug_matrix[line][start_block] = bid
                        break
                    else:
                        exist_bid_task_len = 0  # 已经存在的任务长度
                        for i in range(start_block - 1, -1, -1):
                            if item[i] == bid:
                                exist_bid_task_len += 1
                            else:
                                break
                        if exist_bid_task_len < min_task_block_length:
                            # 如果还没达到最小任务长度限制
                            need_task_block_length = min_task_block_length - exist_bid_task_len  # 还需要填充的长度
                            if need_task_block_length > time_block_length:
                                # 如果还需要填充的任务长度大于了需要填充的长度
                                if exist_shift_length + need_task_block_length > max_shift_length:
                                    # 校验一下是否大于了最大班次长度限制
                                    continue
                                if self.time_block_length - start_block < need_task_block_length:
                                    # 校验一下是否越界
                                    continue
                                need_fill_length = need_task_block_length  # 需要填充的长度
                            else:
                                need_fill_length = time_block_length
                        else:
                            # 已经达到了最小任务长度限制
                            need_task_block_length = 1  # 第一个放bid即可了
                            need_fill_length = time_block_length

                        """
                        task_dict = copy.deepcopy(fd_task_dict)
                        temp_indirect_task_dict = copy.deepcopy(indirect_task_dict)
                        temp_item = copy.deepcopy(item)
                        task_bid = copy.deepcopy(bid)
                        """

                        self.fd_task_dict_temp = copy.deepcopy(fd_task_dict)
                        self.indirect_tasks_temp = copy.deepcopy(indirect_task_dict)
                        self.line_item_temp = copy.deepcopy(item)
                        task_bid = copy.deepcopy(bid)

                        self.temp_fill_block = []
                        fill_res = self.fill_task_to_line(start_block, need_fill_length, task_bid,
                                                          need_task_block_length)

                        if not fill_res:
                            self.temp_fill_block = []
                            continue
                        else:
                            if self.temp_fill_block and self.fill_coef < 1:
                                fill_num = len(self.temp_fill_block)
                                total_task_num = len([i for i in self.line_item_temp if i]) - \
                                                 len([i for i in self.line_item_temp if i == 'break'])
                                fill_rate = fill_num / total_task_num
                                if fill_rate > 1 - self.fill_coef:
                                    # 拆分规则 班次填补系数不满足
                                    continue
                            flag = True
                            fd_task_dict = self.fd_task_dict_temp
                            indirect_task_dict = self.indirect_tasks_temp
                            self.matrix[line] = self.line_item_temp
                            for i in self.temp_fill_block:
                                infoLog.info('填补了' + self.block_to_time(i[0]) + '的任务，bid为：' + i[1])
                            if self.debug:
                                debug_item = self.debug_matrix[line]
                                fill_list = [item[0] for item in self.temp_fill_block]
                                for i in range(start_block, len(self.line_item_temp)):
                                    if i not in fill_list:
                                        debug_item[i] = self.line_item_temp[i]
                                    else:
                                        debug_item[i] = ''
                                self.debug_matrix[line] = debug_item
                            break
            if not flag:
                # 全程没进行操作，所以行数不够用了
                # 先检查一下最后一行是否为空，如果为空，则删除此bid，若不能discard，则加入强制保留字典
                last_line = self.matrix[-1]
                exist_tasks = [b for b in list(set(last_line)) if b]
                if not exist_tasks:
                    # 最后一行是空的
                    task_list = fd_task_dict.get(start_block, [])
                    task_list.remove(bid)
                    if task_list:
                        fd_task_dict[start_block] = task_list
                    else:
                        fd_task_dict.pop(start_block)

                    # TODO: 将300细化
                    if not discard or self.min_shift_length_rule[1] > 300 or self.only_generate_priority_tasks:
                        task_bid_list = not_discard_bid_dict.get(start_block, [])
                        task_bid_list.append(bid)
                        not_discard_bid_dict[start_block] = task_bid_list
                    else:
                        infoLog.info('删除了' + self.block_to_time(start_block) + '的任务，bid为：' + bid)
                    last_bid = ''
                else:
                    self.matrix.append(['' for _ in range(self.time_block_length)])
                    self.matrix_status.append(0)
                    if self.debug:
                        self.debug_matrix.append(['' for _ in range(self.time_block_length)])
            else:
                last_bid = bid
                if self.with_break:
                    for line in range(len(self.matrix)):
                        item = self.matrix[line]
                        if not self.check_if_need_insert_break(item):
                            continue
                        line_item, re_task_dict = self.insert_break_to_line(item)
                        self.matrix[line] = line_item
                        for block in re_task_dict:
                            task = re_task_dict[block]
                            all_task_list = fd_task_dict.get(block, [])
                            all_task_list.append(task)
                            fd_task_dict[block] = sorted(all_task_list)

        if self.with_break:
            if not_discard_bid_dict:
                for start_block in sorted(not_discard_bid_dict.keys()):
                    task_list = sorted(not_discard_bid_dict[start_block])
                    if not task_list:
                        not_discard_bid_dict.pop(start_block)
                        continue
                    remove_task_list: List[str] = []
                    for bid in task_list:
                        for line in range(len(self.matrix)):
                            item = self.matrix[line]
                            if item[start_block]:
                                continue

                            if start_block == 0 and not item[1]:
                                continue
                            elif start_block == self.time_block_length - 1 and not item[self.time_block_length - 2]:
                                continue
                            elif not item[start_block - 1] and not item[start_block + 1]:
                                continue

                            # 条件2 最大工时数
                            if not self.max_work_time_check(item, 1):
                                continue

                            # 条件8 最大任务个数
                            if not self.max_task_count_rule_check(bid, item, start_block, True):
                                continue

                            # 条件5 最大班段长度
                            if not self.max_shift_length_rule_check_for_indirectwh(bid, item, start_block):
                                continue

                            # 条件1 组合规则需要满足
                            if not self.combine_rule_check_all(bid, item):
                                continue

                            # 条件x 无休息班次不能超过定长
                            if self.BREAK_TASK_NAME not in item:
                                exist_shift_length = 0
                                for i in range(start_block - 1, -1, -1):
                                    if item[i]:
                                        exist_shift_length += 1
                                    else:
                                        break
                                for i in range(start_block + 1, self.time_block_length):
                                    if item[i]:
                                        exist_shift_length += 1
                                    else:
                                        break
                                if (exist_shift_length + 1) * self.block_length >= self.no_break_shift_time:
                                    continue

                            # 校验成功
                            item[start_block] = bid
                            remove_task_list.append(bid)
                            self.matrix[line] = item
                            break
                    if remove_task_list:
                        for bid in remove_task_list:
                            task_list.remove(bid)
                        if task_list:
                            not_discard_bid_dict[start_block] = task_list
                        else:
                            not_discard_bid_dict.pop(start_block)

        # 将不能删除的杂任务插到矩阵下方
        if not_discard_bid_dict:
            n_matrix = [['' for _ in range(self.time_block_length)]]
            n_matrix_status = [0]
            for block in not_discard_bid_dict:
                task_list = not_discard_bid_dict[block]
                while task_list:
                    flag = False
                    bid = task_list[0]
                    for line in range(len(n_matrix)):
                        item = n_matrix[line]
                        if item[block]:
                            continue
                        if not self.combine_rule_check_all(bid, item):
                            # 组合规则判定
                            continue
                        if not self.max_task_count_rule_check(bid, item, block, True):
                            # 任务个数判定
                            continue

                        # 条件2 最大工时数
                        if not self.max_work_time_check(item, 1):
                            continue

                        # 条件3 最大间隔时段
                        if not self.max_interval_check(item, block):
                            continue

                        # 条件4 最大班次个数
                        if not self.max_shift_num_rule_check(bid, item, block):
                            continue

                        # 条件6 最小间隔时段
                        if not self.min_interval_check(item, block):
                            continue

                        # 条件5 最大班段长度
                        if not self.max_shift_length_rule_check(bid, item, 1, block):
                            continue

                        # 条件7 最大任务长度
                        if not self.max_task_work_time_check(bid, item, 1):
                            continue

                        item[block] = bid
                        task_list.remove(bid)
                        n_matrix[line] = item
                        flag = True
                        break
                    if not flag:
                        n_matrix.append(['' for _ in range(self.time_block_length)])
                        n_matrix_status.append(0)
            for item in n_matrix:
                self.matrix.append(item)
                if self.debug:
                    self.debug_matrix.append(item)
            for status in n_matrix_status:
                self.matrix_status.append(status)

        # 直接工时已经放完了，也满足了所有条件，检查剩余的间接工时
        # 预处理
        for bid in indirect_task_dict:
            if indirect_task_dict.get(bid) == 0:
                indirect_task_dict.pop(bid)
        if not indirect_task_dict:
            # 间接工时也没了 不需要做任何事
            pass
        else:
            total_block_length = sum(indirect_task_dict.values())
            need_insert_bid_num = 0
            integer_divide_length = 0
            integer_divide_num = 0

            if self.max_shift_length_rule:
                max_shift_length = int(self.max_shift_length_rule[1]) // self.block_length
                if self.max_shift_length_rule[0] == 'lt':
                    max_shift_length -= 1
            elif self.max_working_hour_rule:
                max_shift_length = int(self.max_working_hour_rule[1]) // self.block_length
                if self.max_working_hour_rule[0] == 'lt':
                    max_shift_length -= 1
            else:
                # 没规定就8小时 或者全长
                max_shift_length = 480 // self.block_length
                if max_shift_length > self.time_block_length:
                    max_shift_length = self.time_block_length

            if total_block_length < min_shift_length:
                # 剩余长度小于最小长度，需要都插入到上面的矩阵中
                need_insert_bid_num = total_block_length
            elif total_block_length <= max_shift_length:
                # 剩余长度介于最小长度和最大长度之间，那直接插一行新的即可
                integer_divide_length = total_block_length
                integer_divide_num = 1
            else:
                # 更长的情况
                need_insert_bid_num = total_block_length % min_shift_length
                integer_divide_num = total_block_length // min_shift_length
                integer_divide_length = min_shift_length
                for length in range(min_shift_length + 1, max_shift_length + 1):
                    need_num = total_block_length % length
                    if need_num <= need_insert_bid_num:
                        need_insert_bid_num = need_num
                        integer_divide_num = total_block_length // length
                        integer_divide_length = length

            # 如果需要构造多余的几行间接任务
            if integer_divide_num:
                for i in range(integer_divide_num):
                    line = ['' for _ in range(self.time_block_length)]
                    for j in range(integer_divide_length):
                        bid = sorted(indirect_task_dict.keys())[0]
                        line[j] = bid
                        if indirect_task_dict[bid] > 1:
                            indirect_task_dict[bid] = indirect_task_dict[bid] - 1
                        else:
                            indirect_task_dict.pop(bid)
                    self.matrix.append(line)
                    self.matrix_status.append(0)
                    if self.debug:
                        self.debug_matrix.append(line)

            # 如果有需要插入的间接任务
            if need_insert_bid_num:
                indirect_task_flag = True
                for line in range(len(self.matrix)):
                    if not indirect_task_flag:
                        break
                    item = self.matrix[line]
                    for column in range(len(item)):
                        block = item[column]
                        if block:
                            continue

                        # 最大工作时长
                        if not self.max_work_time_check(item, 1):
                            continue

                        # 最小间隔 前
                        if not self.min_interval_check(item, column):
                            continue

                        # 最小间隔 后
                        if not self.min_interval_check_for_indirect(item, column):
                            continue

                        bid = sorted(indirect_task_dict.keys())[0]

                        if not self.max_shift_length_rule_check_for_indirectwh(bid, item, column):
                            continue

                        if not self.min_shift_length_rule_check_for_indirectwh(bid, item, column):
                            continue

                        # 最大任务数
                        if not self.max_task_count_rule_check(bid, item, column, True):
                            continue

                        # 最大班次数
                        if not self.max_shift_num_rule_check(bid, item, column):
                            continue

                        self.matrix[line][column] = bid

                        if self.debug:
                            self.debug_matrix[line][column] = bid

                        if indirect_task_dict[bid] > 1:
                            indirect_task_dict[bid] = indirect_task_dict[bid] - 1
                        else:
                            indirect_task_dict.pop(bid)
                        if not indirect_task_dict:
                            indirect_task_flag = False
                            break

                # 遍历完整个矩阵, 如果还没插完，直接插到一行新的
                if indirect_task_dict:
                    line = ["" for _ in range(self.time_block_length)]
                    need_insert_bid_num = 0
                    for bid in indirect_task_dict:
                        task_num = indirect_task_dict.get(bid, 0)
                        if task_num > 0:
                            need_insert_bid_num += task_num
                        else:
                            indirect_task_dict.pop(bid)
                    for i in range(need_insert_bid_num):
                        bid = sorted(indirect_task_dict.keys())[0]
                        line[i] = bid
                        if indirect_task_dict[bid] > 1:
                            indirect_task_dict[bid] = indirect_task_dict[bid] - 1
                        else:
                            indirect_task_dict.pop(bid)
                    self.matrix.append(line)
                    self.matrix_status.append(0)
                    if self.debug:
                        self.debug_matrix.append(line)

    def check_if_need_insert_break(self, line_item: List[str]) -> bool:
        """
        检查是否需要填充休息
        :param line_item:
        :return:
        """
        if self.BREAK_TASK_NAME in line_item:
            return False
        longest_shift_length: int = 0
        now_shift_length: int = 0
        for task_bid in line_item:
            if not task_bid:
                if now_shift_length > 0:
                    longest_shift_length = now_shift_length if now_shift_length > longest_shift_length else \
                        longest_shift_length
                    now_shift_length = 0
            else:
                now_shift_length += 1
        if now_shift_length > 0:
            longest_shift_length = now_shift_length if now_shift_length > longest_shift_length else longest_shift_length

        if longest_shift_length * self.block_length >= self.no_break_shift_time:
            return True
        return False

    def get_position_of_need_break_shift(self, item: List[str]) -> Tuple[int, int]:
        """
        得到需要插入（置换）休息的班次开始位置和长度
        TODO: 现在仅支持给最长的添加，如果有多个班次添加休息需求，需要修改这里
        :param item:
        :return:
        """
        start: int = 0
        longest_shift_length: int = 0
        now_shift_length: int = 0
        for i in range(len(item)):
            task_bid = item[i]
            if not task_bid:
                if now_shift_length > 0:
                    if now_shift_length > longest_shift_length:
                        start = i - now_shift_length
                        longest_shift_length = now_shift_length
                    now_shift_length = 0
            else:
                now_shift_length += 1
        if now_shift_length > 0:
            if now_shift_length > longest_shift_length:
                start = len(item) - now_shift_length
                longest_shift_length = now_shift_length

        return start, longest_shift_length

    def insert_break_to_line(self, item: List[str]) -> Tuple[List[str], Dict[int, str]]:
        """
        插入休息
        TODO: 校验任务长度
        :param item:
        :return:
        """
        line_item = copy.deepcopy(item)
        start, length = self.get_position_of_need_break_shift(item)
        if self.break_length > 1:
            length = length - self.break_length + 1
        first_priority: List[int] = []
        second_priority: List[int] = []
        third_priority: List[int] = []
        not_available: List[int] = []
        if start + self.prev_no_break_length - 1 > 0:
            if item[start + self.prev_no_break_length - 1] != item[start + self.prev_no_break_length]:
                second_priority.append(start + self.prev_no_break_length)
        for i in range(start + self.prev_no_break_length, start + length - 1 - self.rear_no_break_length):
            if item[i] != item[i + 1]:
                second_priority.append(i)
                second_priority.append(i + 1)
        second_priority = list(set(second_priority))

        for i in range(start, start + self.prev_no_break_length):
            not_available.append(i)
        for i in range(start + length - self.rear_no_break_length, start + length):
            not_available.append(i)
        for i in range(start, start + length):
            break_num = self.break_count[i]
            if break_num >= self.max_break_count:
                not_available.append(i)
        not_available = list(set(not_available))

        for i in not_available:
            if i in second_priority:
                second_priority.remove(i)

        for i in second_priority:
            if i > 0:
                prev_break_num = self.break_count[i - 1]
            else:
                prev_break_num = 0
            if i < len(item) - 1:
                rear_break_num = self.break_count[i + 1]
            else:
                rear_break_num = 0
            if prev_break_num or rear_break_num:
                first_priority.append(i)

        for i in first_priority:
            if i in second_priority:
                second_priority.remove(i)

        if self.priority_task_list:
            for i in first_priority:
                if item[i] in self.priority_task_list:
                    not_available.append(i)

            for i in second_priority:
                if item[i] in self.priority_task_list:
                    not_available.append(i)

            for i in not_available:
                if i in first_priority:
                    first_priority.remove(i)
                if i in second_priority:
                    second_priority.remove(i)

        for i in range(start, start + length):
            if i not in first_priority and i not in not_available and i not in second_priority:
                third_priority.append(i)

        bid_dict: Dict[int, str] = {}
        if first_priority:
            block = random.choice(first_priority)
        elif second_priority:
            block = random.choice(second_priority)
        elif third_priority:
            block = random.choice(third_priority)
        else:
            infoLog.warning('insert break failed.')
            return item, {}
        for i in range(self.break_length):
            bid_dict[block + i] = item[block + i]
            self.break_count[block + i] = self.break_count[block + i] + 1
            line_item[block + i] = self.BREAK_TASK_NAME
        return line_item, bid_dict

    def fill_task_to_line(self, start_block: int, need_fill_length: int, task_bid: str,
                          need_task_block_length: int) -> bool:
        """
        填充整行
        :param start_block:
        :param need_fill_length:
        :param task_bid:
        :param need_task_block_length:
        :return:
        """
        max_task_time = self.fd_task_max_time_dict.get(task_bid, 8 * 60)
        max_task_time = max_task_time if max_task_time else 480
        max_task_block_length = max_task_time // self.block_length if max_task_time % self.block_length == 0 else \
            max_task_time // self.block_length + 1
        max_fill_task_length = max_task_block_length
        for i in range(self.time_block_length - 1, -1, -1):
            if self.line_item_temp[i] == task_bid:
                max_fill_task_length -= 1
        if max_fill_task_length > need_fill_length:
            max_fill_task_length = need_fill_length
        elif max_fill_task_length <= 0:
            another_bid = ''
            while not another_bid:
                task_list = list(set(self.fd_task_dict_temp.get(start_block, [])))
                avaliable_task_list = []
                for bid in task_list:
                    if bid == task_bid:
                        continue
                    if not self.combine_rule_check(bid, self.line_item_temp, start_block):
                        # 组合规则
                        continue
                    if not self.max_task_count_rule_check(bid, self.line_item_temp, start_block, False):
                        # 最大任务数
                        continue
                    avaliable_task_list.append(bid)
                if avaliable_task_list:
                    shuffled_task_list = list(set(avaliable_task_list))
                    random.shuffle(shuffled_task_list)
                    for another_bid in shuffled_task_list:
                        min_task_time_for_another_bid = self.fd_task_min_time_dict.get(another_bid, self.block_length)
                        min_task_block_length_for_another_bid = min_task_time_for_another_bid // self.block_length if \
                            min_task_time_for_another_bid % self.block_length == 0 else \
                            min_task_time_for_another_bid // self.block_length + 1
                        if min_task_block_length_for_another_bid > need_fill_length:
                            continue
                        fd_task_dict_temp = copy.deepcopy(self.fd_task_dict_temp)
                        line_item_temp = copy.deepcopy(self.line_item_temp)
                        indirect_task_dict_temp = copy.deepcopy(self.indirect_tasks_temp)
                        res = self.fill_task_to_line(start_block, need_fill_length, another_bid,
                                                     min_task_block_length_for_another_bid)
                        if res:
                            return res
                        else:
                            self.fd_task_dict_temp = fd_task_dict_temp
                            self.line_item_temp = line_item_temp
                            self.indirect_tasks_temp = indirect_task_dict_temp
                elif self.indirect_tasks_temp:
                    for bid in self.indirect_tasks_temp:
                        if self.indirect_tasks_temp.get(bid) < 1:
                            self.indirect_tasks_temp.pop(bid)
                    if self.indirect_tasks_temp:
                        bid = list(self.indirect_tasks_temp.keys())[0]
                        task_block_length = self.indirect_tasks_temp.get(bid, 1)
                        if not self.max_task_count_rule_check(bid, self.line_item_temp, start_block, False):
                            return False
                        self.line_item_temp[start_block] = bid
                        if task_block_length - 1 > 0:
                            self.indirect_tasks_temp[bid] = task_block_length - 1
                        else:
                            self.indirect_tasks_temp.pop(bid)
                        if need_fill_length - 1 <= 0:
                            return True
                        else:
                            start_block += 1
                    else:
                        return False
                else:
                    return False
        if max_fill_task_length > need_task_block_length:
            res_list = []
            have_task_hours_num = 0
            total_task_num = 0
            for i in range(0, max_fill_task_length):
                pivot = start_block + i
                task_list = self.fd_task_dict_temp.get(pivot, [])
                if task_bid in task_list:
                    have_task_hours_num += 1
                total_task_num += 1
                res_list.append(have_task_hours_num / total_task_num)
            if need_task_block_length >= 1:
                cut_pre_len = need_task_block_length - 1
            else:
                cut_pre_len = 0
            max_fulfill_rate = max(res_list[cut_pre_len:])
            fill_coef = self.fd_task_fill_coef_dict.get(task_bid, 1)
            if max_fulfill_rate < fill_coef:
                return False

            fill_length = need_task_block_length + len(res_list[cut_pre_len:]) - \
                          res_list[cut_pre_len:][::-1].index(max_fulfill_rate) - 1
        else:
            fill_length = need_task_block_length - 1
        if not fill_length:
            fill_length = 1
        if fill_length > len(self.line_item_temp) - start_block:
            return False
        if fill_length >= need_fill_length:
            fill_length_true = need_fill_length
        else:
            fill_length_true = fill_length
        for i in range(start_block, start_block + fill_length_true):
            self.line_item_temp[i] = task_bid
            task_list = self.fd_task_dict_temp.get(i, [])
            if task_bid in task_list:
                task_list.remove(task_bid)
                if task_list:
                    self.fd_task_dict_temp[i] = task_list
                else:
                    self.fd_task_dict_temp.pop(i)
            else:
                fill_coef = self.fd_task_fill_coef_dict.get(task_bid, 0)
                if fill_coef >= 1:
                    return False
                else:
                    self.temp_fill_block.append((i, task_bid))
        if fill_length >= need_fill_length:
            return True

        next_start_block = start_block + fill_length
        next_need_fill_length = need_fill_length - fill_length
        next_task_bid_list = self.fd_task_dict_temp.get(next_start_block, [])
        while not next_task_bid_list:
            for bid in self.indirect_tasks_temp:
                if self.indirect_tasks_temp.get(bid) < 1:
                    self.indirect_tasks_temp.pop(bid)
            if not self.indirect_tasks_temp:
                return False
            else:
                bid = list(self.indirect_tasks_temp.keys())[0]
                task_block_length = self.indirect_tasks_temp.get(bid, 1)
                if not self.max_task_count_rule_check(bid, self.line_item_temp, start_block, False):
                    return False
                self.line_item_temp[next_start_block] = bid
                if task_block_length - 1 > 0:
                    self.indirect_tasks_temp[bid] = task_block_length - 1
                else:
                    self.indirect_tasks_temp.pop(bid)
                next_need_fill_length -= 1
                if not next_need_fill_length:
                    return True
                next_start_block += 1
                next_task_bid_list = self.fd_task_dict_temp.get(next_start_block, [])
        next_task_bid = ''
        if next_start_block - 1 > 0:
            if self.line_item_temp[next_start_block - 1]:
                last_bid = self.line_item_temp[next_start_block - 1]
                if last_bid in next_task_bid_list:
                    next_task_bid = last_bid
        if not next_task_bid:
            available_bid_list = []
            for bid in next_task_bid_list:
                if not self.combine_rule_check(bid, self.line_item_temp, next_start_block):
                    # 检查组合规则
                    continue
                available_bid_list.append(bid)
            if available_bid_list:
                next_task_bid = random.choice(list(set(available_bid_list)))
        if not next_task_bid:
            return False
        min_task_time_for_next_task_bid = self.fd_task_min_time_dict.get(next_task_bid, self.block_length)
        min_task_block_length = min_task_time_for_next_task_bid // self.block_length if \
            min_task_time_for_next_task_bid % self.block_length == 0 else \
            min_task_time_for_next_task_bid // self.block_length + 1
        exist_next_bid_num = 0
        for i in range(next_start_block - 1, -1, -1):
            if self.line_item_temp[i] == next_task_bid:
                exist_next_bid_num += 1
            else:
                break
        next_task_block_length = min_task_block_length - exist_next_bid_num
        if next_task_block_length < 0:
            next_task_block_length = 0

        return self.fill_task_to_line(next_start_block, next_need_fill_length, next_task_bid,
                                      next_task_block_length)

    def modify_matrix(self):
        """
        移动可以移动的格子 使得一列中尽量少种类的工种
        :return:
        """
        for line in range(len(self.matrix)):
            # 从上到下逐行遍历
            item = self.matrix[line]
            for column in range(1, len(item)):
                # 从左到右逐列遍历
                block = self.matrix[line][column]
                block_prev = self.matrix[line][column - 1]
                if block == block_prev or block in self.indirect_tasks_list or not block or not block_prev:
                    continue
                if block == self.BREAK_TASK_NAME:
                    continue
                # 如果和前面的不一样
                for line_b in range(len(self.matrix) - 1, line, -1):
                    # 从下往上遍历本行
                    item_b = self.matrix[line_b]
                    block_b = item_b[column]
                    block_b_prev = self.matrix[line_b][column - 1]
                    if block_b != block_prev or block_b == block_b_prev:
                        continue
                    if block_b == self.BREAK_TASK_NAME:
                        continue
                    # 1 组合规则
                    if not self.combine_rule_check(block, item_b[:column] + item_b[column + 1:], len(item_b)):
                        continue

                    # 检查结束，可以转移
                    self.matrix[line_b][column] = block
                    self.matrix[line][column] = block_b
                    if self.debug:
                        self.debug_matrix[line_b][column] = block
                        self.debug_matrix[line][column] = block_b
                    break

        for line in range(len(self.matrix)):
            # 从上到下逐行遍历
            item = self.matrix[line]
            for column in range(len(item) - 2, 0, -1):
                # 从右到左逐列遍历
                block = self.matrix[line][column]
                block_prev = self.matrix[line][column + 1]
                if block == block_prev or block in self.indirect_tasks_list or not block or not block_prev:
                    continue
                if block == self.BREAK_TASK_NAME:
                    continue
                # 如果和后面的不一样
                for line_b in range(len(self.matrix) - 1, line, -1):
                    # 从下往上遍历本行
                    item_b = self.matrix[line_b]
                    block_b = item_b[column]
                    block_b_prev = self.matrix[line_b][column + 1]
                    if block_b != block_prev or block_b_prev == block_b:
                        continue
                    if block_b == self.BREAK_TASK_NAME:
                        continue

                    # 1 组合规则
                    if not self.combine_rule_check(block, item_b[:column] + item_b[column + 1:], len(item_b)):
                        continue

                    # 检查结束，可以转移
                    self.matrix[line_b][column] = block
                    self.matrix[line][column] = block_b
                    if self.debug:
                        self.debug_matrix[line_b][column] = block
                        self.debug_matrix[line][column] = block_b
                    break

    def indirect_task_convert(self):
        """
        合并相同的间接工时任务
        :return:
        """
        indirect_task_dict: Dict[str, int] = {}
        for task in self.indirect_tasks:
            bid = task.bid
            work_time = task.work_time
            indirect_task_dict[bid] = indirect_task_dict.get(bid, 0) + work_time

        new_indirect_tasks: List[InDirectTask] = []
        for bid in indirect_task_dict:
            task = InDirectTask(bid, indirect_task_dict[bid])
            new_indirect_tasks.append(task)

        if self.use_virtual_indirect_task:
            self.indirect_tasks_list.append('virtual_indirectwh')

        self.indirect_tasks = new_indirect_tasks

    def add_indirect_task_to_matrix(self):
        """
        添加间接工时任务
        :return:
        """
        indirect_task_dict: Dict[str, int] = {}
        for task in self.indirect_tasks:
            bid = task.bid
            work_time = task.work_time
            indirect_task_dict[bid] = indirect_task_dict.get(bid, 0) + work_time

        for task_bid in indirect_task_dict:
            work_time = indirect_task_dict[task_bid]
            if work_time % self.block_length > 0:
                task_length = work_time // self.block_length + 1
            else:
                task_length = work_time // self.block_length
            indirect_task_dict[task_bid] = task_length

        if not indirect_task_dict:
            return

        for line in range(len(self.matrix)):
            item = self.matrix[line]
            for column in range(len(item)):
                block = item[column]
                if block:
                    continue

                # 最大工作时长
                if not self.max_work_time_check(item, 1):
                    continue

                # 最小间隔 前
                if not self.min_interval_check(item, column):
                    continue

                # 最小间隔 后
                if not self.min_interval_check_for_indirect(item, column):
                    continue

                if not indirect_task_dict:
                    return

                for bid in indirect_task_dict:
                    # 最大班次长度
                    if not self.max_shift_length_rule_check_for_indirectwh(bid, item, column):
                        break

                    task_length = indirect_task_dict[bid]
                    self.matrix[line][column] = bid
                    task_length -= 1
                    if task_length == 0:
                        indirect_task_dict.pop(bid)
                    else:
                        indirect_task_dict[bid] = task_length
                    break

    def generate_combine_rules_dict(self):
        """
        转换combine rules to Dict[bid -> List[combine_bids]]
        :return:
        """
        for item in self.combine_rules:
            bid_list = list(set([bid.strip() for bid in item.split(',')]))
            for bid in bid_list:
                bid_list_other = [i for i in bid_list if i != bid]
                if bid in self.combine_rules_dict:
                    combine_list = self.combine_rules_dict[bid]
                    combine_list += bid_list_other
                    combine_list = list(set(combine_list))
                    self.combine_rules_dict[bid] = combine_list
                else:
                    self.combine_rules_dict[bid] = bid_list_other

    def to_dict_new(self, min_matrix: List[List[str]], max_matrix: List[List[str]]) -> List[Dict]:
        """
        输出对应的dict arr
        :return:
        """
        task_type_dict: Dict[str, str] = {}
        for item in self.fixed_tasks:
            bid = item.bid
            task_type_dict[bid] = 'fixedwh'
        for item in self.direct_tasks:
            bid = item.bid
            task_type_dict[bid] = 'directwh'
        for item in self.indirect_tasks:
            bid = item.bid
            task_type_dict[bid] = 'indirectwh'

        task_type_dict[self.BREAK_TASK_NAME] = 'indirectwh'

        result: List[Dict] = []
        done_line: List[int] = []
        done_line_min: List[int] = []
        done_line_max: List[int] = []
        matrix = self.get_full_matrix()
        set_matrix = [list(i) for i in list(set([tuple(j) for j in matrix + max_matrix + min_matrix])) if list(i)]
        for line in range(len(set_matrix)):
            item = set_matrix[line]
            total_val: int = 0
            min_val: int = 0
            max_val: int = 0

            exist_bids = [bid for bid in list(set(item)) if bid]
            if not exist_bids:
                continue

            # value
            for j in range(len(matrix)):
                if j in done_line:
                    continue
                item_j = matrix[j]
                if item_j == item:
                    total_val += 1
                    done_line.append(j)

            # scope min
            for j in range(len(min_matrix)):
                if j in done_line_min:
                    continue
                item_j = min_matrix[j]
                if item_j == item:
                    min_val += 1
                    done_line_min.append(j)

            # scope max
            for j in range(len(max_matrix)):
                if j in done_line_max:
                    continue
                item_j = max_matrix[j]
                if item_j == item:
                    max_val += 1
                    done_line_max.append(j)

            res = {}

            if min_val > max_val:
                temp = min_val
                min_val = max_val
                max_val = temp
            if total_val < min_val:
                total_val = min_val
            if total_val > max_val:
                max_val = total_val

            task_combination = ','.join(exist_bids)
            res['taskCombination'] = task_combination
            res['value'] = total_val
            res['scope'] = [min_val, max_val]

            detail_arr: List[Dict] = []
            last_bid = ''
            start_block = 0
            for i in range(len(item)):
                bid = item[i]
                if bid != last_bid:
                    if last_bid:
                        task_type = task_type_dict.get(last_bid, 'unknown')
                        detail_dict = {
                            'taskId': last_bid,
                            'taskType': task_type,
                            'start': self.block_to_time(start_block),
                            'end': self.block_to_time(i)
                        }
                        detail_arr.append(detail_dict)
                    elif i == len(item) - 1 and bid:
                        task_type = task_type_dict.get(bid, 'unknown')
                        detail_dict = {
                            'taskId': bid,
                            'taskType': task_type,
                            'start': self.block_to_time(start_block),
                            'end': self.block_to_time(i + 1)
                        }
                        detail_arr.append(detail_dict)
                    last_bid = bid
                    start_block = i
                else:
                    if i == len(item) - 1 and bid:
                        task_type = task_type_dict.get(last_bid, 'unknown')
                        detail_dict = {
                            'taskId': last_bid,
                            'taskType': task_type,
                            'start': self.block_to_time(start_block),
                            'end': self.block_to_time(i + 1)
                        }
                        detail_arr.append(detail_dict)
            res['detail'] = detail_arr
            result.append(res)
        return result

    def block_to_time(self, block: int) -> str:
        """
        块编号转化为时间
        :param block:
        :return:
        """
        time = datetime.strptime(self.start_time, '%H:%M') + timedelta(minutes=block * self.block_length)
        return time.strftime('%H:%M')

    def time_to_block(self, start_time: str, end_time: str) -> int:
        """
        开始时间 结束时间 转化为块的长度
        :param start_time:
        :param end_time:
        :return:
        """
        if start_time == '24:00':
            start_time = '00:00'
        if end_time == '24:00':
            end_time = '00:00'
        start_dt = datetime.strptime(start_time, '%H:%M')
        end_dt = datetime.strptime(end_time, '%H:%M')
        if end_dt < start_dt:
            end_dt = end_dt + timedelta(days=1)
        time_delta_minutes = int((end_dt - start_dt).seconds / 60)
        if time_delta_minutes // self.block_length == time_delta_minutes / self.block_length:
            # 能整除
            return time_delta_minutes // self.block_length
        else:
            # 无法整除
            return time_delta_minutes // self.block_length + 1

    @classmethod
    def construct_planner(cls, start_time: str, end_time: str, matrix: List[List[str]]):
        """
        通过部分入参建立一个不完整的planner
        :param matrix:
        :param start_time:
        :param end_time:
        :return:
        """
        time_block_length = len(matrix[0])
        block_length = int(((datetime.strptime(end_time, '%H:%M') -
                             datetime.strptime(start_time, '%H:%M')).seconds + 60) / 60 / time_block_length)
        if end_time < start_time:
            is_cross_day = True
            block_length = int(((datetime.strptime(end_time, '%H:%M') -
                                 datetime.strptime(start_time, '%H:%M') +
                                 timedelta(days=1)).seconds + 60) / 60 / time_block_length)
        else:
            is_cross_day = False
            block_length = int(((datetime.strptime(end_time, '%H:%M') -
                                 datetime.strptime(start_time, '%H:%M')).seconds + 60) / 60 / time_block_length)
        planner = cls(start_time, end_time, block_length, [], [], [], [], is_cross_day, [], [], [], [], [], [], [],
                      False, False, False)
        planner.matrix = matrix
        planner.template_matrix = []

        return planner

    def shrink_matrix(self, new_start_time: str, new_end_time: str, is_cross_day: bool):
        """
        缩减矩阵长度
        :param new_start_time:
        :param new_end_time:
        :param is_cross_day:
        :return:
        """
        time_block_length = self.time_block_length
        matrix = self.matrix
        if new_start_time != self.start_time:
            if new_start_time > self.start_time:
                minus_length = int(((datetime.strptime(new_start_time, '%H:%M') -
                                     datetime.strptime(self.start_time, '%H:%M')).seconds) / 60 / self.block_length)
            else:
                minus_length = int(((datetime.strptime(new_start_time, '%H:%M') -
                                     datetime.strptime(self.start_time, '%H:%M') +
                                     timedelta(days=1)).seconds) / 60 / self.block_length)
            time_block_length -= minus_length
            for i in range(len(matrix)):
                matrix[i] = matrix[i][minus_length:]
        if new_end_time != self.end_time:
            if new_end_time < self.end_time:
                minus_length = int(((datetime.strptime(self.end_time, '%H:%M') -
                                     datetime.strptime(new_end_time, '%H:%M')).seconds) / 60 / self.block_length)
            else:
                minus_length = int(((datetime.strptime(self.end_time, '%H:%M') -
                                     datetime.strptime(new_end_time, '%H:%M') +
                                     timedelta(days=1)).seconds) / 60 / self.block_length)
            time_block_length -= minus_length
            for i in range(len(matrix)):
                matrix[i] = matrix[i][:-minus_length]
        self.matrix = matrix
        self.start_time = new_start_time
        self.end_time = new_end_time
        self.time_block_length = time_block_length
        self.is_cross_day = False if self.start_time < self.end_time else True

    def expand_matrix(self, new_start_time: str, new_end_time: str, is_cross_day: bool):
        """
        扩充矩阵长度
        :param new_start_time:
        :param new_end_time:
        :param is_cross_day:
        :return:
        """
        time_block_length = self.time_block_length
        matrix = self.matrix
        if new_start_time != self.start_time:
            if new_start_time < self.start_time:
                add_length = int(((datetime.strptime(self.start_time, '%H:%M') -
                                   datetime.strptime(new_start_time, '%H:%M')).seconds) / 60 / self.block_length)
            else:
                add_length = int(((datetime.strptime(self.start_time, '%H:%M') -
                                   datetime.strptime(new_start_time, '%H:%M') +
                                   timedelta(days=1)).seconds) / 60 / self.block_length)
            time_block_length += add_length
            for i in range(len(matrix)):
                matrix[i] = ['' for _ in range(add_length)] + matrix[i]
        if new_end_time != self.end_time:
            if new_end_time > self.end_time:
                add_length = int(((datetime.strptime(new_end_time, '%H:%M') -
                                   datetime.strptime(self.end_time, '%H:%M')).seconds) / 60 / self.block_length)
            else:
                add_length = int(((datetime.strptime(new_end_time, '%H:%M') -
                                   datetime.strptime(self.end_time, '%H:%M') +
                                   timedelta(days=1)).seconds) / 60 / self.block_length)
            time_block_length += add_length
            for i in range(len(matrix)):
                matrix[i] = matrix[i] + ['' for _ in range(add_length)]
        self.matrix = matrix
        self.start_time = new_start_time
        self.end_time = new_end_time
        self.time_block_length = time_block_length
        self.is_cross_day = False if self.start_time < self.end_time else True

    def modify_matrix_by_api(self, modify_detail: List[Dict]):
        """
        改矩阵
        :param modify_detail:
        :return:
        """
        matrix_dict: Dict[Tuple, Dict[Tuple, int]] = {}
        new_matrix: List[List[str]] = []
        matrix = self.matrix

        for line_item in matrix:
            task_set = tuple(sorted(list(set([task_bid for task_bid in line_item if task_bid]))))
            task_tuple = tuple(line_item)

            task_tuple_dict = matrix_dict.get(task_set, {})
            value = task_tuple_dict.get(task_tuple, 0)
            task_tuple_dict[task_tuple] = value + 1
            matrix_dict[task_set] = task_tuple_dict

        for item in modify_detail:
            combine_str = item.get('combiRule', '').strip()
            new_value_str = item.get('combiRuleNewVal', '0').strip()
            old_value_str = item.get('combiRuleOldVal', '0').strip()
            detail_list = item.get('detail', [])

            if not detail_list:
                infoLog.warning('need detail for combi: %s to reconstruct matrix.', combine_str)
                continue

            try:
                new_value = int(new_value_str)
                old_value = int(old_value_str)
            except ValueError:
                infoLog.error('combiRuleNewVal: %s, combiRuleOldVal: %s failed to convert to integer.', new_value_str,
                              old_value_str)
                continue

            combine_bids_set = tuple(sorted(list(set([i.strip() for i in combine_str.split(',')]))))
            if combine_bids_set not in matrix_dict:
                infoLog.info('combiRule: %s not in existing matrix.', combine_str)
            matrix_dict[combine_bids_set] = {}

            task_tuple_dict = matrix_dict[combine_bids_set]
            task_line = self.convert_detail_to_task_line(detail_list)
            task_line_tuple = tuple(task_line)

            if task_line_tuple not in task_tuple_dict:
                infoLog.info('task combination %s not in task tuple dict.', combine_str)

            saved_value = task_tuple_dict.get(task_line_tuple, 0)
            if saved_value != old_value:
                infoLog.warning('saved old value: %s, imported old value: %s are different.', str(saved_value),
                                old_value_str)

            if new_value > 0:
                for i in range(new_value):
                    new_matrix.append(task_line)

            if old_value > 0:
                try:
                    task_tuple_dict.pop(task_line_tuple)
                except KeyError:
                    infoLog.warning('task tuple dict keyError: %s', str(task_line_tuple))
            if task_tuple_dict:
                matrix_dict[combine_bids_set] = task_tuple_dict
            else:
                try:
                    matrix_dict.pop(combine_bids_set)
                except KeyError:
                    infoLog.warning('matrix dict keyError: %s', str(combine_bids_set))

        for combine_bids_set in matrix_dict:
            task_tuple_dict = matrix_dict[combine_bids_set]
            for task_tuple in task_tuple_dict:
                saved_value = task_tuple_dict[task_tuple]
                task_line = list(task_tuple)
                for i in range(saved_value):
                    new_matrix.append(task_line)

        self.matrix = new_matrix

    def convert_detail_to_task_line(self, detail_item: List[Dict[str, str]]) -> List[str]:
        """
        将 detail 转化为 matrix 的一行
        :param detail_item:
        :return:
        """
        line = ['' for _ in range(self.time_block_length)]
        for item_dict in detail_item:
            task_id = item_dict.get('taskId', '')
            task_start_time = item_dict.get('start', '')
            task_end_time = item_dict.get('end', '')

            if task_start_time == '24:00':
                task_start_time = '00:00'
            if task_end_time == '24:00':
                task_end_time = '00:00'

            if not task_id:
                # task id 为空
                infoLog.warning('failed to get task id in item dict: %s', str(item_dict))
                continue
            if not task_start_time:
                infoLog.warning('failed to get task start time in item dict: %s', str(item_dict))
                continue
            if not task_end_time:
                infoLog.warning('failed to get task end time in item dict: %s', str(item_dict))
                continue
            if not self.is_cross_day:
                if datetime.strptime(task_start_time, '%H:%M') < datetime.strptime(self.start_time, '%H:%M'):
                    infoLog.error('task start time: %s is behind day start time: %s', task_start_time, self.start_time)
                    continue
                if datetime.strptime(task_end_time, '%H:%M') > datetime.strptime(self.end_time, '%H:%M'):
                    infoLog.error('task end time: %s is after day end time: %s', task_end_time, self.end_time)
                    continue

            start_block = self.time_to_block(self.start_time, task_start_time)
            end_block = self.time_to_block(self.start_time, task_end_time)

            for i in range(start_block, end_block):
                line[i] = task_id

        return line


def task_convert(tasks: List[Tuple[str, str, str, str]], block_length: int) -> List[Tuple[str, str, str, str, str]]:
    """
    对任务从 List[Tuple(bid, start_time, end_time, work_time)]
    转化为 List[Tuple(bid, start_time, end_time, work_time, time_block_length)]
    并排序 key1: start_time key2: time_block_length
    :param block_length:
    :param tasks:
    :return:
    """
    new_tasks: List[Tuple[str, str, str, str, str]] = []
    for task in tasks:
        bid = task[0]
        start_time = task[1]
        end_time = task[2]
        work_time = task[3]

        start_dt = datetime.strptime(start_time, '%H:%M')
        end_dt = datetime.strptime(end_time, '%H:%M')
        if end_dt < start_dt:
            end_dt = end_dt + timedelta(days=1)

        time_interval = (end_dt - start_dt).seconds / 60 / block_length
        time_block_length = str(int(time_interval))
        if time_interval % 1 != 0:
            infoLog.warning('task bid: %s, start time: %s, end_time: %s, length not compatible with time interval %s, '
                            'give up the length num less than 1.', bid, start_time, end_time, str(block_length))
        new_tasks.append((bid, start_time, end_time, work_time, time_block_length))
    return new_tasks


def calculate_people_num(start_time: str, end_time: str, work_time: int) -> int:
    """
    计算工作需要的人力数
    :param start_time:
    :param end_time:
    :param work_time:
    :return:
    """
    start_dt = datetime.strptime(start_time, '%H:%M')
    end_dt = datetime.strptime(end_time, '%H:%M')
    if end_dt < start_dt:
        end_dt = end_dt + timedelta(days=1)
    work_length_minutes = int((end_dt - start_dt).seconds / 60)
    if work_time // work_length_minutes == work_time / work_length_minutes:
        # 能整除
        return work_time // work_length_minutes
    else:
        # 不能整除
        return work_time // work_length_minutes + 1


def calculate_minute_interval(start_time: str, end_time: str, is_cross_day: bool, fmt: str = '%H:%M') -> int:
    """
    计算两个HH:MM时间字符串的间隔分钟数
    :param is_cross_day:
    :param fmt:
    :param start_time:
    :param end_time:
    :return:
    """
    start_dt = datetime.strptime(start_time, fmt)
    end_dt = datetime.strptime(end_time, fmt)
    if not is_cross_day or end_dt > start_dt:
        return int((end_dt - start_dt).seconds / 60)
    else:
        return int((timedelta(days=1) + (end_dt - start_dt)).seconds / 60)


def time_string_formatter(time_str: str) -> str:
    """
    标准化time str 例如 8:00 -> 08:00
    :param time_str:
    :return:
    """
    return datetime.strptime(time_str, '%H:%M').strftime('%H:%M')


def have_tasks(line_item: List[str]) -> bool:
    """
    是否含有tasks
    :param line_item:
    :return:
    """
    for task in line_item:
        if task:
            return True
    return False


def test():
    """
    测试
    :return:
    """
    pass


if __name__ == '__main__':
    test()
