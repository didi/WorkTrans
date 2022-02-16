#!/usr/bin/env python
# encoding: utf-8

import tornado
import json
import traceback
import datetime
import time
from utils.md5Token import Token
from forecastPOS.service.posDBService import PosDBService
from utils.myLogger import infoLog, tracebackLog
from tornado import gen


class ModifyHandler1(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self):
        starttime = datetime.datetime.now()
        try:
            infoLog.info('POSModifyHandler : %s' % (self.request.body.decode('utf-8').replace('\n', '')))
            raw_data = json.loads(self.request.body.decode('utf-8'))

            time_str = raw_data.get('timestr', '1900-01-01 00:00:00.123')
            token = raw_data.get('token', '1900null')
            server_token = Token().getToken(time_str)

            infoLog.info('ModifyHandler token:%s, server_token:%s' % (token, server_token))

            clent_time = datetime.datetime.strptime(str(time_str), "%Y-%m-%d %H:%M:%S.%f")
            server_time = datetime.datetime.now()

            gap = server_time - clent_time if server_time >= clent_time else clent_time - server_time
            time_check = gap.seconds
            s = datetime.datetime.now()
            save_result = {'code': 400, 'result': '未知异常'}
            if time_check >= 1800 or time_check <= -1800:
                save_result = {'code': 405, 'result': '非法请求'}
            else:
                if token != server_token:
                    save_result = {'code': 408, 'result': 'token校验失败，非法请求'}
                    infoLog.info('ModifyHandler : %s', save_result)
                else:
                    infoLog.info('ModifyHandler raw_data:%s' % raw_data)
                    save_result = yield PosDBService.modifyData1(raw_data)  # 执行数据存储

            e = datetime.datetime.now()
            infoLog.info('POS 单条请求响应时间: ' + time_str + '  ' + str((e - s).seconds))
            self.write(save_result)
        except Exception:
            infoLog.info('traceback.format_exc():%s', save_result)
            tracebackLog.error('traceback.format_exc():%s', traceback.format_exc())
            self.write(save_result)
            end_time = datetime.datetime.now()
            sec = str((end_time - starttime).microseconds)
            handler_name = 'ModifyHandler1'
            time_str = time.mktime(starttime.timetuple())
            infoLog.info('handler_name: %s, timestrs: %s, starttime: %s,  endtime: %s, endtime-starttime: %s ms',
                         handler_name, str(time_str), str(starttime), str(end_time), sec)
