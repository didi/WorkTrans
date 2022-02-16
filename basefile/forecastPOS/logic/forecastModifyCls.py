#!/usr/bin/env python
# encoding: utf-8

import tornado
import json
import datetime
import time
from utils.md5Token import Token
from forecastPOS.service.posDBService import PosDBService
import traceback
from utils.myLogger import infoLog, tracebackLog
from tornado import gen


class ForecastModifyHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def post(self):
        start_time = datetime.datetime.now()
        req = self.request.body.decode('utf-8')
        infoLog.info('ForecastModifyHandler : %s' % (req.replace('\n', '')))
        code, notice = self.check_param(req)
        if code:
            save_result = {'code': 400 + code, 'result': notice}
            self.write(save_result)
            return
        try:
            params = json.loads(self.request.body.decode('utf-8'))
            #  token校验
            time_str = params.get('timestr', '')
            token = params.get('token', '')

            server_token = Token().getToken(time_str)

            infoLog.info('ForecastModifyHandler token:%s, server_token:%s' % (token, server_token))

            client_time = datetime.datetime.strptime(str(time_str), "%Y-%m-%d %H:%M:%S.%f")
            server_time = datetime.datetime.now()

            gap = server_time - client_time if server_time >= client_time else client_time - server_time
            time_check = gap.seconds
            infoLog.info('ForecastModifyHandler timeCheck: %s %s %d %f', server_time, client_time, time_check,
                         time_check / 60)

            save_result = {'code': 400, 'result': '未知异常'}
            if time_check >= 1800 or time_check <= -1800:
                save_result = {'code': 405, 'result': '非法请求'}
                infoLog.info('ForecastModifyHandler timeCheck: %d', time_check)
                self.write(save_result)
            else:
                if token != server_token:
                    save_result = {'code': 408, 'result': 'token校验失败，非法请求'}
                    infoLog.info('ForecastModifyHandler: %s', save_result)
                else:
                    infoLog.info('ForecastModifyHandler params: %s' % params)
                    save_result = yield PosDBService.modifyForecast(params)

        except Exception:
            infoLog.info('traceback.format_exc():%s', save_result)
            tracebackLog.error('traceback.format_exc():%s', traceback.format_exc())
        finally:
            self.write(save_result)
            self.finish()
        endtime = datetime.datetime.now()
        sec = str((endtime - start_time).microseconds)
        handler_name = 'ForecastModifyHandler'
        timestr = time.mktime(start_time.timetuple())
        infoLog.info('handler_name: %s, timestrs: %s, starttime: %s,  endtime: %s, endtime-starttime: %s ms',
                     handler_name, str(timestr), str(start_time), str(endtime), sec)

    def check_param(cls, input_json_string):
        """
        验证参数合法性
        :param input_json_string:
        :return: （code, result）code 0 为合法 其余为不合法
        """
        try:
            raw_data = json.loads(input_json_string)
        except json.JSONDecodeError:
            return 1, 'json解析错误'

        if not isinstance(raw_data, dict):
            return 2, 'json格式错误'

        if 'timestr' not in raw_data or 'token' not in raw_data:
            return 3, '未包含token'

        if not ('cid' in raw_data and 'didArr' in raw_data and 'changedDataArr' in raw_data):
            return 4, '未包含 cid 或 didArr 或 changedDataArr'

        if not (isinstance(raw_data['didArr'], list) and isinstance(raw_data['changedDataArr'], list)):
            return 5, 'didArr 或 changedDataArr不是数组'

        for d in raw_data['changedDataArr']:
            if not (
                    "forecastDate" in d and "startTimeStr" in d and "endTimeStr" in d and "forecastType" in d
                    and "forecastPosValue" in d and "changedPosValue" in d):
                return 6, 'changedDataArr 必须包含[forecastDate、startTimeStr、endTimeStr、forecastType、' \
                          'forecastPosValue、changedPosValue]'

            if d['forecastType'] not in ['trueGMV', 'truePeoples', 'trueOrders']:
                return 7, 'forecastType 必须在trueGMV、truePeoples、trueOrders三个值之间'

        return 0, ''
