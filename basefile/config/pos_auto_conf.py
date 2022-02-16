#!/usr/bin/env python
# encoding: utf-8

"""
@author: shenzihan
@contact: shenzihan@didichuxing.com
@file: pos_auto_conf.py
@time: 2019-10-28 15:38


@desc:
"""


class PosAutoConfig(object):
    config_coffDict = {
        # deepDict
        'truegmv_deepDict_6': [11, 1],
        'truegmv_deepDict_14': [13, 1],
        'truegmv_deepDict_15': [4, 1],
        'truegmv_deepDict_16': [37, 1],
        'truegmv_deepDict_44': [10, 1],
        'truegmv_deepDict_47': [8, 1],
        'truegmv_deepDict_48': [22, 1],
        'truegmv_deepDict_49': [37, 1],
        'truegmv_deepDict_50': [36, 1],
        'truegmv_deepDict_51': [51, 1],
        'truegmv_deepDict_53': [51, 1],
        'truegmv_deepDict_57': [51, 1],
        'truegmv_deepDict_52': [4, 1],
        'truegmv_deepDict_58': [25, 1],

        'truepeoples_deepDict_6': [19, 1],
        'truepeoples_deepDict_14': [29, 1],
        'truepeoples_deepDict_15': [28, 1],
        'truepeoples_deepDict_16': [13, 1],
        'truepeoples_deepDict_44': [9, 1],
        'truepeoples_deepDict_47': [13, 1],
        'truepeoples_deepDict_48': [10, 1],
        'truepeoples_deepDict_49': [41, 1],
        'truepeoples_deepDict_50': [44, 1],
        'truepeoples_deepDict_51': [1, 1],
        'truepeoples_deepDict_53': [1, 1],
        'truepeoples_deepDict_57': [1, 1],
        'truepeoples_deepDict_52': [13, 1],
        'truepeoples_deepDict_58': [38, 1],

        'trueorders_deepDict_6': [7, 1],
        'trueorders_deepDict_14': [25, 1],
        'trueorders_deepDict_15': [22, 1],
        'trueorders_deepDict_16': [3, 1],
        'trueorders_deepDict_44': [5, 1],
        'trueorders_deepDict_47': [53, 1],
        'trueorders_deepDict_48': [20, 1],
        'trueorders_deepDict_49': [28, 1],
        'trueorders_deepDict_50': [12, 1],
        'trueorders_deepDict_51': [1, 1],
        'trueorders_deepDict_53': [1, 1],
        'trueorders_deepDict_57': [1, 1],
        'trueorders_deepDict_52': [18, 1],
        'trueorders_deepDict_58': [22, 1],

        # prophetDict
        'truegmv_prophetDict_6': [4, 1],
        'truegmv_prophetDict_14': [30, 1],
        'truegmv_prophetDict_15': [32, 1],
        'truegmv_prophetDict_16': [30, 1],
        'truegmv_prophetDict_44': [11, 1],
        'truegmv_prophetDict_47': [13, 1],
        'truegmv_prophetDict_48': [18, 1],
        'truegmv_prophetDict_49': [39, 1],
        'truegmv_prophetDict_50': [38, 1],
        'truegmv_prophetDict_51': [2, 1],
        'truegmv_prophetDict_53': [2, 1],
        'truegmv_prophetDict_57': [2, 1],
        'truegmv_prophetDict_52': [24, 1],
        'truegmv_prophetDict_58': [32, 1],

        'truepeoples_prophetDict_6': [18, 1],
        'truepeoples_prophetDict_14': [7, 1],
        'truepeoples_prophetDict_15': [29, 1],
        'truepeoples_prophetDict_16': [18, 1],
        'truepeoples_prophetDict_44': [22, 1],
        'truepeoples_prophetDict_47': [9, 1],
        'truepeoples_prophetDict_48': [35, 1],
        'truepeoples_prophetDict_49': [42, 1],
        'truepeoples_prophetDict_50': [6, 1],
        'truepeoples_prophetDict_51': [2, 1],
        'truepeoples_prophetDict_53': [2, 1],
        'truepeoples_prophetDict_57': [2, 1],
        'truepeoples_prophetDict_52': [11, 1],
        'truepeoples_prophetDict_58': [28, 1],

        'trueorders_prophetDict_6': [8, 1],
        'trueorders_prophetDict_14': [24, 1],
        'trueorders_prophetDict_15': [18, 1],
        'trueorders_prophetDict_16': [4, 1],
        'trueorders_prophetDict_44': [21, 1],
        'trueorders_prophetDict_47': [54, 1],
        'trueorders_prophetDict_48': [17, 1],
        'trueorders_prophetDict_49': [44, 1],
        'trueorders_prophetDict_50': [22, 1],
        'trueorders_prophetDict_51': [2, 1],
        'trueorders_prophetDict_53': [2, 1],
        'trueorders_prophetDict_57': [2, 1],
        'trueorders_prophetDict_52': [42, 1],
        'trueorders_prophetDict_58': [48, 1],

        # seq2seqDict
        'truegmv_seq2seqDict_6': [19, 1],
        'truegmv_seq2seqDict_14': [31, 1],
        'truegmv_seq2seqDict_15': [33, 1],
        'truegmv_seq2seqDict_16': [33, 1],
        'truegmv_seq2seqDict_44': [33, 1],
        'truegmv_seq2seqDict_47': [3, 1],
        'truegmv_seq2seqDict_48': [16, 1],
        'truegmv_seq2seqDict_49': [17, 1],
        'truegmv_seq2seqDict_50': [39, 1],
        'truegmv_seq2seqDict_51': [3, 1],
        'truegmv_seq2seqDict_53': [3, 1],
        'truegmv_seq2seqDict_57': [3, 1],
        'truegmv_seq2seqDict_52': [27, 1],
        'truegmv_seq2seqDict_58': [33, 1],

        'truepeoples_seq2seqDict_6': [20, 1],
        'truepeoples_seq2seqDict_14': [30, 1],
        'truepeoples_seq2seqDict_15': [31, 1],
        'truepeoples_seq2seqDict_16': [36, 1],
        'truepeoples_seq2seqDict_44': [5, 1],
        'truepeoples_seq2seqDict_47': [12, 1],
        'truepeoples_seq2seqDict_48': [8, 1],
        'truepeoples_seq2seqDict_49': [43, 1],
        'truepeoples_seq2seqDict_50': [43, 1],
        'truepeoples_seq2seqDict_51': [3, 1],
        'truepeoples_seq2seqDict_53': [3, 1],
        'truepeoples_seq2seqDict_57': [3, 1],
        'truepeoples_seq2seqDict_52': [10, 1],
        'truepeoples_seq2seqDict_58': [34, 1],

        'trueorders_seq2seqDict_6': [19, 1],
        'trueorders_seq2seqDict_14': [26, 1],
        'trueorders_seq2seqDict_15': [21, 1],
        'trueorders_seq2seqDict_16': [16, 1],
        'trueorders_seq2seqDict_44': [10, 1],
        'trueorders_seq2seqDict_47': [45, 1],
        'trueorders_seq2seqDict_48': [21, 1],
        'trueorders_seq2seqDict_49': [47, 1],
        'trueorders_seq2seqDict_50': [23, 1],
        'trueorders_seq2seqDict_51': [3, 1],
        'trueorders_seq2seqDict_53': [3, 1],
        'trueorders_seq2seqDict_57': [3, 1],
        'trueorders_seq2seqDict_52': [17, 1],
        'trueorders_seq2seqDict_58': [52, 1]

    }
    model_conf = {
        "lstm": {
            "req_days": 7,
            "pred_type": "15T",
            "day_seq_len": 96,
            "epochs": 1,
            "batch_size": 64
        },
        "seq2seq": {
            "req_days": 3,
            "out_seq": 7,
            "day_seq_len": 24,  # 这个是根据pred_type来设定的，一天需要分成多少个预测值
            "pred_type": "1H",
            "decode_length": 1,  # decode的长度是天级别的
            "dim_hidden": 128,  # 隐含层的纬度
            "epochs": 1,
            "batch_size": 64
        }
    }
    prophet_config = {
        "trueGMV": {
            'base_week': 4,
            'changepoint_prior_scale': 0.4,
            'changepoint_range': 0.9,
            'pred_type': "15T"
        },
        "truePeoples": {
            'base_week': 4,
            'changepoint_prior_scale': 0.4,
            'changepoint_range': 0.9,
            'pred_type': "15T"
        },
        "trueOrders": {
            'base_week': 4,
            'changepoint_prior_scale': 0.4,
            'changepoint_range': 0.9,
            'pred_type': "15T"
        }
    }

    # 配置客户-门店，及其需训练的模型、模型类型等
    train_conf = {
        # 319西少爷，735喜茶，799屈臣氏
        '50000319': {'62': {'model_name': ['lstm', 'seq2seq', 'prophet'],
                            'preType': ['truegmv', 'truepeoples', 'trueorders'],
                            'history': 0, 'min_datanums': 30 * 96}},
        '50000735': {'12': {'model_name': ['lstm', 'seq2seq', 'prophet'],
                            'preType': ['truegmv', 'truepeoples', 'trueorders'],
                            'history': 0, 'min_datanums': 30 * 96},
                     '22': {'model_name': ['lstm', 'seq2seq', 'prophet'],
                            'preType': ['truegmv', 'truepeoples', 'trueorders'],
                            'history': 0, 'min_datanums': 30 * 96}
                     },
        '50000799': {'14': {'model_name': ['lstm', 'seq2seq', 'prophet'],
                            'preType': ['trueorders'],
                            'history': 762, 'min_datanums': 30 * 96}}
    }
