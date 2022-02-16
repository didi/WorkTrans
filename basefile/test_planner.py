#!/usr/bin/env python
# encoding: utf-8

"""
@author: sunsong
@contact: sunsong@didiglobal.com
@file: test_planner.py
@time: 2019/10/11 6:53 下午
@desc:
"""

from datetime import datetime
import pandas as pd

from laborCnt.model.manpower_forecast_db import ManPowerForecastDB
from laborCnt.algorithm.manpower_planner import Planner

if __name__ == '__main__':

    fixed_tasks, direct_tasks, indirect_tasks = ManPowerForecastDB.get_task_info('123456', '6', '2019-07-12')

    combine_rules = [
        '201903291236061290061007959f0209,201903291236116910111007959f0210',
        '201903291248510440511007959f0216,201903291236271250271007959f0211',
        '201903291241363910361007959f0212,201903291236271250271007959f0211',
        '201903291250295220291007959f0217,201903291241432550431007959f0213,201903291244342970341007959f0215',
        '201903291244342970341007959f0215,201903291241563630561007959f0214'
    ]
    work_time_rules = [
        ('lt', 8 * 60, False)
    ]
    interval_rules = [
        ('lt', 120, False)
    ]
    shift_num_rules = [
        ('lt', 4, False)
    ]
    time1 = datetime.now()
    planner = Planner('05:30', '22:00', 15, fixed_tasks, direct_tasks, indirect_tasks, combine_rules,
                      False, interval_rules, work_time_rules, shift_num_rules)
    print('planner used ' + str((datetime.now() - time1).seconds) + ' seconds.')

    pd.DataFrame(planner.matrix).to_csv('out.csv')
