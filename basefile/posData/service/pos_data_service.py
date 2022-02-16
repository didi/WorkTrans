#!/usr/bin/env python
# encoding: utf-8

"""
@author: pyd
@contact:
@file: special_event_scope_service.py
@time: 2020/2/28
@desc:
"""

from typing import List

from utils.collectionUtils import CollectionUtils
from utils.dateUtils import DateUtils
from utils.myLogger import infoLog
from posData.model.pos_data_model import PosDataModel
from utils.webResult import WebResult


class PosDataService:

    @staticmethod
    def do_request(raw_data):
        save_result = {'code': 0, 'result': '未处理'}
        num_sum = 0
        err_info = ''
        cid: str = raw_data['cid']
        data_arr: List[str] = raw_data['data']
        for data in data_arr:
            now_time = DateUtils.get_now_datetime_str()
            num_sum = num_sum + 1
            bill_year = data['gmtBill'][0:4]
            bill_month = data['gmtBill'][5:7]
            bill_day = data['gmtBill'][8:10]
            bill_hour = data['gmtBill'][11:13]
            bill_minute = data['gmtBill'][14:16]
            order_no = ''
            if 'orderNo' in data:
                order_no = data['orderNo']
            count = PosDataModel.get_count(cid, data['did'], data['gmtBill'], order_no)
            if count == 0:  # 新增
                success_one = PosDataModel.insert_record(cid, data['did'], data['gmtBill'], data['gmtTurnover'],
                                                         data['money'], None, bill_year, bill_month,
                                                         bill_day, bill_hour, bill_minute, data['peoples'],
                                                         order_no, data['singleSales'], data['payment'],
                                                         data['deviceCode'], now_time, now_time, None,
                                                         data['transactionNum'], data['commodityCode'])
            else:  # 更新
                success_one = PosDataModel.update_record(cid, data['did'], data['gmtBill'], data['gmtTurnover'],
                                                         data['money'], None, bill_year, bill_month,
                                                         bill_day, bill_hour, bill_minute, data['peoples'],
                                                         order_no, data['singleSales'], data['payment'],
                                                         data['deviceCode'], now_time, now_time, None,
                                                         data['transactionNum'], data['commodityCode'])
                infoLog.info('更新%s条数据', count)
            if not success_one:
                err_info = err_info + data['commodity_code'] + '：db操作错误；'
        if len(err_info) == 0:
            save_result = {'code': 100, 'result': str(num_sum) + '条数据操作成功'}
        else:
            save_result = {'code': 101, 'result': err_info[0:-1]}
        return save_result

    @classmethod
    def select(cls, cid: str, did: int, startDateTime: str, endDateTime: str, orderNoArr: List[str]):

        if cid is None or len(cid) < 1 or did is None or len(did) < 1 or startDateTime is None or endDateTime is None:
            return WebResult.errorCode(400, "cid, did, startDateTime, endDateTime 必填")

        _startDateTime = DateUtils.transTime(startDateTime, "%Y-%m-%d %H:%M:%S")

        if _startDateTime is None:
            return WebResult.errorCode(400, "startDateTime 格式不正确， yyyy-MM-dd hh:mm:ss")
        _endDateTime = DateUtils.transTime(startDateTime, "%Y-%m-%d %H:%M:%S")
        if _endDateTime is None:
            return WebResult.errorCode(400, "endDateTime 格式不正确， yyyy-MM-dd hh:mm:ss")

        result = PosDataModel.select(cid, did, startDateTime, endDateTime, orderNoArr)

        if result is None:
            return WebResult.errorCode(400, "未成功获取数据")

        if len(result) < 1:
            return WebResult.successResult("无数据")

        return cls.transData(result)

    @classmethod
    def transData(cls, result):
        """
        :param result:
        :return:
        """
        returnResult = []
        for item in result:
            if item is None:
                continue

            returnResult.append({
                "cid": item.get("cid", None),
                "did": item.get("did", None),
                "gmtBill": item.get("gmt_bill", None),
                "gmtTurnover": item.get("gmt_trunover", None),
                "money": item.get("money", None),
                "transactionNum": item.get("transaction_num", None),
                "peoples": item.get("peoples", None),
                "singleSales": item.get("singleSales", None),
                "commodityCode": item.get("commodity_code", None),
                "payment": item.get("payment", None),
                "deviceCode": item.get("deviceCode", None),
                "orderNo": item.get("order_no", None)
            })
        return WebResult.successData(returnResult)



