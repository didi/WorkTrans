#!/usr/bin/env python
# encoding: utf-8

"""
@author: pyd
@contact:
@file: special_event_service.py
@time: 2020/2/26
@desc:
"""

from typing import List

from utils.myLogger import infoLog
from specialEvent.model.special_event_model import SpecialEventModel


class SpecialEventService:

    @staticmethod
    def do_request(raw_data):
        save_result = {'code': 0, 'result': '未处理'}
        num_sum = 0
        err_info = ''
        cid: str = raw_data['cid']
        did: str = raw_data['did']
        opt: str = raw_data['opt']
        infoLog.info('opt=' + opt)
        data_arr: List[str] = raw_data['data']
        for data_obj in data_arr:
            success_one = False
            num_sum = num_sum + 1
            bid = data_obj['eventId'];
            if opt == 'delete':
                success_one = SpecialEventModel.soft_delete(bid, cid, did)
            elif opt == 'add':
                success_one = SpecialEventModel.insert_record(bid, cid, did,
                                                              data_obj['eventStart'], data_obj['eventEnd'],
                                                              data_obj['eventName'])
            elif opt == 'update':
                success_one = SpecialEventModel.update_record(bid, cid, did,
                                                              data_obj['eventStart'], data_obj['eventEnd'],
                                                              data_obj['eventName'])
            if not success_one:
                err_info = err_info + data_obj['eventId'] + ','
        if len(err_info) == 0:
            save_result = {'code': 100, 'result': str(num_sum) + '条数据' + opt + '操作成功'}
        else:
            save_result = {'code': 101, 'result': 'eventId=' + err_info + opt + 'db操作错误'}
        return save_result
