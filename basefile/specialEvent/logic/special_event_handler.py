#!/usr/bin/env python
# encoding: utf-8

"""
@author: pyd
@contact:
@file: special_event_handler.py
@time: 2020/2/25
@desc:
"""
from abc import ABC

from tornado.web import RequestHandler
from typing import Tuple
import json

from utils.check_token import check_token
from utils.myLogger import infoLog
from specialEvent.service.special_event_service import SpecialEventService


class SpecialEventHandler(RequestHandler, ABC):

    def post(self):
        """
        特殊事件（测试）
        :return:
        """

        req = self.request.body.decode('utf-8')
        infoLog.info('SpecialEventHandler接口产生调用')
        infoLog.info('req: %s', str(req))

        code, notice = self.check_param(req)
        if code:
            save_result = {'code': 400 + code, 'result': notice}
            self.write(save_result)
            return

        raw_data = json.loads(self.request.body.decode('utf-8'))

        time_str = raw_data.get('timestr', '')
        token = raw_data.get('token', '')

        code, result = check_token(token, time_str)
        if code:
            save_result = {'code': code, 'result': result}
        else:
            save_result = SpecialEventService.do_request(raw_data)
        self.write(save_result)

    @staticmethod
    def check_param(input_json_string: str) -> Tuple[int, str]:
        try:
            raw_data = json.loads(input_json_string)
        except json.JSONDecodeError:
            return 1, 'json解析错误'

        if not isinstance(raw_data, dict):
            return 2, 'json格式错误'

        if 'timestr' not in raw_data or 'token' not in raw_data:
            return 3, '未包含token'

        if 'cid' not in raw_data or 'opt' not in raw_data:
            return 2, '参数错误，需要包含cid, opt'

        if raw_data.get("opt", "") not in ["update", "delete", "add"]:
            return 2, 'opt参数错误，需要为add,update或delete'

        if raw_data['opt'] == 'update' or raw_data['opt'] == 'add':
            if 'data' not in raw_data:
                return 2, '参数错误，opt为add或update时需要包含data'
            special_event_data = raw_data['data']
            for item in special_event_data:
                if 'eventStart' not in item or 'eventEnd' not in item or 'eventName' not in item \
                        or 'status' not in item:
                    return 2, '参数错误，data需要包含eventStart, eventEnd, eventName, status'
        return 0, ''
