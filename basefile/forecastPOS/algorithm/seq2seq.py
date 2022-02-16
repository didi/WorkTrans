#!/usr/bin/env python
# encoding: utf-8

import numpy as np
import pandas as pd
import os
from keras.models import Model
from keras.layers import Dense
from keras.layers import LSTM, Input
from keras.models import load_model
from config.pos_auto_conf import PosAutoConfig
import datetime
import json
from forecastPOS.algorithm.dnn_factory import DeepModel
from utils.myLogger import tracebackLog


class seq2seqForecast(DeepModel):
    def __init__(self, cid, did, pre_type):
        super(seq2seqForecast, self).__init__()

        self.cid = cid
        self.did = did
        self.pre_type = pre_type
        self.model_conf = PosAutoConfig.model_conf[self._name()]
        self.encode, self.decode = None, None
        self.model_path = os.path.join("models", str(self.cid) + "_" + str(self.did), 'seq2seq')
        self.model_name = "_".join([self._name(), self.pre_type])

        self.model_info_name = self._name() + "model_info.txt"
        self._mode_config_path = os.path.join(self.model_path, self.model_info_name)
        self.model_info = None

    @classmethod
    def _name(cls):
        return "seq2seq"

    def load_model(self):
        encode_path = os.path.join(self.model_path, self.model_name + '_encoder.h5')
        decode_path = os.path.join(self.model_path, self.model_name + '_decoder.h5')
        if os.path.exists(encode_path) and os.path.exists(decode_path):
            self.encode = load_model(encode_path)
            self.decode = load_model(decode_path)
            with open(self._mode_config_path) as fh:
                self.model_info = json.load(fh)
        else:
            tracebackLog.error(
                "encode_model_path:{} or decode_model_path:{} is not found".format(encode_path, decode_path))

    def create_input(self, dataset, encode_length, decode_length):
        X, y = [], []
        for i in range(len(dataset) - encode_length - decode_length + 1):
            X_vals = dataset[i:(i + encode_length)]  # lag = 1至period
            y_val = dataset[i + encode_length:i + encode_length + decode_length]  # decode
            X.append(X_vals)
            y.append(y_val)
        X = np.array(X)
        X = np.reshape(X, (X.shape[0], encode_length, 1))  # lstm输入要求是3d，根据此来reshape array
        y = np.array(y)
        y = np.reshape(y, (y.shape[0], decode_length, 1))
        return X, y

    def build_model(self):
        encoder_input = Input(shape=(None, 1))
        encoder = LSTM(self.model_conf["dim_hidden"], return_state=True)
        encoder_output, encoder_h, encoder_c = encoder(encoder_input)
        encoded_state = [encoder_h, encoder_c]
        # 训练decoder
        decoder_input = Input(shape=(None, 1))
        decoder = LSTM(self.model_conf["dim_hidden"], return_sequences=True, return_state=True)
        decoder_output, _, _ = decoder(decoder_input, initial_state=encoded_state)

        dense_f1 = Dense(64, activation='tanh')
        dense1 = dense_f1(decoder_output)
        dense_f2 = Dense(1)
        output = dense_f2(dense1)

        # 训练模型
        model = Model([encoder_input, decoder_input], output)

        # 预测encoder
        infer_encoder = Model(encoder_input, encoded_state)

        # 预测decoder
        infer_init_h = Input(shape=(self.model_conf["dim_hidden"],))
        infer_init_c = Input(shape=(self.model_conf["dim_hidden"],))
        infer_init_state = [infer_init_h, infer_init_c]
        infer_output, infer_h, infer_c = decoder(decoder_input, initial_state=infer_init_state)
        infer_state = [infer_h, infer_c]
        infer_outputs = dense_f2(dense_f1(infer_output))
        infer_decoder = Model([decoder_input] + infer_init_state, [infer_outputs] + infer_state)

        return model, infer_encoder, infer_decoder

    def gen_decode_input(self, input_sequence, output_sequence):
        input_sequence = np.array(input_sequence)
        output_sequence = np.array(output_sequence)
        output_sequence = output_sequence.reshape((output_sequence.shape[0], output_sequence.shape[1], 1))
        decoder_input = np.concatenate((input_sequence[:, -1:, :], output_sequence[:, :-1, :]), axis=1)
        return decoder_input

    def train(self, message):
        train_ = message["train"]
        train_ = train_[self.pre_type].tolist()
        if "test" in message:
            test_ = message["test"][self.pre_type].tolist()
        else:
            train_ = train_[:int(len(train_) * 0.7)]
            test_ = train_[int(len(train_) * 0.7):]

        mean = np.mean(train_)
        std = np.std(train_)

        # scaler = MinMaxScaler()
        # train_ = np.array(train_).reshape(-1, 1)
        # test_ = np.array(test_).reshape(-1, 1)
        # scaler.fit(train_)  # 只通过训练集来训练scaler
        # scale_ = scaler.scale_
        # min_ = scaler.min_
        # train_scaler = scaler.transform(train_)
        # test_scaler = scaler.transform(test_)

        train_scaler = (train_ - mean) / std
        test_scaler = (test_ - mean) / std
        encode_length = self.model_conf['req_days'] * self.model_conf["day_seq_len"]
        decode_length = self.model_conf["decode_length"] * self.model_conf["day_seq_len"]

        X_train, y_train = self.create_input(train_scaler, encode_length, decode_length)
        X_test, y_test = self.create_input(test_scaler, encode_length, decode_length)

        model, encoder, decoder = self.build_model()
        decoder_input_train = self.gen_decode_input(X_train, y_train)
        decoder_input_test = self.gen_decode_input(X_test, y_test)
        model.compile(loss='mean_squared_error', optimizer='adam')

        model.fit([X_train, decoder_input_train], y_train, epochs=self.model_conf["epochs"],
                  batch_size=self.model_conf["batch_size"], validation_data=([X_test, decoder_input_test], y_test),
                  verbose=1,
                  shuffle=False)

        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)
        encoder.save(os.path.join(self.model_path, self.model_name + "_encoder.h5"))
        decoder.save(os.path.join(self.model_path, self.model_name + "_decoder.h5"))

        save_model_info = {"mean": mean.tolist(), "std": std.tolist()}
        with open(self._mode_config_path, 'w') as fh:
            json.dump(save_model_info, fh, indent=2)

    def decode1day(self, input_sequence, decode_date_now):
        decode_date_last = datetime.datetime.strptime(decode_date_now, '%Y-%m-%d %H:%M') + datetime.timedelta(days=1)
        date_series = pd.date_range(start=decode_date_now, end=decode_date_last,
                                    freq=self.model_conf['pred_type']).tolist()
        date_series = [k.strftime("%Y-%m-%d %H:%M") for k in date_series]
        out_list = []
        encoded_state = self.encode.predict(input_sequence)
        decoder_input = np.reshape(input_sequence[0, -1, 0], [1, 1, 1])

        decode_length = self.model_conf['day_seq_len']  # 一天长度

        for _ in range(decode_length):
            decoder_output, decoded_h, decoded_c = self.decode.predict([decoder_input] + encoded_state)
            encoded_state = [decoded_h, decoded_c]
            decoder_input = decoder_output
            transform_output = (decoder_output * self.model_info['std'] + self.model_info['mean']).reshape([1])[0]
            out_list.append(transform_output if transform_output > 0 else 0)
        out_list = np.array(out_list).flatten().tolist()
        out_dict = {k: v for k, v in zip(date_series, out_list)}
        return out_dict, out_list

    def process(self, message):
        start_day = message['startPreDay']
        end_day = message['endPreDay']
        data = message['data']

        self.load_model()
        if not self.encode or not self.decode:
            return None
        if len(start_day) < 16:
            start_day = start_day + " 00:00"
            end_day = end_day + " 00:00"

        pred_day = start_day
        res = {}
        while pred_day < end_day:
            data = np.array(data).reshape([1, self.model_conf['req_days'] * self.model_conf["day_seq_len"], 1])
            data_input = (data - self.model_info['mean']) / self.model_info['std']
            model_out, out_list = self.decode1day(data_input, pred_day)
            res.update(model_out)
            data = data.flatten().tolist() + out_list
            data = data[len(out_list):]
            pred_day = datetime.datetime.strptime(pred_day, "%Y-%m-%d %H:%M") + datetime.timedelta(days=1)
            pred_day = pred_day.strftime("%Y-%m-%d %H:%M")
        print(res)
        return res
