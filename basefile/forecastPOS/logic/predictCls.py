#!/usr/bin/env python
# encoding: utf-8

import tornado.web
import json
import traceback
import datetime
import time
from utils.myLogger import infoLog, tracebackLog
from utils.dateUtils import DateUtils
from utils.check_token import check_token
from tornado import gen
from forecastPOS.service.PosPredict import PosPredict


class PredictHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def post(self):
        start_time = datetime.datetime.now()

        predict_result = json.dumps({'code': 400, 'result': '烦请联系研发解决此异常'})

        try:
            param_str = self.request.body.decode('utf-8')
            infoLog.info('PredictHandler : %s' % (param_str.replace('\n', '')))

            code, notice = self.check_predict_param(param_str)
            predict_param = json.loads(param_str)
            if code == 0:
                predict_data = yield self.process(predict_param)
                predict_result = {'code': 100, 'result': 'success', 'predictParam': predict_param, 'data': predict_data}
            else:
                predict_result = {'code': 400 + code, 'result': '参数校验失败' + notice, 'predictParam': predict_param,
                                  'data': '{}'}

        except Exception:
            tracebackLog.error('traceback.format_exc():%s', traceback.format_exc())
        finally:
            infoLog.info('predict : %s', predict_result)
            self.write(json.dumps(predict_result))

            end_time = datetime.datetime.now()
            sec = str((end_time - start_time).microseconds)
            handler_name = 'PredictHandler'
            time_str = time.mktime(start_time.timetuple())
            infoLog.info('handler_name: %s, timestrs: %s, starttime: %s,  endtime: %s, endtime-starttime: %s ms',
                         handler_name, str(time_str), str(start_time), str(end_time), sec)

    def check_predict_param(cls, paramstr):
        """
        检验参数有效性
        :param paramstr: 参数
        :return:
        """
        try:
            raw_data = json.loads(paramstr)
        except json.JSONDecodeError:
            return 6, 'json解析错误'

        if not isinstance(raw_data, dict):
            return 7, 'json格式错误'

        if 'timestr' not in raw_data or 'token' not in raw_data:
            return 8, '未包含token'

        time_str = raw_data.get('timestr', '')
        token = raw_data.get('token', '')

        code, result = check_token(token, time_str)
        if code:
            return 9, 'token校验失败,检查是否合法或者是否超时等..'

        server_time = datetime.datetime.now()
        start_pre_day = raw_data.get('startDay', time_str)[0:10]
        end_pre_day = raw_data.get('endDay', DateUtils.nDatesAgo(start_pre_day, raw_data.get('dayCount', 7)))
        predict_len = (datetime.datetime.strptime(end_pre_day, "%Y-%m-%d") - server_time).seconds

        if predict_len >= 30 * 24 * 3600:
            return 7, '请不要预测超过今天30天的数据'

        clent_time = datetime.datetime.strptime(str(time_str), "%Y-%m-%d %H:%M:%S.%f")
        gap = server_time - clent_time if server_time >= clent_time else clent_time - server_time
        time_check = gap.seconds
        if time_check >= 1800 or time_check <= -1800:
            return 5, '非法请求'

        try:
            if isinstance(raw_data, dict):
                pks = raw_data.keys()
                if ("token" in pks) and ("timestr" in pks) and ("predictType" in pks) and ("did" in pks) and (
                        "startDay" in pks) and ("endDay" in pks) and ("preType" in pks):
                    if raw_data.get('preType') in ['trueGMV', 'truePeoples', 'trueOrders']:
                        if raw_data.get('endDay') >= raw_data.get('startDay'):
                            return 0, '参数检验合格'
                    else:
                        return 2, '查询类型错误，trueGMV ， truePeoples ， trueOrders'
                else:
                    return 3, '缺少必传参数 token,timestr,predictType,did,startDay,endDay,preType'
            else:
                return 4, '字典转换错误'
        except Exception:
            return 5, '参数校验失败'

    @gen.coroutine
    def process(self, params):
        pos = PosPredict()
        res = pos.process(params)
        return res
