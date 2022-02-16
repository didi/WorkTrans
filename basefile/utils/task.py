#!/usr/bin/env python
# encoding: utf-8

"""
@author: sunsong
@contact: sunsong@didiglobal.com
@file: task.py
@time: 2020/4/4 7:06 下午
@desc:
"""


class BaseTask(object):
    """
    任务基类
    """

    def __init__(self, bid: str, task_type: int, work_time: int):
        """
        初始化函数
        :param bid:
        :param task_type: 0-固定任务 1-直接任务 2-间接任务
        :param work_time: 工作时长 单位: min
        """
        super(BaseTask, self).__init__()

        self.bid = bid
        self.task_type = task_type
        self.work_time = work_time
        self.task_block_length = -1

    def calculate_task_block_length(self, block_length: int):
        """
        计算任务的格子数
        :param block_length:
        :return:
        """
        if self.work_time % block_length == 0:
            # 能整除
            self.task_block_length = self.work_time // block_length
        else:
            # 不能整除，增加一格
            self.task_block_length = self.work_time // block_length + 1


class FDTask(BaseTask):
    """
    固定或直接任务的基础类
    """

    def __init__(self, bid: str, task_type: int, start_time: str, end_time: str, work_time: int, fill_coef: float,
                 discard: bool, task_min_time: int, task_max_time: int):
        """
        初始化函数
        :param bid:
        :param task_type:
        :param work_time:
        :param start_time:
        :param end_time:
        :param fill_coef:
        :param discard:
        :param task_min_time:
        :param task_max_time:
        """
        super(FDTask, self).__init__(bid, task_type, work_time)

        self.start_time = start_time
        self.end_time = end_time
        self.fill_coef = fill_coef
        self.discard = discard
        self.task_min_time = task_min_time
        self.task_max_time = task_max_time

        self.is_cross_day = True if start_time > end_time else False


class FixedTask(FDTask):
    """
    固定任务
    """

    def __init__(self, bid: str, start_time: str, end_time: str, work_time: int, fill_coef: float, discard: bool,
                 task_min_time: int, task_max_time: int):
        """
        初始化函数
        :param bid:
        :param start_time:
        :param end_time:
        :param work_time:
        :param fill_coef:
        :param discard:
        :param task_min_time:
        :param task_max_time:
        """
        task_type: int = 0  # 固定任务
        super(FixedTask, self).__init__(bid, task_type, start_time, end_time, work_time, fill_coef, discard,
                                        task_min_time, task_max_time)


class DirectTask(FDTask):
    """
    直接任务
    """

    def __init__(self, bid: str, start_time: str, end_time: str, work_time: int, fill_coef: float, discard: bool,
                 task_min_time: int, task_max_time: int):
        """
        初始化函数
        :param bid:
        :param start_time:
        :param end_time:
        :param work_time:
        :param fill_coef:
        :param discard:
        :param task_min_time:
        :param task_max_time:
        """
        task_type: int = 1  # 直接任务
        super(DirectTask, self).__init__(bid, task_type, start_time, end_time, work_time, fill_coef, discard,
                                         task_min_time, task_max_time)


class InDirectTask(BaseTask):
    """
    间接任务
    """

    def __init__(self, bid: str, work_time: int):
        """
        初始化函数
        :param bid:
        :param work_time:
        """
        task_type: int = 2
        super(InDirectTask, self).__init__(bid, task_type, work_time)
