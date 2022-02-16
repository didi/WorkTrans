#!/usr/bin/env python
# encoding: utf-8

"""
@author: sunsong
@contact: sunsong@didiglobal.com
@file: prophet.py
@time: 2019-08-07 17:37
@desc:
"""

import pandas as pd
from fbprophet import Prophet
import pickle
import os
from forecastPOS.algorithm.dnn_factory import DeepModel
from config.pos_auto_conf import PosAutoConfig
from utils.myLogger import tracebackLog


class ProphetForecast(DeepModel):
    def __init__(self, cid, did, pre_type):
        super(ProphetForecast, self).__init__()

        self.cid = cid
        self.did = did
        self.pre_type = pre_type
        self.model_conf = PosAutoConfig.prophet_config[pre_type]
        self.model = None
        self.model_path = os.path.join("models", str(self.cid) + "_" + str(self.did), 'prophet')
        self.model_name = "_".join([self._name(), self.pre_type])

        self.model_info_name = self._name() + "_model_info.txt"
        self._mode_config_path = os.path.join(self.model_path, self.model_info_name)

    @classmethod
    def _name(cls):
        return "prophet"

    def load_model(self):
        model_path = os.path.join(self.model_path, self.model_name + '.pkl')
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
        else:
            tracebackLog.error("model_path:{} is not found".format(model_path))

    def train(self, message):
        data = message["train"]
        df = pd.DataFrame({"ds": data.index.tolist(),
                           "y": data[self.pre_type].tolist()})
        print(self.model_conf)
        model = Prophet(changepoint_prior_scale=self.model_conf['changepoint_prior_scale'],
                        changepoint_range=self.model_conf['changepoint_range'])
        model.fit(df)
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)
        with open(os.path.join(self.model_path, self.model_name + '.pkl'), "wb") as fh:
            pickle.dump(model, fh)

    def process(self, message):
        self.load_model()
        if not self.model:
            return None

        res_type = message["res_type"]
        start_pre_day = message["startPreDay"]
        end_pre_day = message["endPreDay"]
        start_pre_day_seq = pd.date_range(start=start_pre_day, end=end_pre_day,
                                          freq=self.model_conf['pred_type']).tolist()
        start_pre_day_key = list(map(lambda x: str(x)[0:16], start_pre_day_seq))
        start_pre_day_key = start_pre_day_key[0:-1]
        pre_df = pd.DataFrame()
        pre_df['ds'] = pd.Series(start_pre_day_key)

        model_res = self.model.predict(pre_df)
        if res_type == 1:
            result = list(model_res['yhat_upper'])
        elif res_type == 2:
            result = list(model_res['yhat_lower'])
        else:
            result = list(model_res['yhat'])
        pre_res = [i if i >= 0 else 0.0 for i in result]
        prophet_dict = {}
        for i, key in enumerate(start_pre_day_key):
            prophet_dict[key] = pre_res[i]
        return prophet_dict
