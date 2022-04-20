#!/usr/bin/env python
# encoding: utf-8
"""
@author: pengyd
@file: task_view_service.py
@time: 2020/3/19 13:56
@desc:
"""
import ast
import json
import sys

from laborTask.service.labor_task_service import LaborTaskService
from laborTaskView.model.task_view_model import TaskViewModel
from laborTaskView.service.all_title_array import TitleArray
from utils.collectionUtils import CollectionUtils
from utils.dateTimeProcess import DateTimeProcess
from utils.dateUtils import DateUtils
from utils.webResult import WebResult
import pandas as pd


class TaskViewService:

    @classmethod
    def listByDay(cls, cid: str, did: int, day: str):
        if cid is None or len(cid) < 1 or did is None:
            return WebResult.errorResult("cid did 必填")
        if day is None or len(day) < 1:
            return WebResult.errorResult("日期必填")

        result = TaskViewModel.query(cid, did, day, "full", 0, sys.maxsize)
        if result is None:
            return WebResult.errorResult("查询失败")
        data = result['data']
        data = data if (data is not None and len(data) > 0) else []
        if data is None or len(data) == 0:
            return WebResult.errorResult("暂无数据")

        return WebResult.successData(data, result.get("count", 0))



    @classmethod
    def list(cls, cid: str, did: int, date: str, t_type: str,  page: int, size: int):

        if cid is None or len(cid) < 1 or did is None:
            return WebResult.errorResult("cid did 必填")
        if date is None or len(date) < 1:
            return WebResult.errorResult("日期必填")
        if t_type is None or len(t_type) < 1:
            return WebResult.errorResult("type必填")
        if page is None or page < 0:
            page = 0
        if size is None or size < 0:
            size = 5

        result = TaskViewModel.query(cid, did, date, t_type, page, size)
        if result is None:
            return WebResult.errorResult("查询失败")
        if result['data'] is None or len(result['data']) == 0:
            return WebResult.errorResult("暂无数据")
        # 过滤没有劳动人数的数据
        cls._filter(result)
        if result.get("data", None) is None or len(result.get("data")) < 1:
            return WebResult.errorResult("暂无数据")
        # 整理要翻译的bid数组(提取，去重)
        bids = np.array([], dtype=np.str_)
        # 全局颗粒度 单条的话就是单个result的颗粒度
        all_step = 60
        # all_step_arr = []
        for one in result['data']:
            matrix_np_arr = np.array(ast.literal_eval(one['task_matrix']), dtype=np.str_)
            one['task_matrix'] = matrix_np_arr
            bids = np.append(bids, np.unique(matrix_np_arr))
            # 计算颗粒度
            diff_min = DateTimeProcess.worktime_interval(one['start_time'], one['end_time'], 15)
            step = diff_min // one['task_matrix'].shape[1]
            one['step_real'] = step
            one['step_now'] = step
            all_step = min(all_step, step)

        # 以最小颗粒度15统一(拆分)
        for one in result['data']:
            if one["step_now"] == 60:
                index = one['task_matrix'].shape[1]
                while index > 0:
                    index = index - 1
                    one['task_matrix'] = np.insert(one['task_matrix'], index, one['task_matrix'][..., index], axis=1)
                one["step_now"] = 30
            if one["step_now"] == 30:
                index = one['task_matrix'].shape[1]
                while index > 0:
                    index = index - 1
                    one['task_matrix'] = np.insert(one['task_matrix'], index, one['task_matrix'][..., index], axis=1)
                one["step_now"] = 15

        # all_line_count = 1440 // 15
        # all_step_arr = np.zeros((len(result['data']), all_line_count), dtype=np.str_)
        temp_index = 0
        begin = []  # time_list中第一个不为0的位置（起始位置）
        all_title_15 = TitleArray.all_title_array
        for one in result['data']:
            time_list = DateTimeProcess.timeStr_to_timeList([one['start_time'] + "-" + one['end_time']], 15)
            task_matrix_index = 0
            for i in range(len(time_list)):
                if time_list[i] == 1:
                    if task_matrix_index == 0:
                        begin.append(i)
                    all_title_15[i]['data'].extend(one['task_matrix'][..., task_matrix_index])
                    task_matrix_index = task_matrix_index + 1

            one['time_list'] = time_list
            # all_step_arr[temp_index] = time_list
            temp_index = temp_index + 1

        df = pd.DataFrame(all_title_15)
        df['data_info'] = df.apply(f_group, axis=1, args=('data',))
        df['data_len'] = df.apply(f_len, axis=1, args=('data',))

        # 查出翻译的dict，格式[{"bids": name}]
        bids = np.unique(bids)
        bid_2_name_result = LaborTaskService.listForBids(cid, bids)
        bid_2_name = {}
        if bid_2_name_result.isSuccess:
            bid_2_name = bid_2_name_result.data
        for one in bids:
            if not (one in bid_2_name):
                if not one.strip() == '':  # 去空值
                    bid_2_name.setdefault(one, one)

        detail_data = []
        for one in result['data']:
            task_matrix = one['task_matrix']
            time_list = one['time_list']
            for i in range(len(task_matrix)):
                one_task_matrix_time = get_task_with_time(task_matrix[i], time_list, bid_2_name, all_step//15)
                if one_task_matrix_time:  # 去空值
                    one_task_matrix_time.setdefault('index', str(one['auto_id']) + '_' + str(i))
                    detail_data.append(one_task_matrix_time)

        count = len(detail_data)
        # 归并
        if all_step == 15:
            return_data = {
                'data': df.loc[:, ['title', 'data_info']][df.data_len > 0].to_dict(orient='records'),
                'taskBid2Name': bid_2_name,
                'detail': {
                        'title': np.array(df.loc[:, ['title']][df.data_len > 0]).tolist(),
                        'data': detail_data
                    }
            }
        elif all_step == 30:
            offset = begin[0] % 2
            return_data = {
                'data': df.loc[:, ['title', 'data_info']][(df.index % 2 == offset)
                                                          & (df.data_len > 0)].to_dict(orient='records'),
                'taskBid2Name': bid_2_name,
                'detail': {
                    'title': np.array(df.loc[:, ['title']][(df.index % 2 == offset)
                                                           & (df.data_len > 0)]).tolist(),
                    'data': detail_data
                }
            }
        elif all_step == 60:
            offset = begin[0] % 4
            return_data = {
                'data': df.loc[:, ['title', 'data_info']][(df.index % 4 == offset)
                                                          & (df.data_len > 0)].to_dict(orient='records'),
                'taskBid2Name': bid_2_name,
                'detail': {
                    'title': np.array(df.loc[:, ['title']][(df.index % 4 == offset)
                                                           & (df.data_len > 0)]).tolist(),
                    'data': detail_data
                }
            }
        else:
            return WebResult.errorResult("数据颗粒度有误" + str(all_step))
        return WebResult.successData(return_data, count)


    @classmethod
    def select(cls, cid: str, didArr: str, forecastType: int, startDate: str, endDate: str):
        if cid is None or len(cid) < 1 or didArr is None or len(didArr) < 1 or forecastType < 0:
            return WebResult.errorCode(400, "cid, didArr, forcastType  parameter error")
        if DateUtils.transTime(startDate, "%Y-%m-%d") is None or DateUtils.transTime(endDate, "%Y-%m-%d") is None:
            return WebResult.errorCode(400, "startDate or endDate format error")

        result = TaskViewModel.slelect(cid, didArr, forecastType, startDate, endDate)
        if result is None:
            return WebResult.errorCode(400, "select data is error")
        if len(result) < 1:
            return WebResult.successResult("select data is empty")
        dateToItems = CollectionUtils.group(result, "forecast_date")
        dayToResult = {}
        for day in dateToItems:
            items = dateToItems.get(day)
            dateList = []
            cls.initItems(dateList, items)
            dayToResult[day] = cls.initItems(dateList, items)

        return WebResult.successData(dayToResult)
    #内部方法
    @classmethod
    def initItems(cls, dateList, items):
        for item in items:
            task_matrix = item.get("task_matrix", None)
            if task_matrix is None:
                continue
            task_matrix = json.loads(task_matrix)

            if len(dateList) < 1:
                dateList = cls.getDateList(item, task_matrix)
            results = []
            map = {}
            cls.initTaskMatrix(dateList, item, map, results, task_matrix)
            for re in results:
                _items = re.get("items", None)
                hash(str(_items))
                _obj = map.get(hash(str(_items)))
                re["value"] = _obj.get("count")
                re["items"] = None
        return results

    # 内部方法
    @classmethod
    def initTaskMatrix(cls, dateList, item, map, results, task_matrix):
        for tasks in task_matrix:
            hashCode = hash(str(tasks))
            obj = map.get(hashCode, None)
            if obj is None:
                # 计算 时间段
                result = cls.getDetail(tasks, dateList)
                results.append(result)
                obj = {
                    "data": item,
                    "count": 1
                }
            else:
                count = obj.get("count")
                obj["count"] = count + 1
            map[hashCode] = obj

    # 内部方法
    @classmethod
    def getDateList(cls, item, task_matrix):
        startTime = item.get("start_time")
        endTime = item.get("end_time")
        intervalMin = DateTimeProcess.worktime_interval(startTime, endTime, 0)
        interval = intervalMin // len(task_matrix[0])
        # 此处需要性能优化
        dateList = DateUtils.get_start_end_min_array(startTime, endTime, interval)
        return dateList

    # 内部方法
    @classmethod
    def getDetail(cls, tasks, dateList):

        detail = []
        _temp = [x for x in set(tasks) if x != '']
        result = {
            "taskCombination":  ','.join(str(i) for i in _temp),
            "items": tasks,
            "detail": detail
        }
        map = {}
        __len = len(tasks)
        for index, item in enumerate(tasks):
            if len(item) > 0:
                obj = map.get(item, None)
                if obj is None:
                    map[item] = {
                        "start": dateList[index],
                        "end": None
                    }
                elif __len > (index + 1) and tasks[index + 1] != item:
                    detail.append({
                        "taskId": item,
                        "start":obj.get("start"),
                        "end": dateList[index]
                    })
                    map = {}
        return result

    @classmethod
    def _filter(cls, result):
        datas = result.get("data")
        _temp = []
        for data in datas:
            task_matrix = data.get("task_matrix", None)
            if task_matrix is None or len(task_matrix) < 1 or len(json.loads(task_matrix)) < 1:
                continue
            _temp.append(data)

        result["data"] = _temp

def f_group(arr, cl):
    # return pd.value_counts(arr[cl]).to_dict()
    return pd.value_counts(list(filter(None, arr[cl]))).to_dict()  # 去空值


def f_len(arr, cl):
    return len(arr[cl])


def get_task_with_time(one_task_matrix, time_list, bid_2_name, step_filter):  # step_filter用于归并 把15颗粒度还原30或60
    result = {}
    matrix_index = 0
    for i in range(len(time_list)):
        if time_list[i] == 1:
            if not one_task_matrix[matrix_index].strip() == '' and matrix_index % step_filter == 0:  # 去空值 and 归并
                title = TitleArray.all_title_array[i].get('title')
                result.setdefault(title, bid_2_name.get(one_task_matrix[matrix_index]))
            matrix_index = matrix_index + 1
    return result



if __name__ == '__main__':
    req={"endDate":"2019-07-01","forecastType":2,
         "token": "d8e9f583b7f20750a50f47178b109871", "timestr": "2020-08-06 21:21:17.683022" ,
         "did":"7692","startDate":"2019-07-01","cid":"50000031"}
    cid = req.get("cid", None)
    did = req.get("did", None);
    did_arr = None
    if did is not None:
        did_arr = [did]
    forecast_type = req.get("forecastType", None)
    start_date = req.get("startDate", None)
    end_date = req.get("endDate", None)
    print(TaskViewModel.slelect(cid, did_arr, forecast_type, start_date, end_date))
