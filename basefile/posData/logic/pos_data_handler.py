#!/usr/bin/env python
# encoding: utf-8

"""
@author: pyd
@contact:
@file: special_event_scope_handler.py
@time: 2020/2/28
@desc:
"""
from abc import ABC

from tornado.web import RequestHandler
from typing import Tuple
import json

from posData.service.pos_data_service import PosDataService
from utils.apiFilter import apiFilter
from utils.authenticated import authenticated
from utils.check_token import check_token
from utils.myLogger import infoLog
from utils.webResult import WebResult


class PosDataHandler(RequestHandler, ABC):

    def post(self, route, *args, **kwargs):
        """
        处理pos数据
        :return:
        """
        infoLog.info('handler name: %s; route: %s; request body: %s' %(str("PosDataHandler"), str(route),str(self.request.body.decode('utf-8')).replace('\n', '')))
        if route == "insert":
            self.write(self.insert())
        elif route == "select":
            self.write(self.select().__str__())
        else:
            self.write(WebResult.errorCode(404, "请求不存在").__str__())

    @authenticated(role=["滴滴", "喔趣"])
    def insert(self):
        req = self.request.body.decode('utf-8')
        infoLog.info('PosDataHandler接口产生调用')
        infoLog.info('req: %s', str(req))

        code, notice = self.check_param(req)
        if code:
            save_result = {'code': 400 + code, 'result': notice}
            return save_result

        raw_data = json.loads(self.request.body.decode('utf-8'))

        time_str = raw_data.get('timestr', '')
        token = raw_data.get('token', '')

        code, result = check_token(token, time_str)
        if code:
            save_result = {'code': code, 'result': result}
        else:
            save_result = PosDataService.do_request(raw_data)
        return save_result

    @apiFilter()
    def select(self):
        try:
            req = json.loads(self.request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return WebResult.errorResult("json 解析失败")
        cid = req.get("cid", None)
        did = req.get("did", None)
        start_date_time = req.get("startDateTime", None)
        end_date_time = req.get("endDateTime", None)
        order_no_arr = req.get("orderNoArr", None)
        return PosDataService.select(cid, did, start_date_time, end_date_time, order_no_arr)



    @staticmethod
    def check_param(input_json_string: str) -> Tuple[int, str]:
        try:
            raw_data = json.loads(input_json_string)
        except json.JSONDecodeError:
            return 1, 'json解析错误'

        if not isinstance(raw_data, dict):
            return 2, 'json格式错误'

        if 'cid' not in raw_data or 'data' not in raw_data:
            return 2, '参数错误，需要包含cid, data'

        if 'timestr' not in raw_data or 'token' not in raw_data:
            return 3, '未包含token'

        data_arr = raw_data['data']
        for item in data_arr:
            if 'did' not in item or 'gmtBill' not in item:
                return 2, '参数错误，data必须包含did，gmtBill'
            # if item['opt'] != 'update' and item['opt'] != 'delete' and item['opt'] != 'add':
            #    return 2, 'opt参数错误，需要为add,update或delete'
        return 0, ''
