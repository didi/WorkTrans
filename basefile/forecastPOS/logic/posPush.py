#!/usr/bin/env python
# encoding: utf-8

import json
import datetime
from utils.md5Token import Token
from utils.myLogger import infoLog, tracebackLog
from concurrent.futures import ThreadPoolExecutor
from utils.mysql_pool import DBpool
import time
from forecastPOS.service.PosProcessDB import PosDB_process
from utils.global_keys import *

dbpool = DBpool()


class PosPushHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(POS_THREAD_NUM)

    @gen.coroutine
    def post(self):
        infoLog.info("pos_query_input")
        try:
            infoLog.info('POSModifyHandler : %s' % (self.request.body.decode('utf-8').replace('\n', '')))
            raw_data = json.loads(self.request.body.decode('utf-8'))
            start_time = time.time()
            save_result = self.check_param(raw_data)
            if save_result['code'] == 100:
                save_result = yield self.process(raw_data)
            batch_id = raw_data.get('batchId', "0")
            serial_number = raw_data.get('serialNumber', "0")
            infoLog.info('trace_id:{}_{} pos_data_process_time_cost:{} result:{}'.format(batch_id, serial_number,
                                                                                         time.time() - start_time,
                                                                                         save_result))
        except Exception as e:
            tracebackLog.error('POS_SERVER_ERROR:input={}'.format(self.request.body))
            tracebackLog.error(e)
            save_result = {'code': 400, 'result': '未知异常'}
        self.write(save_result)

    def check_param(self, raw_data):
        time_str = raw_data.get('timestr', '1900-01-01 00:00:00.123')
        token = raw_data.get('token', '1900null')
        server_token = Token().getToken(time_str)

        infoLog.info('ModifyHandler token:%s, server_token:%s' % (token, server_token))

        clent_time = datetime.datetime.strptime(str(time_str), "%Y-%m-%d %H:%M:%S.%f")
        server_time = datetime.datetime.now()

        gap = server_time - clent_time if server_time >= clent_time else clent_time - server_time
        time_check = gap.seconds
        save_result = {'code': 100}
        if time_check >= 1800 or time_check <= -1800:
            save_result = {'code': 405, 'result': '非法请求'}
        elif token != server_token:
            save_result = {'code': 408, 'result': 'token校验失败，非法请求'}
        return save_result

    @run_on_executor
    def process(self, raw_data):
        pos_process = PosDB_process(dbpool)
        res = pos_process.process(raw_data)
        return res
