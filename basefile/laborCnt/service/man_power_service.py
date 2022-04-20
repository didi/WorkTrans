"""
@author: liyabin
@contact: liyabin_i@didiglobal.com
@file: man_power_service.py
@time: 2019-09-12 11:51
@desc:
"""

from datetime import datetime
from typing import List

from laborCnt.algorithm.manpower_planner import Planner
from laborCnt.model.man_power_db import ManPowerDB
from laborCnt.model.manpower_forecast_db import ManPowerForecastDB
from utils.myLogger import infoLog
import asyncio


class ManPowerService:
    @staticmethod
    def doRequest2(raw_data):
        cid: str = raw_data['cid']
        bid: str = raw_data['bid']
        combiRuleData = raw_data['combiRuleData']
        res = True
        for item in combiRuleData:
            combiRule: str = item['combiRule']
            combiRuleNewVal: str = item['combiRuleNewVal']
            combiRuleOldVal: str = item['combiRuleNewVal']

            res = ManPowerService.update_man_power_record(cid, bid, combiRule, combiRuleNewVal, combiRuleOldVal)

        if res:
            save_result = {'code': 100, 'result': '操作成功'}
        else:
            save_result = {'code': 101, 'result': 'DB操作失败'}

        return save_result

    @staticmethod
    @gen.coroutine
    def doRequest(raw_data):
        cid: str = str(raw_data.get('cid', ''))
        bid: str = raw_data.get('forecastType', '')
        did: str = raw_data.get('did', '')
        combiRuleData = raw_data.get('combiRuleData', '')

        error_message: List[str] = []
        res = True
        for item in combiRuleData:
            # key 为预测时间 例如：2019-07-12
            for key in item.keys():
                if len(item[key]) == 0:
                    continue
                else:
                    for forecast_shift_item in item[key]:
                        combiRule: str = forecast_shift_item.get('combiRule', ',')
                        combiRuleNewVal: str = forecast_shift_item.get('combiRuleNewVal', '')
                        combiRuleOldVal: str = forecast_shift_item.get('combiRuleOldVal', '')

                        res = ManPowerService.update_man_power_record(cid, bid, key, combiRule, combiRuleNewVal,
                                                                      combiRuleOldVal)
                        if not res:
                            error_message.append('日期：' + str(key) + '修改失败，数据库update失败。')

                    start_time, end_time, task_matrix = ManPowerForecastDB.get_matrix_info(cid, did, bid, key)

                    if not start_time or not end_time or not task_matrix:
                        infoLog.error('日期：%s 修改失败，数据库内没有存储原有矩阵信息。', str(key))
                        error_message.append('日期：' + str(key) + '修改失败，数据库内没有存储原有矩阵信息。')
                        save_result = {'code': 101, 'result': 'DB部分操作失败，详情：' + '; '.join(error_message)}
                        raise gen.Return(save_result)

                    # 如果修改范围超过了原有矩阵范围
                    new_start_time = ''
                    new_end_time = ''
                    is_cross_day = False if start_time < end_time else True
                    flag = False

                    for forecast_shift_item in item[key]:
                        for detail in forecast_shift_item['detail']:
                            detail_start_time = detail['start']
                            detail_end_time = detail['end']
                            if detail_start_time == '24:00':
                                detail_start_time = '00:00'
                            if detail_end_time == '24:00':
                                detail_end_time = '00:00'

                            if not new_start_time and not new_end_time:
                                new_start_time = detail_start_time
                                new_end_time = detail_end_time
                            else:
                                if conv_dt(detail_start_time) < conv_dt(end_time) and not is_cross_day:
                                    if conv_dt(detail_start_time) < conv_dt(new_start_time):
                                        new_start_time = detail_start_time
                                else:
                                    if not is_cross_day:
                                        is_cross_day = True
                                        flag = True
                                    if conv_dt(detail_start_time) > conv_dt(end_time) > conv_dt(new_start_time):
                                        new_start_time = detail_start_time
                                    elif conv_dt(detail_start_time) < conv_dt(new_start_time) < conv_dt(end_time):
                                        new_start_time = detail_start_time
                                    elif conv_dt(detail_start_time) < conv_dt(new_start_time) and not flag:
                                        new_start_time = detail_start_time

                                if conv_dt(detail_end_time) > conv_dt(start_time) and not is_cross_day:
                                    if conv_dt(detail_end_time) > conv_dt(new_end_time):
                                        new_end_time = detail_end_time
                                else:
                                    if not is_cross_day:
                                        is_cross_day = True
                                        flag = True
                                    if conv_dt(new_end_time) > conv_dt(start_time) > conv_dt(detail_end_time):
                                        new_end_time = detail_end_time
                                    elif conv_dt(start_time) > conv_dt(detail_end_time) > conv_dt(new_end_time):
                                        new_end_time = detail_end_time
                                    elif conv_dt(detail_end_time) > conv_dt(new_end_time) and not flag:
                                        new_end_time = detail_end_time

                    planner = Planner.construct_planner(start_time, end_time, task_matrix)

                    start_expand = False
                    start_shrink = False
                    if new_start_time:
                        if new_start_time > start_time and new_start_time > end_time:
                            start_expand = True
                        if new_start_time < start_time and new_start_time < end_time < start_time:
                            start_shrink = True
                    end_expand = False
                    end_shrink = False
                    if new_end_time:
                        if new_end_time < end_time and new_end_time < start_time:
                            end_expand = True
                        if new_end_time > end_time and end_time < start_time < new_end_time:
                            end_shrink = True

                    if new_start_time or new_end_time:
                        if start_time != new_start_time or end_time != new_end_time:
                            if not new_start_time:
                                new_start_time = start_time
                            if not new_end_time:
                                new_end_time = end_time
                            if new_start_time < start_time and not start_shrink or start_expand:
                                planner.expand_matrix(new_start_time, end_time, is_cross_day)
                            if new_end_time > end_time and not end_shrink or end_expand:
                                planner.expand_matrix(start_time, new_end_time, is_cross_day)
                            if new_start_time < start_time and not start_expand or start_shrink:
                                planner.shrink_matrix(new_start_time, end_time, is_cross_day)
                            if new_end_time < end_time and not end_expand or end_shrink:
                                planner.shrink_matrix(start_time, new_end_time, is_cross_day)
                    planner.modify_matrix_by_api(item[key])
                    ManPowerForecastDB.insert_matrix_ss(cid, did, bid, 'full', key, new_start_time, new_end_time,
                                                        planner.get_full_matrix())
                    infoLog.info('日期：%s 修改储存成功。')

        if res:
            save_result = {'code': 100, 'result': '操作成功'}
        else:
            save_result = {'code': 101, 'result': 'DB部分操作失败，详情：' + '; '.join(error_message)}

        raise gen.Return(save_result)

    @staticmethod
    def update_man_power_record(cid: str, bid: str, forecast_date: str, combiRule: str, combiRuleNewVal: str,
                                combiRuleOldVal: str) -> bool:
        s = datetime.now()
        res = ManPowerDB.update_man_power_record(cid, bid, forecast_date, combiRule, combiRuleNewVal, combiRuleOldVal)
        e = datetime.now()
        infoLog.info('ManPowerService Update耗时: ' + str(e - s))
        return res

    @staticmethod
    def delete_man_power_record(cid: str, bid: str):
        s = datetime.now()
        res = ManPowerDB.delete_man_power_record(cid, bid)
        e = datetime.now()
        infoLog.info('ManPowerService Delete耗时: ' + str(e - s))
        return res


def conv_dt(time_str: str, fmt='%H:%M') -> datetime:
    """
    转化时间
    :param time_str:
    :param fmt:
    :return:
    """
    res = datetime.strptime(time_str, fmt)
    return res


if __name__ == '__main__':
    data = {
        "forecastType": 0,
        "combiRuleData": [
            {
                "2020-02-10": [
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "10:30",
                                "taskType": "fixedwh",
                                "end": "13:30",
                                "taskId": "202004210940473541404040e0000056"
                            },
                            {
                                "start": "17:00",
                                "taskType": "directwh",
                                "end": "23:00",
                                "taskId": "202004210941479521404040e0000060"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060,202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "4",
                        "detail": [
                            {
                                "start": "11:30",
                                "taskType": "fixedwh",
                                "end": "14:30",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "10:30",
                                "taskType": "fixedwh",
                                "end": "13:30",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "5",
                        "detail": [
                            {
                                "start": "10:30",
                                "taskType": "directwh",
                                "end": "13:30",
                                "taskId": "202004210941479521404040e0000060"
                            },
                            {
                                "start": "19:00",
                                "taskType": "fixedwh",
                                "end": "23:00",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060,202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "06:00",
                                "taskType": "fixedwh",
                                "end": "11:00",
                                "taskId": "202004210940473541404040e0000056"
                            },
                            {
                                "start": "13:30",
                                "taskType": "directwh",
                                "end": "20:00",
                                "taskId": "202004210941479521404040e0000060"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060,202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "10:30",
                                "taskType": "directwh",
                                "end": "13:30",
                                "taskId": "202004210941479521404040e0000060"
                            },
                            {
                                "start": "17:00",
                                "taskType": "fixedwh",
                                "end": "20:00",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060,202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "06:00",
                                "taskType": "directwh",
                                "end": "13:30",
                                "taskId": "202004210941479521404040e0000060"
                            },
                            {
                                "start": "14:30",
                                "taskType": "fixedwh",
                                "end": "18:00",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060,202004210940473541404040e0000056"
                    }
                ]
            },
            {
                "2020-02-11": [
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "06:00",
                                "taskType": "fixedwh",
                                "end": "11:00",
                                "taskId": "202004210940473541404040e0000056"
                            },
                            {
                                "start": "13:30",
                                "taskType": "directwh",
                                "end": "16:30",
                                "taskId": "202004210941479521404040e0000060"
                            },
                            {
                                "start": "17:30",
                                "taskType": "fixedwh",
                                "end": "21:30",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060,202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "10:30",
                                "taskType": "directwh",
                                "end": "16:30",
                                "taskId": "202004210942484551404040e0000073"
                            },
                            {
                                "start": "17:30",
                                "taskType": "directwh",
                                "end": "23:00",
                                "taskId": "202004210941479521404040e0000060"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060,202004210942484551404040e0000073"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "11:30",
                                "taskType": "fixedwh",
                                "end": "14:30",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "06:00",
                                "taskType": "directwh",
                                "end": "13:30",
                                "taskId": "202004210941479521404040e0000060"
                            },
                            {
                                "start": "14:30",
                                "taskType": "fixedwh",
                                "end": "17:30",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060,202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "10:30",
                                "taskType": "directwh",
                                "end": "13:30",
                                "taskId": "202004210941479521404040e0000060"
                            },
                            {
                                "start": "15:30",
                                "taskType": "directwh",
                                "end": "18:30",
                                "taskId": "202004210941479521404040e0000060"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "10:30",
                                "taskType": "fixedwh",
                                "end": "13:30",
                                "taskId": "202004210940473541404040e0000056"
                            },
                            {
                                "start": "15:30",
                                "taskType": "directwh",
                                "end": "18:30",
                                "taskId": "202004210942484551404040e0000073"
                            }
                        ],
                        "combiRule": "202004210942484551404040e0000073,202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "10:30",
                                "taskType": "directwh",
                                "end": "13:30",
                                "taskId": "202004210942484551404040e0000073"
                            },
                            {
                                "start": "17:30",
                                "taskType": "directwh",
                                "end": "22:30",
                                "taskId": "202004210942484551404040e0000073"
                            }
                        ],
                        "combiRule": "202004210942484551404040e0000073,202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "10:30",
                                "taskType": "directwh",
                                "end": "13:30",
                                "taskId": "202004210941479521404040e0000060"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "10:30",
                                "taskType": "fixedwh",
                                "end": "13:30",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "06:00",
                                "taskType": "directwh",
                                "end": "13:30",
                                "taskId": "202004210942484551404040e0000073"
                            },
                            {
                                "start": "15:30",
                                "taskType": "fixedwh",
                                "end": "18:30",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210942484551404040e0000073,202004210940473541404040e0000056"
                    }
                ]
            },
            {
                "2020-02-12": [
                    {
                        "combiRuleOldVal": "0",
                        "combiRuleNewVal": "0",
                        "detail": [
                            {
                                "start": "06:00",
                                "taskType": "fixedwh",
                                "end": "13:00",
                                "taskId": "202004210940473541404040e0000056"
                            },
                            {
                                "start": "15:30",
                                "taskType": "fixedwh",
                                "end": "20:30",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "0",
                        "combiRuleNewVal": "0",
                        "detail": [
                            {
                                "start": "06:00",
                                "taskType": "directwh",
                                "end": "13:00",
                                "taskId": "202004210941479521404040e0000060"
                            },
                            {
                                "start": "15:30",
                                "taskType": "directwh",
                                "end": "20:30",
                                "taskId": "202004210941479521404040e0000060"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060"
                    },
                    {
                        "combiRuleOldVal": "0",
                        "combiRuleNewVal": "0",
                        "detail": [
                            {
                                "start": "12:30",
                                "taskType": "fixedwh",
                                "end": "15:30",
                                "taskId": "202004210940473541404040e0000056"
                            },
                            {
                                "start": "18:00",
                                "taskType": "fixedwh",
                                "end": "23:00",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "0",
                        "combiRuleNewVal": "0",
                        "detail": [
                            {
                                "start": "12:30",
                                "taskType": "directwh",
                                "end": "15:30",
                                "taskId": "202004210941479521404040e0000060"
                            },
                            {
                                "start": "18:00",
                                "taskType": "directwh",
                                "end": "23:00",
                                "taskId": "202004210941479521404040e0000060"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "10:00",
                                "taskType": "directwh",
                                "end": "13:00",
                                "taskId": "202004210941479521404040e0000060"
                            },
                            {
                                "start": "16:00",
                                "taskType": "directwh",
                                "end": "19:00",
                                "taskId": "202004210941479521404040e0000060"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060"
                    },
                    {
                        "combiRuleOldVal": "0",
                        "combiRuleNewVal": "0",
                        "detail": [
                            {
                                "start": "10:00",
                                "taskType": "directwh",
                                "end": "13:00",
                                "taskId": "202004210941479521404040e0000060"
                            },
                            {
                                "start": "16:00",
                                "taskType": "fixedwh",
                                "end": "19:00",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060,202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "06:00",
                                "taskType": "fixedwh",
                                "end": "11:00",
                                "taskId": "202004210940473541404040e0000056"
                            },
                            {
                                "start": "12:30",
                                "taskType": "fixedwh",
                                "end": "16:30",
                                "taskId": "202004210940473541404040e0000056"
                            },
                            {
                                "start": "18:00",
                                "taskType": "fixedwh",
                                "end": "21:00",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "0",
                        "combiRuleNewVal": "0",
                        "detail": [
                            {
                                "start": "10:00",
                                "taskType": "fixedwh",
                                "end": "13:00",
                                "taskId": "202004210940473541404040e0000056"
                            },
                            {
                                "start": "16:00",
                                "taskType": "directwh",
                                "end": "19:00",
                                "taskId": "202004210941479521404040e0000060"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060,202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "10:00",
                                "taskType": "fixedwh",
                                "end": "13:00",
                                "taskId": "202004210940473541404040e0000056"
                            },
                            {
                                "start": "18:00",
                                "taskType": "fixedwh",
                                "end": "23:00",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "10:30",
                                "taskType": "directwh",
                                "end": "16:30",
                                "taskId": "202004210941479521404040e0000060"
                            },
                            {
                                "start": "18:00",
                                "taskType": "directwh",
                                "end": "23:00",
                                "taskId": "202004210941479521404040e0000060"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "10:30",
                                "taskType": "fixedwh",
                                "end": "13:30",
                                "taskId": "202004210940473541404040e0000056"
                            },
                            {
                                "start": "18:00",
                                "taskType": "directwh",
                                "end": "21:30",
                                "taskId": "202004210941479521404040e0000060"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060,202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "06:00",
                                "taskType": "directwh",
                                "end": "13:00",
                                "taskId": "202004210941479521404040e0000060"
                            },
                            {
                                "start": "16:00",
                                "taskType": "fixedwh",
                                "end": "19:00",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060,202004210940473541404040e0000056"
                    }
                ]
            },
            {
                "2020-02-13": [
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "11:30",
                                "taskType": "directwh",
                                "end": "14:30",
                                "taskId": "202004210942484551404040e0000073"
                            },
                            {
                                "start": "16:30",
                                "taskType": "directwh",
                                "end": "19:30",
                                "taskId": "202004210941479521404040e0000060"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060,202004210942484551404040e0000073"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "11:30",
                                "taskType": "directwh",
                                "end": "14:30",
                                "taskId": "202004210941479521404040e0000060"
                            },
                            {
                                "start": "16:30",
                                "taskType": "directwh",
                                "end": "22:30",
                                "taskId": "202004210942484551404040e0000073"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060,202004210942484551404040e0000073"
                    },
                    {
                        "combiRuleOldVal": "2",
                        "combiRuleNewVal": "2",
                        "detail": [
                            {
                                "start": "20:00",
                                "taskType": "fixedwh",
                                "end": "23:00",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "2",
                        "combiRuleNewVal": "2",
                        "detail": [
                            {
                                "start": "20:00",
                                "taskType": "directwh",
                                "end": "23:00",
                                "taskId": "202004210941479521404040e0000060"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060"
                    },
                    {
                        "combiRuleOldVal": "2",
                        "combiRuleNewVal": "2",
                        "detail": [
                            {
                                "start": "20:00",
                                "taskType": "directwh",
                                "end": "23:00",
                                "taskId": "202004210942484551404040e0000073"
                            }
                        ],
                        "combiRule": "202004210942484551404040e0000073"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "06:00",
                                "taskType": "directwh",
                                "end": "12:00",
                                "taskId": "202004210942484551404040e0000073"
                            },
                            {
                                "start": "14:30",
                                "taskType": "directwh",
                                "end": "19:00",
                                "taskId": "202004210942484551404040e0000073"
                            }
                        ],
                        "combiRule": "202004210942484551404040e0000073"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "11:30",
                                "taskType": "directwh",
                                "end": "14:30",
                                "taskId": "202004210941479521404040e0000060"
                            },
                            {
                                "start": "16:30",
                                "taskType": "fixedwh",
                                "end": "19:30",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060,202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "06:00",
                                "taskType": "fixedwh",
                                "end": "12:00",
                                "taskId": "202004210940473541404040e0000056"
                            },
                            {
                                "start": "14:30",
                                "taskType": "fixedwh",
                                "end": "19:00",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "11:30",
                                "taskType": "fixedwh",
                                "end": "14:30",
                                "taskId": "202004210940473541404040e0000056"
                            },
                            {
                                "start": "16:30",
                                "taskType": "directwh",
                                "end": "22:30",
                                "taskId": "202004210941479521404040e0000060"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060,202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "11:30",
                                "taskType": "directwh",
                                "end": "14:30",
                                "taskId": "202004210942484551404040e0000073"
                            },
                            {
                                "start": "16:30",
                                "taskType": "directwh",
                                "end": "19:30",
                                "taskId": "202004210942484551404040e0000073"
                            }
                        ],
                        "combiRule": "202004210942484551404040e0000073"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "06:00",
                                "taskType": "directwh",
                                "end": "12:00",
                                "taskId": "202004210941479521404040e0000060"
                            },
                            {
                                "start": "14:30",
                                "taskType": "directwh",
                                "end": "19:00",
                                "taskId": "202004210941479521404040e0000060"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "11:30",
                                "taskType": "fixedwh",
                                "end": "14:30",
                                "taskId": "202004210940473541404040e0000056"
                            },
                            {
                                "start": "16:30",
                                "taskType": "fixedwh",
                                "end": "20:30",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210940473541404040e0000056"
                    }
                ]
            },
            {
                "2020-02-14": [
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "11:00",
                                "taskType": "fixedwh",
                                "end": "14:00",
                                "taskId": "202004210940473541404040e0000056"
                            },
                            {
                                "start": "18:00",
                                "taskType": "directwh",
                                "end": "23:00",
                                "taskId": "202004210941479521404040e0000060"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060,202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "06:00",
                                "taskType": "fixedwh",
                                "end": "13:00",
                                "taskId": "202004210940473541404040e0000056"
                            },
                            {
                                "start": "14:00",
                                "taskType": "fixedwh",
                                "end": "19:00",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "11:00",
                                "taskType": "directwh",
                                "end": "14:00",
                                "taskId": "202004210941479521404040e0000060"
                            },
                            {
                                "start": "17:30",
                                "taskType": "fixedwh",
                                "end": "20:30",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060,202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "06:00",
                                "taskType": "directwh",
                                "end": "14:00",
                                "taskId": "202004210941479521404040e0000060"
                            },
                            {
                                "start": "17:00",
                                "taskType": "directwh",
                                "end": "20:30",
                                "taskId": "202004210941479521404040e0000060"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "19:30",
                                "taskType": "fixedwh",
                                "end": "23:00",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "11:00",
                                "taskType": "directwh",
                                "end": "17:00",
                                "taskId": "202004210941479521404040e0000060"
                            },
                            {
                                "start": "18:00",
                                "taskType": "fixedwh",
                                "end": "21:00",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060,202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "11:00",
                                "taskType": "fixedwh",
                                "end": "14:00",
                                "taskId": "202004210940473541404040e0000056"
                            },
                            {
                                "start": "17:30",
                                "taskType": "directwh",
                                "end": "20:30",
                                "taskId": "202004210941479521404040e0000060"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060,202004210940473541404040e0000056"
                    }
                ]
            },
            {
                "2020-02-15": [
                    {
                        "combiRuleOldVal": "0",
                        "combiRuleNewVal": "0",
                        "detail": [
                            {
                                "start": "06:00",
                                "taskType": "directwh",
                                "end": "13:00",
                                "taskId": "202004210941479521404040e0000060"
                            },
                            {
                                "start": "15:30",
                                "taskType": "directwh",
                                "end": "18:30",
                                "taskId": "202004210941479521404040e0000060"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060"
                    },
                    {
                        "combiRuleOldVal": "0",
                        "combiRuleNewVal": "0",
                        "detail": [
                            {
                                "start": "06:00",
                                "taskType": "directwh",
                                "end": "13:00",
                                "taskId": "202004210942484551404040e0000073"
                            },
                            {
                                "start": "15:30",
                                "taskType": "directwh",
                                "end": "18:30",
                                "taskId": "202004210942484551404040e0000073"
                            }
                        ],
                        "combiRule": "202004210942484551404040e0000073"
                    },
                    {
                        "combiRuleOldVal": "0",
                        "combiRuleNewVal": "0",
                        "detail": [
                            {
                                "start": "12:30",
                                "taskType": "directwh",
                                "end": "15:30",
                                "taskId": "202004210941479521404040e0000060"
                            },
                            {
                                "start": "18:30",
                                "taskType": "fixedwh",
                                "end": "23:00",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060,202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "12:00",
                                "taskType": "fixedwh",
                                "end": "15:00",
                                "taskId": "202004210940473541404040e0000056"
                            },
                            {
                                "start": "17:30",
                                "taskType": "fixedwh",
                                "end": "20:30",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "12:00",
                                "taskType": "directwh",
                                "end": "15:00",
                                "taskId": "202004210941479521404040e0000060"
                            },
                            {
                                "start": "17:30",
                                "taskType": "directwh",
                                "end": "20:30",
                                "taskId": "202004210941479521404040e0000060"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "12:30",
                                "taskType": "fixedwh",
                                "end": "15:30",
                                "taskId": "202004210940473541404040e0000056"
                            },
                            {
                                "start": "18:00",
                                "taskType": "fixedwh",
                                "end": "23:00",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "06:00",
                                "taskType": "fixedwh",
                                "end": "13:00",
                                "taskId": "202004210940473541404040e0000056"
                            },
                            {
                                "start": "15:30",
                                "taskType": "fixedwh",
                                "end": "19:30",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "12:30",
                                "taskType": "directwh",
                                "end": "15:30",
                                "taskId": "202004210941479521404040e0000060"
                            },
                            {
                                "start": "18:00",
                                "taskType": "directwh",
                                "end": "23:00",
                                "taskId": "202004210941479521404040e0000060"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060"
                    },
                    {
                        "combiRuleOldVal": "0",
                        "combiRuleNewVal": "0",
                        "detail": [
                            {
                                "start": "12:30",
                                "taskType": "fixedwh",
                                "end": "15:30",
                                "taskId": "202004210940473541404040e0000056"
                            },
                            {
                                "start": "17:30",
                                "taskType": "directwh",
                                "end": "20:30",
                                "taskId": "202004210941479521404040e0000060"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060,202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "0",
                        "combiRuleNewVal": "0",
                        "detail": [
                            {
                                "start": "12:30",
                                "taskType": "directwh",
                                "end": "15:30",
                                "taskId": "202004210941479521404040e0000060"
                            },
                            {
                                "start": "17:30",
                                "taskType": "directwh",
                                "end": "20:30",
                                "taskId": "202004210942484551404040e0000073"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060,202004210942484551404040e0000073"
                    },
                    {
                        "combiRuleOldVal": "0",
                        "combiRuleNewVal": "0",
                        "detail": [
                            {
                                "start": "12:30",
                                "taskType": "directwh",
                                "end": "15:30",
                                "taskId": "202004210942484551404040e0000073"
                            },
                            {
                                "start": "18:30",
                                "taskType": "directwh",
                                "end": "23:00",
                                "taskId": "202004210941479521404040e0000060"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060,202004210942484551404040e0000073"
                    },
                    {
                        "combiRuleOldVal": "0",
                        "combiRuleNewVal": "0",
                        "detail": [
                            {
                                "start": "18:30",
                                "taskType": "directwh",
                                "end": "23:00",
                                "taskId": "202004210942484551404040e0000073"
                            }
                        ],
                        "combiRule": "202004210942484551404040e0000073"
                    },
                    {
                        "combiRuleOldVal": "0",
                        "combiRuleNewVal": "0",
                        "detail": [
                            {
                                "start": "18:30",
                                "taskType": "directwh",
                                "end": "21:30",
                                "taskId": "202004210942484551404040e0000073"
                            }
                        ],
                        "combiRule": "202004210942484551404040e0000073"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "06:00",
                                "taskType": "directwh",
                                "end": "13:00",
                                "taskId": "202004210942484551404040e0000073"
                            },
                            {
                                "start": "15:30",
                                "taskType": "directwh",
                                "end": "19:30",
                                "taskId": "202004210942484551404040e0000073"
                            }
                        ],
                        "combiRule": "202004210942484551404040e0000073"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "12:00",
                                "taskType": "directwh",
                                "end": "15:00",
                                "taskId": "202004210942484551404040e0000073"
                            },
                            {
                                "start": "17:30",
                                "taskType": "directwh",
                                "end": "20:30",
                                "taskId": "202004210942484551404040e0000073"
                            }
                        ],
                        "combiRule": "202004210942484551404040e0000073"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "12:30",
                                "taskType": "directwh",
                                "end": "15:30",
                                "taskId": "202004210942484551404040e0000073"
                            },
                            {
                                "start": "18:00",
                                "taskType": "directwh",
                                "end": "23:00",
                                "taskId": "202004210942484551404040e0000073"
                            }
                        ],
                        "combiRule": "202004210942484551404040e0000073"
                    },
                    {
                        "combiRuleOldVal": "0",
                        "combiRuleNewVal": "0",
                        "detail": [
                            {
                                "start": "06:00",
                                "taskType": "fixedwh",
                                "end": "13:00",
                                "taskId": "202004210940473541404040e0000056"
                            },
                            {
                                "start": "15:30",
                                "taskType": "fixedwh",
                                "end": "19:00",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "0",
                        "combiRuleNewVal": "0",
                        "detail": [
                            {
                                "start": "12:30",
                                "taskType": "directwh",
                                "end": "15:30",
                                "taskId": "202004210942484551404040e0000073"
                            },
                            {
                                "start": "18:30",
                                "taskType": "directwh",
                                "end": "21:30",
                                "taskId": "202004210941479521404040e0000060"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060,202004210942484551404040e0000073"
                    },
                    {
                        "combiRuleOldVal": "0",
                        "combiRuleNewVal": "0",
                        "detail": [
                            {
                                "start": "12:30",
                                "taskType": "fixedwh",
                                "end": "15:30",
                                "taskId": "202004210940473541404040e0000056"
                            },
                            {
                                "start": "17:30",
                                "taskType": "fixedwh",
                                "end": "20:30",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "06:00",
                                "taskType": "directwh",
                                "end": "13:00",
                                "taskId": "202004210941479521404040e0000060"
                            },
                            {
                                "start": "15:30",
                                "taskType": "directwh",
                                "end": "19:30",
                                "taskId": "202004210941479521404040e0000060"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060"
                    }
                ]
            },
            {
                "2020-02-16": [
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "14:00",
                                "taskType": "fixedwh",
                                "end": "17:00",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210940473541404040e0000056"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "06:00",
                                "taskType": "directwh",
                                "end": "14:00",
                                "taskId": "202004210941479521404040e0000060"
                            },
                            {
                                "start": "17:00",
                                "taskType": "directwh",
                                "end": "21:00",
                                "taskId": "202004210941479521404040e0000060"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "14:00",
                                "taskType": "directwh",
                                "end": "17:00",
                                "taskId": "202004210941479521404040e0000060"
                            }
                        ],
                        "combiRule": "202004210941479521404040e0000060"
                    },
                    {
                        "combiRuleOldVal": "1",
                        "combiRuleNewVal": "1",
                        "detail": [
                            {
                                "start": "06:00",
                                "taskType": "fixedwh",
                                "end": "14:00",
                                "taskId": "202004210940473541404040e0000056"
                            },
                            {
                                "start": "17:00",
                                "taskType": "fixedwh",
                                "end": "21:00",
                                "taskId": "202004210940473541404040e0000056"
                            }
                        ],
                        "combiRule": "202004210940473541404040e0000056"
                    }
                ]
            }
        ],
        "did": 3132,
        "token": "c83975ed0ef86e81419452da0290c8b2",
        "timestr": "2020-04-27 17:32:02.998020",
        "cid": 60000004
    }

    res = ManPowerService.doRequest(data)
    print(res)
