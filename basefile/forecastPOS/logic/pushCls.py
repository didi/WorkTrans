#!/usr/bin/env python
# encoding: utf-8

import json
import datetime
from utils.md5Token import Token
from forecastPOS.service.posDBService import PosDBService
import traceback
from utils.myLogger import infoLog, tracebackLog


def prn_obj(obj):
    print('\n'.join(['%s:%s' % item for item in obj.__dict__.items()]))


class PushHandler(tornado.web.RequestHandler):
    def post(self):

        try:
            raw_data = json.loads(self.request.body.decode('utf-8'))
            infoLog.info('PushHandler raw_data:%s' % raw_data)

            timestr = raw_data.get('timestr', '')
            token = raw_data.get('token', '')

            server_token = Token().getToken(timestr)

            infoLog.info('PushHandler token:%s, server_token:%s' % (token, server_token))

            clent_time = datetime.datetime.strptime(str(timestr), "%Y-%m-%d %H:%M:%S.%f")
            server_time = datetime.datetime.now()

            gap = server_time - clent_time if server_time >= clent_time else clent_time - server_time
            time_check = gap.seconds
            infoLog.info('PushHandler  timeCheck:%s   %s %d %f', server_time, clent_time, time_check, time_check / 60)

            if time_check >= 1800 or time_check <= -1800:
                save_result = {'code': 405, 'result': '非法请求'}
            else:
                if token != server_token:
                    save_result = {'code': 408, 'result': 'token校验失败，非法请求'}
                    infoLog.info('PushHandler token != server_token  : %s', save_result)
                else:
                    save_result = PosDBService.pushData(raw_data)
                    infoLog.info('PushHandler predictResult  : %s', save_result)
        except Exception:
            infoLog.info('traceback.format_exc():%s', save_result)
            tracebackLog.error('traceback.format_exc():%s', traceback.format_exc())
        finally:
            self.write(save_result)
