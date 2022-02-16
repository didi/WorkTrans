#!/usr/bin/env python
# encoding: utf-8

import numpy as np
import pandas as pd
import os
import random
from keras.models import Sequential, Model
from keras.layers import Dense
from keras.layers import LSTM, Input
from keras.layers import Dropout
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from utils.global_keys import *
from utils.myLogger import infoLog, tracebackLog
from config.pos_auto_conf import PosAutoConfig
from forecastPOS.algorithm.dnn_factory import DeepModel
import datetime
import json, re
from utils.dateUtils import Date2delta


class LstmForecast(DeepModel):
    def __init__(self, cid, did, pre_type):
        super(LstmForecast, self).__init__()

        self.cid = cid
        self.did = did
        self.pre_type = pre_type
        self.model_conf = PosAutoConfig.model_conf[self._name()]
        self.model = None
        self.model_path = os.path.join("models", str(self.cid) + "_" + str(self.did), 'lstm')
        print(self.model_path)
        self.model_name = "_".join([self._name(), self.pre_type])

        self.model_info_name = self._name() + "_model_info.txt"
        self._mode_config_path = os.path.join(self.model_path, self.model_info_name)
        self.mode_info = None
        self.Date2delta = Date2delta()

    @classmethod
    def _name(cls):
        return "lstm"

    def load_model(self):
        model_path = os.path.join(self.model_path, self.model_name + '.h5')
        if os.path.exists(model_path):
            self.model = load_model(model_path)
            with open(self._mode_config_path) as fh:
                self.mode_info = json.load(fh)
        else:
            tracebackLog.error("model_path:{} is not found".format(model_path))

    def create_input(self, dataset, period):
        X, y = [], []
        for i in range(len(dataset) - period - 1):
            X_vals = dataset[i:(i + period), 0]  # lag = 1至period
            y_val = dataset[i + period, 0]  # 当前值
            X.append(X_vals)
            y.append(y_val)
        X = np.array(X)
        X = np.reshape(X, (X.shape[0], 1, X.shape[1]))  # lstm输入要求是3d，根据此来reshape array
        y = np.array(y)
        return X, y

    def build_model(self):
        # 设置input 这个是手动配置,当前是配置的15分钟预测，一天是预测的96个
        input_lstm = Input(shape=(1, self.model_conf["req_days"] * self.model_conf["day_seq_len"]))
        lstm1 = LSTM(100)(input_lstm)
        dropout1 = Dropout(0.2)(lstm1)
        dense = Dense(1)(dropout1)
        return Model(input_lstm, dense)

    def train(self, message):
        """
        :param message:  DataFrame message ={"train": data}
        :return:
        """
        train_ = message["train"]
        train_ = train_[self.pre_type].tolist()
        if "test" in message:
            test_ = message["test"]
        else:
            train_ = train_[:int(len(train_) * 0.7)]
            test_ = train_[int(len(train_) * 0.7):]

        scaler = MinMaxScaler()
        train_ = np.array(train_).reshape(-1, 1)
        test_ = np.array(test_).reshape(-1, 1)
        scaler.fit(train_)  # 只通过训练集来训练scaler
        scale_ = scaler.scale_
        min_ = scaler.min_
        train_scaler = scaler.transform(train_)
        test_scaler = scaler.transform(test_)

        period = self.model_conf['req_days'] * self.model_conf["day_seq_len"]
        # period = 49
        X_train, y_train = self.create_input(train_scaler, period)
        X_test, y_test = self.create_input(test_scaler, period)

        model = self.build_model()
        model.compile(loss='mean_squared_error', optimizer='adam')
        print(model.summary())
        model.fit(X_train, y_train, epochs=self.model_conf["epochs"],
                  batch_size=self.model_conf["batch_size"], validation_data=(X_test, y_test), verbose=1,
                  shuffle=False)
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)
        model.save(os.path.join(self.model_path, self.model_name + ".h5"))
        save_model_info = {"scale_": scale_.tolist(), "min_": min_.tolist()}
        with open(self._mode_config_path, 'w') as fh:
            json.dump(save_model_info, fh, indent=2)

    def process(self, message):
        start_day = message['startPreDay']
        end_day = message['endPreDay']
        data = message['data']

        self.load_model()
        if not self.model:
            return None
        if len(start_day) < 16:
            start_day = start_day + " 00:00"
            end_day = end_day + " 00:00"
        pred_day = start_day
        res = {}
        while pred_day < end_day:
            data = np.array(data).reshape([1, 1, self.model_conf['req_days'] * self.model_conf["day_seq_len"]]).astype(
                np.float64)
            data_input = self.transform(data, self.mode_info["scale_"], self.mode_info["min_"])
            model_out = self.model.predict(data_input)
            model_out = self.inverse_transform(model_out, self.mode_info["scale_"], self.mode_info["min_"])
            res[pred_day] = 0 if model_out.tolist()[0][0] < 0 else model_out.tolist()[0][0]
            data = np.squeeze(data).tolist()[1:]
            data.append(res[pred_day])
            pred_day = datetime.datetime.strptime(pred_day, "%Y-%m-%d %H:%M") + datetime.timedelta(minutes=15)
            pred_day = pred_day.strftime("%Y-%m-%d %H:%M")
        return res
