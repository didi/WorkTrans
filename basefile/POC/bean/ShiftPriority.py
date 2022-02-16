"""
@author: lidan
@time: 2020-07-02

"""

from typing import List

class ShiftPriority:


    @staticmethod
    def init_shift_priority(comb_tasks_list:List,tasks_priority_list:List):
        """
        通过任务列表的序号，给出包含班次的列表的优先级

        :param comb_tasks_list:List 由任务构成的班次列表
        :param tasks_priority_list:List settings里设置的任务优先级
        :return: comb_tasks_list_with_priority : 考虑任务优先级之后的班次列表
        """
        comb_tasks_list_high_priority = []
        comb_tasks_list_low_priority = []

        for inx, comb_task in enumerate(comb_tasks_list):
            set_priority = False
            for comb_task_name in comb_task.taskName_list:
                for i in tasks_priority_list:  # 优先级要求的关键字
                    if comb_task_name.find(i) >= 0:
                        set_priority = True
            if set_priority:
                    comb_tasks_list_high_priority.append(comb_task)
            else:
                comb_tasks_list_low_priority.append(comb_task)

        comb_tasks_list_with_priority = comb_tasks_list_high_priority+comb_tasks_list_low_priority

        return comb_tasks_list_with_priority
