#!/usr/bin/env python
# encoding: utf-8
"""
@author: pengyd
@file: schedule_view_service.py
@time: 2020/3/25 13:56
@desc:
"""
import ast
import json
import sys

from laborTask.service.labor_task_service import LaborTaskService
from laborTaskView.service.all_title_array import TitleArray
from scheduleView.model.schedule_view_model import ScheduleViewModel
from utils.dateTimeProcess import DateTimeProcess
from utils.webResult import WebResult
import numpy as np
import pandas as pd


class ScheduleViewService:


    @classmethod
    def list_sch_byday(cls,cid: str, did: int, date: str):
        if cid is None or len(cid) < 1 or did is None:
            return WebResult.errorResult("cid did 必填")
        if date is None or len(date) < 1:
            return WebResult.errorResult("日期必填")
        result = ScheduleViewModel.query(cid, did, date, None, None, None, None)
        if result is None:
            return WebResult.errorResult("获取结果失败")
        data = result.get("data", [])
        return WebResult.successData(data)

    @classmethod
    def getApplyId(cls, cid: str, did: int):
        if cid is None or did is None:
            return WebResult.errorResult("cid, did  必填")

        applyIds = ScheduleViewModel.getApplyId(cid, did)

        if applyIds is None:
            return WebResult.errorResult("cid 查询失败")
        data = []
        for item in applyIds:
            data.append(item['applyId'])
        return WebResult.successData(data)


    @classmethod
    def list_task_schedule(cls, cid, did: int, date: str, apply_id: str, scheme_type: str, page: int, size: int):
        """

        :param cid:
        :param did:
        :param date:
        :param apply_id:
        :param scheme_type:
        :param page:
        :param size:
        :return:
        """
        if cid is None or len(cid) < 1 or did is None:
            return WebResult.errorResult("cid did 必填")
        if date is None or len(date) < 1:
            return WebResult.errorResult("日期必填")
        if scheme_type is None or len(scheme_type) < 1:
            return WebResult.errorResult("scheme_type必填")
        if apply_id is None or len(apply_id) < 1:
            return WebResult.errorResult("apply_id必填")
        if page is None or page < 0:
            page = 0
        if size is None or size < 0:
            size = 5
        result = ScheduleViewModel.query(cid, did, date, apply_id, scheme_type, page, size)
        if result is None:
            return WebResult.errorResult("查寻数据失败")
        data = result.get("data", [])
        count = result.get("count", [])

        return WebResult.successData(data, count)

    @classmethod
    def list(cls, cid: str, did: int, date: str, apply_id: str, scheme_type: str):
        """

        :param cid:
        :param did:
        :param date:
        :param apply_id:
        :param scheme_type:
        :param page:
        :param size:
        :return:
        """
        return_result = {}
        return_result_1 = {}
        return_result_2 = {}
        return_result_3 = {}
        return_result_4 = {}

        query_result = cls.list_task_schedule(cid, did, date, apply_id, scheme_type, 0, sys.maxsize)
        if query_result is None:
            return WebResult.errorResult("查询失败")
        if query_result.isError:
            return query_result

        if len(query_result.data) == 0:
            return WebResult.errorResult("暂无数据")
        df = pd.DataFrame(query_result.data, columns=('eid', 'task_id', 'startTime', 'endTime', 'workTime'))

        # 任务id翻译数组
        task_ids = []
        for one in query_result.data:
            task_ids.append(one['task_id'])
        task_ids = np.unique(task_ids)
        task_ids_2_name_result = LaborTaskService.listForBids(cid, task_ids)
        task_ids_2_name = {}
        if task_ids_2_name_result.isSuccess:
            task_ids_2_name = task_ids_2_name_result.data
        for one in task_ids:
            if not (one in task_ids_2_name):
                if not one.strip() == '':  # 去空值
                    task_ids_2_name.setdefault(one, one)

        # 有的值是空的，根据起始结束时间计算补齐
        df['eid'] = df['eid'].apply(pd.to_numeric)
        df['workTime'] = df.apply(f_get_work_time, axis=1, args=('startTime', 'endTime', 'workTime'))

        # 计算时间颗粒度 规则根据起始/结束时间情况：
        # 分钟数都一致的（全00/全15/全30/全45）颗粒度=60
        # 分钟数含30差值的（全为00+30/全为15+45）颗粒度=30
        # 分钟数含15差值的 (15+30等)颗粒度=15
        df['minute_type'] = df.apply(f_get_minute, axis=1, args=('startTime', 'endTime'))
        min_type_list = np.unique(df['minute_type'].to_list()).astype(np.int16)
        if len(min_type_list) < 2:
            time_step = 60
        elif len(min_type_list) > 2:
            time_step = 15
        else:
            if min_type_list.ptp() == 30:
                time_step = 30
            else:
                time_step = 15

        # 计算时间范围和表头的list
        start_time = df['startTime'].apply(pd.to_datetime).min()
        end_time = df['endTime'].apply(pd.to_datetime).max()
        dlt = (end_time - start_time).seconds // 60
        time_num = dlt // time_step
        title_list = []
        for _ in range(time_num):
            tt = DateTimeProcess.cacl_time_str(startTime=start_time.strftime('%H:%M'),
                                               timeSize=time_step, timeSizeNum=_)
            title_list.append(tt)
        # 生成和表头一致的数组 用于展示
        df['time_arr'] = df.apply(f_get_time_arr, axis=1, args=(task_ids_2_name, title_list))
        # time_arr里没有按人员合并 接下来做合并（如果有重合会一格显示两个）
        df_combine = pd.pivot_table(df, values='workTime', index=['eid'])
        df_combine['date'] = date
        df_combine['eid'] = df_combine.index
        df_combine['work_time'] = df_combine['workTime']
        df_combine = df_combine.drop(['workTime'], axis=1)
        df_combine['time_arr'] = df_combine.apply(f_get_time_arr_combine, axis=1, args=(title_list, df))

        for i in range(len(title_list)):
            df_combine[title_list[i]] = df_combine.apply(lambda row: row['time_arr'][i], axis=1)
        return_result_1['title'] = ['日期',  '员工ID', '员工工时'] + title_list
        return_result_1['data'] = df_combine.drop(['time_arr'], axis=1).to_dict(orient='records')

        # 下方页面的统计信息
        return_result_2['total_emp'] = len(df['eid'].unique())
        return_result_2['total_time'] = int(df['workTime'].sum())
        if return_result_2['total_time'] > 0:
            return_result_2['total_min'] = int(df['workTime'].min())
            return_result_2['total_max'] = int(df['workTime'].max())
        else:
            return_result_2['total_min'] = 0
            return_result_2['total_max'] = 0

        return_result_3['real_emp'] = len(df[df['eid'] > -1]['eid'].unique())
        return_result_3['real_time'] = int(df[df['eid'] > -1]['workTime'].sum())
        if return_result_3['real_time'] > 0:
            return_result_3['real_min'] = int(df[df['eid'] > -1]['workTime'].min())
            return_result_3['real_max'] = int(df[df['eid'] > -1]['workTime'].max())
        else:
            return_result_3['real_min'] = 0
            return_result_3['real_max'] = 0

        return_result_4['vir_emp'] = len(df[df['eid'] < 0]['eid'].unique())
        return_result_4['vir_time'] = int(df[df['eid'] < 0]['workTime'].sum())
        if return_result_4['vir_time'] > 0:
            return_result_4['vir_min'] = int(df[df['eid'] < 0]['workTime'].min())
            return_result_4['vir_max'] = int(df[df['eid'] < 0]['workTime'].max())
        else:
            return_result_4['vir_min'] = 0
            return_result_4['vir_max'] = 0

        return_result['table1'] = return_result_1
        return_result['table2'] = return_result_2
        return_result['table3'] = return_result_3
        return_result['table4'] = return_result_4
        return WebResult.successData(return_result)


def f_get_work_time(arr, start_time, end_time, default):
    result = 0
    if (arr[default] is None) or (len(arr[default]) == 0):
        datetime_end = pd.to_datetime(arr[end_time])
        datetime_start = pd.to_datetime(arr[start_time])
        result = (datetime_end - datetime_start).seconds // 60
    else:
        result = int(arr[default])
    return result


def f_get_minute(arr, start_time, end_time):
    arr = [pd.to_datetime(arr[start_time]).strftime('%M'), pd.to_datetime(arr[end_time]).strftime('%M')]
    return arr


def f_get_time_arr(arr, id_2_name, title_list):
    task_name = arr['task_id']
    result_arr = []
    if task_name in id_2_name:
        task_name = id_2_name[arr['task_id']]
    start_time = arr['startTime'][11:]
    end_time = arr['endTime'][11:]
    for one in title_list:
        if (one >= start_time) and (one < end_time):
            result_arr.append(task_name)
        else:
            result_arr.append('')
    return result_arr


def f_get_time_arr_combine(arr, title_list, df):
    ls = df[df['eid'] == arr['eid']]['time_arr'].to_list()
    for i in range(len(ls)):
        if i == 0:
            r = np.array(ls[i])
        else:
            r = np.char.add(r, ls[i])
    return r.tolist()


if __name__ == '__main__':
    # cid, did, date, apply_id: str, scheme_type,  page, size
    ScheduleViewService.list('50000671', 62, '2019-12-01', '99999999999999999999999999', 'violation')
