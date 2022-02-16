#!/usr/bin/env python
# encoding: utf-8

"""
@author: pyd
@contact:
@file: special_event_scope_service.py
@time: 2020/2/26
@desc:
"""

from typing import List

from utils.myLogger import infoLog
from specialEvent.model.special_event_scope_model import SpecialEventScopeModel


class SpecialEventScopeService:

    @staticmethod
    def do_request(raw_data):
        save_result = {'code': 0, 'result': '未处理'}
        num_sum = 0
        err_info = ''
        cid: str = raw_data['cid']
        data_arr: List[str] = raw_data['eventScopeArr']
        for data_obj in data_arr:
            success_one = False
            num_sum = num_sum + 1
            opt: str = data_obj['opt']
            bid: str = data_obj['bid']
            if opt == 'delete':
                success_one = SpecialEventScopeModel.delete(bid, cid)
            elif opt == 'add':
                count = SpecialEventScopeModel.get_count(bid, cid)
                if count == 0:
                    success_one = SpecialEventScopeModel.insert_record(bid, cid, data_obj['eventBid'],
                                                                       data_obj['goodsBids'], data_obj['didArr'],
                                                                       data_obj['startDate'], data_obj['endDate'])
                else:
                    infoLog.info('add操作中bid+cid[' + bid + '+' + cid + ']重复，改为update')
                    success_one = SpecialEventScopeModel.update_record(bid, cid, data_obj['eventBid'],
                                                                       data_obj['goodsBids'], data_obj['didArr'],
                                                                       data_obj['startDate'], data_obj['endDate'])
            elif opt == 'update':
                count = SpecialEventScopeModel.get_count(bid, cid)
                if count == 0:
                    infoLog.info('update操作中bid+cid[' + bid + '+' + cid + ']不存在，改为add')
                    success_one = SpecialEventScopeModel.insert_record(bid, cid, data_obj['eventBid'],
                                                                       data_obj['goodsBids'], data_obj['didArr'],
                                                                       data_obj['startDate'], data_obj['endDate'])
                else:
                    success_one = SpecialEventScopeModel.update_record(bid, cid, data_obj['eventBid'],
                                                                       data_obj['goodsBids'], data_obj['didArr'],
                                                                       data_obj['startDate'], data_obj['endDate'])
            else:
                err_info = err_info + 'bid=' + bid + '：opt参数错误，opt只能为add，update或delete；'
                continue
            if not success_one:
                err_info = err_info + 'bid=' + bid + '：db操作错误；'
        if len(err_info) == 0:
            save_result = {'code': 100, 'result': str(num_sum) + '条数据操作成功'}
        else:
            save_result = {'code': 401, 'result': err_info[0:-1]}
        return save_result
