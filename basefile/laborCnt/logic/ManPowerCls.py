"""
@author: liyabin
@contact: liyabin_i@didiglobal.com
@file: ManPowerCls.py
@time: 2019-09-12 11:08
@desc:
"""
from utils.myLogger import infoLog
import datetime, time
from typing import Tuple, Dict, Any, List
import json
from utils.check_token import check_token
from laborCnt.service.man_power_service import ManPowerService


class ManPowerModifyHandler(RequestHandler):
    # 记录异常
    _reason = None

    @gen.coroutine
    def post(self):
        starttime = datetime.datetime.now()
        infoLog.info('ManPowerModifyHandler : %s' % (self.request.body.decode('utf-8')))

        code, notice = self.check_param(self.request.body.decode('utf-8'))

        if code:
            save_result = {'code': 400 + code, 'result': notice}
            self.write(save_result)
            return

        raw_data: Dict = json.loads(self.request.body.decode('utf-8'))

        time_str = raw_data.get('timestr', '')
        token = raw_data.get('token', '')

        code, result = check_token(token, time_str)
        if code:
            save_result = {'code': code, 'result': result}
        else:
            try:
                save_result = yield ManPowerService.doRequest(raw_data)
            except Exception as result:
                print(result)
                ManPowerModifyHandler._reason = str(result)

        self.write(save_result)
        endtime = datetime.datetime.now()
        sec = str((endtime - starttime).microseconds)
        handler_name = 'ManPowerModifyHandler'
        timestr = time.mktime(starttime.timetuple())
        infoLog.info('handler_name: %s, timestrs: %s, starttime: %s,  endtime: %s, endtime-starttime: %s ms',
                     handler_name, str(timestr), str(starttime), str(endtime), sec)

    def write_error(self, status_code, **kwargs):
        '''
        自定义错误代码返回
        :param status_code:
        :param kwargs:
        :return:
        '''
        if status_code == 500:
            self.write("<html><title> %(message)s</title>"
                       "<body> %(message)s</body></html>" % {
                           # "code": status_code,
                           "message": "ERROR: " + ManPowerModifyHandler._reason,
                       })
            self.finish()

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

        if 'cid' not in raw_data or 'forecastType' not in raw_data:
            return 2, '参数错误，需要包含cid, forecastType'

        if 'combiRuleData' not in raw_data:
            return 2, '参数错误，需要包含combiRuleData'
        combiRuleData = raw_data['combiRuleData']
        for item in combiRuleData:
            for key in item.keys():
                for forecast_shift_item in item[key]:
                    if 'combiRule' not in forecast_shift_item \
                            or 'combiRuleNewVal' not in forecast_shift_item \
                            or 'combiRuleOldVal' not in forecast_shift_item:
                        return 2, 'combiRuleData参数错误，需要包含forecase_date、combiRule, combiRuleNewVal, combiRuleOldVal'
        return 0, ''
