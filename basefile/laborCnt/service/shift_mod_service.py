#!/usr/bin/env python
# encoding: utf-8

"""
@author: sunsong
@contact: sunsong@didiglobal.com
@file: shift_mod_service.py
@time: 2019/9/10 11:54 上午
@desc:
"""

from datetime import datetime
from typing import List

from laborCnt.model.shift_mod_data import ShiftModData
from utils.myLogger import infoLog
from tornado import gen


class ShiftModService:

    @staticmethod
    def delete_shift_mod_data_record_level_first(bid: str, cid: str, did_arr: List[int]) -> bool:
        """
        外层删除
        :param did_arr:
        :param bid:
        :param cid:
        :return:
        """

        res = True
        log_time1 = datetime.now()
        for did in did_arr:
            res = ShiftModData.soft_delete_record_level_first(bid, cid, str(did))
        log_time2 = datetime.now()
        infoLog.info('外层删除耗时: ' + str(log_time2 - log_time1))
        return res

    @staticmethod
    def delete_shift_mod_data_record_level_second(bid: str, cid: str, did_arr: List[int], shiftbid: str) -> bool:
        """
        内层删除
        :param bid:
        :param cid:
        :param did_arr:
        :param shiftbid:
        :return:
        """
        res = True
        log_time1 = datetime.now()
        for did in did_arr:
            res = ShiftModData.soft_delete_record_level_second(bid, cid, str(did), shiftbid)
        log_time2 = datetime.now()
        infoLog.info('内层删除耗时: ' + str(log_time2 - log_time1))
        return res

    @staticmethod
    @gen.coroutine
    def doRequest(raw_data):
        save_result = {'code': 0, 'result': '未处理'}
        cid: str = raw_data['cid']
        bid: str = raw_data['bid']
        opt: str = raw_data['opt']
        did_arr: List[int] = raw_data['didArr']

        if opt == 'delete':
            res = ShiftModService.delete_shift_mod_data_record_level_first(bid, cid, did_arr)
            if res:
                save_result = {'code': 100, 'result': '删除成功'}
            else:
                save_result = {'code': 101, 'result': '删除失败'}
        else:
            shift_mod_data = raw_data['shiftModData']
            res = True
            for item in shift_mod_data:
                shift_bid: str = item['shiftBid']
                opt2: str = item['opt']
                shift_start: str = item['shiftStart']
                shift_end: str = item['shiftEnd']
                is_cross_day = item['isCrossDay']
                if is_cross_day:
                    is_cross_day = True
                else:
                    is_cross_day = False

                if opt2 == 'delete':
                    res = ShiftModService.delete_shift_mod_data_record_level_second(bid, cid, did_arr, shift_bid)
                else:
                    res = ShiftModService.update_shift_mod_data_record(bid, cid, did_arr, shift_bid, shift_start,
                                                                       shift_end, is_cross_day)
            if res:
                save_result = {'code': 100, 'result': '操作成功'}
            else:
                save_result = {'code': 101, 'result': 'DB操作失败'}
        raise gen.Return(save_result)

    @staticmethod
    def update_shift_mod_data_record(bid: str, cid: str, did_arr: List[int], shiftbid: str, shift_start: str,
                                     shift_end: str, is_cross_day: bool) -> bool:
        """
        修改
        :param bid:
        :param cid:
        :param did_arr:
        :param shiftbid:
        :param shift_start:
        :param shift_end:
        :param is_cross_day:
        :return:
        """
        res = True
        log_time1 = datetime.now()
        for did in did_arr:
            res = ShiftModData.update_record(bid, cid, str(did), shiftbid, shift_start, shift_end, is_cross_day)
        log_time2 = datetime.now()
        infoLog.info('ShiftModService Update耗时: ' + str(log_time2 - log_time1))
        return res



if __name__ == '__main__':
    raw_data={
    	"token": "25fbf56f70df2b74976317b7de508e4c", "timestr": "2019-09-10 17:29:31.148680",
    	"cid": "123456",
    	"bid": "201903291241563630561001235D025d",
    	"opt": "update",
    	"didArr": [6],
    	"shiftModData": [{
    		"shiftBid": "201903291241563630561001235f0215",
    		"opt": "update",
    		"shiftStart": "14:00",
    		"shiftEnd": "19:00",
    		"isCrossDay": False
    	}, {
    		"shiftBid": "201903291241563630561001234f0214",
    		"shiftStart": "20:00",
    		"opt": "delete",
    		"shiftEnd": "03:00",
    		"isCrossDay": True
    	}]
    }
    ShiftModService.doRequest(raw_data)

