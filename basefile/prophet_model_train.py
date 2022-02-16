#!/usr/bin/env python
# encoding: utf-8

"""
@author: sunsong
@contact: sunsong@didiglobal.com
@file: prophet_model_train.py
@time: 2019-08-09 14:49
@desc:
"""

from forecastPOS.algorithm.prophet import ProphetTrain
from config.prophet_config import ProphetConfig
from utils.dateUtils import DateUtils
import pandas as pd
from forecastPOS.service.posDBService import PosDBService


def prophet_model_train_and_save(cid: int, did: int, preType: str, end_base_day: str):
    """
    模型训练与存储
    :param cid:
    :param did:
    :param preType:
    :return:
    """
    if preType == 'trueGmv':
        config = ProphetConfig.config_gmv
    else:
        config = ProphetConfig.config_people

    base_week = config['base_week']

    startBaseDay = DateUtils.nDatesAgo(end_base_day, base_week * 7)
    startBaseDaySeq = pd.date_range(start=startBaseDay, end=end_base_day, freq='15min').tolist()
    startBaseDayKey = list(map(lambda x: str(x)[0:16], startBaseDaySeq))

    startBaseDayKey = startBaseDayKey[0:-1]
    # modified by caoyabin
    historyPosData = PosDBService.getHistoryPosData(did, startBaseDay, end_base_day, preType, cid)
    history_np = PosDBService.getBasePos(did, startBaseDay, end_base_day, preType, base_week, 7, {}, cid, historyPosData). \
        reshape(len(startBaseDayKey), 1).T

    history_df = pd.DataFrame()
    history_df['ds'] = pd.Series(startBaseDayKey)
    history_df['y'] = pd.Series(history_np[0])

    ProphetTrain(cid, did, preType, history_df, config)


if __name__ == '__main__':
    # end_day_str = DateUtils.get_yesterday_date_str()
    end_day_str = '2018-07-24'

    pre_type_list = ['trueGmv', 'truePeoples']
    cid_list = [0]
    did_list = [6]

    for preType in pre_type_list:
        for cid in cid_list:
            for did in did_list:
                prophet_model_train_and_save(cid, did, preType, end_day_str)
