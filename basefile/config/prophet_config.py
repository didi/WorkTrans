#!/usr/bin/env python
# encoding: utf-8

"""
@author: sunsong
@contact: sunsong@didiglobal.com
@file: prophet_config.py
@time: 2019-08-07 23:38


@desc:
"""


class ProphetConfig(object):
    config_gmv = {
        'base_week': 4,
        'changepoint_prior_scale': 0.4,
        'changepoint_range': 0.9
    }

    config_people = {
        'base_week': 4,
        'changepoint_prior_scale': 0.4,
        'changepoint_range': 0.9
    }
