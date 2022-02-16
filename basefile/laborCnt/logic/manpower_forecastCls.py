#!/usr/bin/env python
# encoding: utf-8

"""
@author: sunsong
@contact: sunsong@didiglobal.com
@file: manpower_forecastCls.py
@time: 2019/9/16 7:54 下午
@desc:
"""

import json
from typing import Tuple, List, Dict, Any
from tornado.web import RequestHandler
import datetime, time
from utils.check_token import check_token
from utils.myLogger import infoLog
from laborCnt.service.manpower_forecast_service2 import ManPowerForecastService
from tornado import gen


class ManPowerForecastHandler(RequestHandler):

    @gen.coroutine
    def post(self):
        starttime = datetime.datetime.now()
        req = self.request.body.decode('utf-8')
        infoLog.info('ManPowerForecastHandler: %s', str(req).replace('\n', ''))

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
            cid: str = str(raw_data['cid'])
            bid: str = str(raw_data['forecastType'])
            timeInterval: int = int(raw_data['timeInterval'])
            did_arr: List[int] = raw_data['didArr']
            forecast_date_start: str = raw_data['forecastDateStart']
            forecast_date_end: str = raw_data['forecastDateEnd']
            shift_mod: List[Dict[str, Any]] = raw_data.get('shiftMod', [])
            combi_rule: List[Dict[str, Any]] = raw_data.get('combirule', [])
            shiftsplitrule: List[Dict[str, Any]] = raw_data.get('shiftsplitrule', [])
            save_method: int = raw_data.get('save_method', 1)
            infoLog.info('ManPowerForecastService.manpower_forecast doing...')

            # save_result_yy, flag_yy = ManPowerForecastService.manpower_forecast(cid, bid, timeInterval, did_arr,
            #                                                                     forecast_date_start, forecast_date_end,
            #                                                                     shift_mod, combi_rule, shiftsplitrule)
            # yyData = save_result_yy.get('data', {})
            # if save_result_yy['code'] == 0:
            #     save_result = {'code': 100, 'result': '操作成功', 'data': save_result_yy.get('data',{})}
            # elif save_result_yy['code'] == 1:
            #     save_result = {'code': 101, 'result': 'DB操作失败', 'data': ''}
            # else:
            #     save_result = {'code': 102, 'result': '未处理', 'data': ''}
            #
            # if flag_yy == 0:
            #     print('yy的排班数据存入数据库成功')
            # else:
            #     print('yy的排班数据存入数据库失败')

            save_result_ss = ManPowerForecastService.manpower_forecast(cid, bid, timeInterval, did_arr,
                                                                       forecast_date_start, forecast_date_end,
                                                                       shift_mod, combi_rule, shiftsplitrule,
                                                                       save_method)

            #ssData = save_result_ss.get('data', {})
            # yyData = save_result_yy.get('data', {})
            # save_result = {'code': 100, 'result': '成功', 'data': {'yyData': yyData, 'ssData': ssData}}
            #save_result = {'code': 100, 'result': '成功', 'data': ssData}
            save_result = save_result_ss
            # end = datetime.now()
            # print('总耗时：', (end - start).seconds)

        self.write(save_result)
        endtime = datetime.datetime.now()
        sec = str((endtime - starttime).microseconds)
        handler_name = 'ManPowerForecastHandler'
        timestr = time.mktime(starttime.timetuple())
        infoLog.info('handler_name: %s, timestrs: %s, starttime: %s,  endtime: %s, endtime-starttime: %s ms', handler_name, str(timestr), str(starttime), str(endtime), sec)

    @staticmethod
    def check_param(input_json_string: str) -> Tuple[int, str]:
        """
        参数检查
        :param input_json_string:
        :return:
        """
        try:
            raw_data = json.loads(input_json_string)
        except json.JSONDecodeError:
            return 1, 'json解析错误'

        if not isinstance(raw_data, dict):
            return 2, 'json格式错误'

        if 'timestr' not in raw_data or 'token' not in raw_data:
            return 3, '未包含token、timestr'
        elif (raw_data['timestr'] is None) or (raw_data['token'] is None):
            return 3,'timestr、token是必填字段，不能为空'

        if 'cid' not in raw_data or 'forecastType' not in raw_data or 'didArr' not in raw_data or 'forecastDateStart' not in \
                raw_data or 'forecastDateEnd' not in raw_data or 'shiftsplitrule' not in raw_data \
                or 'timeInterval' not in raw_data:
            return 3, '参数错误，需要包含cid, forecastType, didArr, forecastDateStart, forecastDateEnd, timeInterval'
        elif (raw_data['cid'] is None) or (raw_data['forecastType'] is None) or (raw_data['didArr'] is None) or(raw_data['forecastDateStart'] is None) or(raw_data['forecastDateEnd'] is None) or(raw_data['shiftsplitrule'] is None) or (raw_data['timeInterval'] is None):
            return 3,'cid, forecastType, didArr, forecastDateStart, forecastDateEnd, timeInterval是必填字段，不能为空'


        shift_split_rule = raw_data['shiftsplitrule']
        for item in shift_split_rule:
            if 'shiftsplitbid' not in item or 'didArr' not in item or 'shiftsplitData' not in item:
                return 3, '参数错误，shiftsplitrule需要包含shiftsplitbid, didArr, shiftsplitData'
            elif (item['shiftsplitbid'] is None) or (item['didArr'] is None) or (item['shiftsplitData'] is None):
                return 3,'shiftsplitbid, didArr, shiftsplitData是必填字段，不能为空'
            shift_split_data = item['shiftsplitData']
            for i in shift_split_data:
                if 'ruleCalType' not in i or 'ruleCpType' not in i or 'ruleCpNum' not in i or 'dayFusion' not in i:
                    return 3, '参数错误， shiftsplitData需要包含ruleCalType, ruleCpType, ruleCpNum, dayFusion'
                elif (i['ruleCalType'] is None) or (i['ruleCpType'] is None) or (i['ruleCpNum'] is None) or (i['dayFusion'] is None):
                    return 3, 'ruleCalType, ruleCpType, ruleCpNum, dayFusion是必填字段，不能为空'
                rule_cal_type = i['ruleCalType']
                if rule_cal_type != 'interval' and rule_cal_type != 'shiftNum' and rule_cal_type != 'shiftLen' and \
                rule_cal_type != 'worktime' and rule_cal_type != 'fillCoefficient' and rule_cal_type != 'taskCount':
                    return 3, '参数错误，ruleCalType需要为interval或shiftNum或shiftLen或worktime或taskCount或fillCoefficient'
                rule_cp_type = i['ruleCpType']
                if rule_cp_type != 'lt' and rule_cp_type != 'le' and rule_cp_type != 'eq' and rule_cp_type != 'ge' and \
                        rule_cp_type != 'gt':
                    return 3, '参数错误，ruleCpType需要为lt或le或eq或ge或gt'

        if 'shiftMod' in raw_data:
            shift_mod = raw_data['shiftMod']
            for item in shift_mod:
                if 'shiftModbid' not in item or 'didArr' not in item:
                    return 3, '参数错误，shiftMod需要包含shiftModbid， didArr'
                elif (item['shiftModbid'] is None) or (item['didArr'] is None):
                    return 3, 'shiftModbid， didArr是必填字段，不能为空'
                if 'shiftModData' in item:
                    shift_mod_data = item['shiftModData']
                    for i in shift_mod_data:
                        if 'shiftBid' not in i or 'shiftStart' not in i or 'shiftEnd' not in i or 'isCrossDay' not in i:
                            return 3, '参数错误，shiftModData需要包含shiftBid, shiftStart, shiftEnd, isCrossDay'
                        elif (i['shiftBid'] is None) or (i['shiftStart'] is None) or (i['shiftEnd'] is None) or (
                                i['isCrossDay'] is None):
                            return 3, 'shiftBid, shiftStart, shiftEnd, isCrossDay是必填字段，不能为空'

        if 'combirule' in raw_data:
            combi_rule = raw_data['combirule']
            if len(combi_rule) != 0:
                for item in combi_rule:
                    if 'combiruleBid' not in item or 'didArr' not in item:
                        return 3, '参数错误，combirule需要包含combiruleBid, didArr'
                    elif (item['combiruleBid'] is None) or (item['didArr'] is None):
                        return 3, 'combiruleBid， didArr是必填字段，不能为空'
                    if 'combiRuleData' in item:
                        combi_rule_data = item['combiRuleData']
                        for i in combi_rule_data:
                            if 'ruleData' not in i:
                                return 3, '参数错误，combiRuleData需要包含ruleData'
                            elif i['ruleData'] is None:
                                return 3, 'ruleData是必填字段，不能为空'

        return 0, ''
