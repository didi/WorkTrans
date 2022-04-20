#!/usr/bin/env python
# encoding: utf-8

"""
@author: sunsong
@contact: sunsong@didiglobal.com
@file: forecastCls.py
@time: 2019-08-20 20:15
@desc:
"""
import json,datetime, time
from typing import Dict, Tuple
from labor.service.labor_db_service import LaborDbService
from utils.check_token import check_token
from utils.myLogger import infoLog


class ForecastMHandler_v2(RequestHandler):
    @gen.coroutine
    def post(self):
        starttime = datetime.datetime.now()
        req = self.request.body.decode('utf-8')
        infoLog.info('ForecastMHandler : %s' % (req.replace('\n', '')))

        s = datetime.datetime.now()
        code, notice = self.check_param(req)
        if code:
            save_result = {'code': 400 + code, 'result': notice}
            self.write(save_result)
            return

        raw_data: Dict = json.loads(self.request.body.decode('utf-8'))

        time_str = raw_data.get('timestr', '')
        token = raw_data.get('token', '')

        code, result = check_token(token, time_str)

        if code:
            # 如果code不是None, token验证出错
            result = {'code': code, 'result': result}
        else:
            cid = raw_data.get('cid', '')
            forecast_type = raw_data.get('forecastType', '')
            did_arr = raw_data.get('didArr', '')
            date_arr = raw_data.get('dateArr', [])
            data = yield LaborDbService.labor_standard_forecast_v2(cid, forecast_type, did_arr, date_arr)
            result = {'code': 100, 'result': "预测成功", 'data': data}

            # cid = raw_data.get('cid', '')
            # forecast_type = raw_data.get('forecastType', '')
            # forecast_date_start = raw_data.get('forecast_date_start', '')
            # forecast_date_end = raw_data.get('forecast_date_end', '')
            # did_arr = raw_data.get('didArr', '')
            # task_arr = raw_data.get('taskArr', [])
            # data = yield LaborDbService.labor_standard_forecast(cid, forecast_type, forecast_date_start,forecast_date_end, did_arr, task_arr)
            # result={'code': 100, 'result': "预测成功",'data':data}


        e = datetime.datetime.now()
        infoLog.info('RequestHandler...此次请求耗时%s' %(e-s))
        self.write(result)
        endtime = datetime.datetime.now()
        sec = str((endtime - starttime).microseconds)
        handler_name = 'ForecastMHandler'
        timestr = time.mktime(starttime.timetuple())
        infoLog.info('handler_name: %s, timestrs: %s, starttime: %s,  endtime: %s, endtime-starttime: %s ms', handler_name, str(timestr), str(starttime), str(endtime), sec)

    @staticmethod
    def check_param(input_json_string: str) -> Tuple[int, str]:
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

        if 'forecastType' not in raw_data or raw_data['forecastType'] not in ['0','1','2']:
            return 4, '未包含forecastType 或者 forecastType不为"0"或"1"或"2"'

        # if 'forecast_date_start' not in raw_data or 'forecast_date_end' not in raw_data:
        #     return 7, '未包含forecast_date_start 或者 forecast_date_end'

        # if raw_data['forecast_date_end'] < raw_data['forecast_date_start']:
        #     return 8, '请保证结束时间在开始时间之后'

        if 'didArr' not in raw_data or  (not isinstance(raw_data['didArr'], list)):
            return 9, '需要包含didArr，并且为list类型'

        if 'dateArr' not in raw_data or  (not isinstance(raw_data['dateArr'], list)):
            return 11, '需要包含dateArr，并且为list类型'

        if len(raw_data.get('dateArr',[]))==0 :
            return 14, 'dateArr必须不为空'

        for arr in raw_data.get('dateArr', ''):
            if 'dateTime' not in arr:
                return 7, '未包含dateTime'

            if 'taskArr' not in arr or (not isinstance(arr['taskArr'], list)):
                return 8, '需要包含taskArr，并且为list类型'

            # if len(arr.get('taskArr', [])) == 0:
            #     return 10, 'taskArr必须不为空'

            for dd in arr['taskArr']:
                if 'forecastStandard' not in dd or dd['forecastStandard'] not in ['order_num', 'turnover', 'peoples']:
                    return 5, 'forecastStandard 或者 forecastStandard不为[order_num或turnover或peoples]'

            flag = True
            for d in arr['taskArr']:
                if 'taskBid' not in d or 'laborStandardBid' not in d or 'taskTimeArr' not in d or 'forecastStandard' not in d:
                    flag = False
            if not flag:
                return 15, 'taskBid、laborStandardBid、taskTimeArr、forecastStandard必须在taskArr数据的每一个元素里'

        return 0, ''

