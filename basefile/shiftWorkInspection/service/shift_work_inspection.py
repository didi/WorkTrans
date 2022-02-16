#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: shift_work_inspection.py
@time: 2020/3/25 15:26
@desc:
'''
import json
import operator
import datetime
from functools import reduce

from laborCaclValue.service.labor_cacl_value_service import LaborCaclValueService
from laborTask.service.labor_task_service import LaborTaskService
from laborTaskView.service.task_view_service import TaskViewService
from scheduleView.service.schedule_view_service import ScheduleViewService
from shiftWorkInspection.model.temp import ScheduleTemp
from utils.collectionUtils import CollectionUtils
from utils.dateTimeProcess import DateTimeProcess
from utils.dateUtils import DateUtils
from utils.webResult import WebResult


class ShiftWorkInspectionService:

    @classmethod
    def list(cls, cid: str, did: int, date: str):
        if cid is None or did is None or date is None:
            return WebResult.errorResult("cid, did, date 不能为空")

        _date = DateUtils.transTime(date, "%Y-%m-%d")
        if _date is None:
            return WebResult.errorResult("日期格式不正确")

        # ------------------------准备劳动工时预测数据 start-----------------#
        #         查询 labor_cacl_value  劳动工时预测
        # 以任务为维度 统计
        webResult = LaborCaclValueService.listByDay(cid, did, date)
        if webResult.isError:
            return webResult
        data = webResult.data

        laborCaclValueResult = cls.initLaborCaclValue(data)
        if laborCaclValueResult is None:
            return WebResult.errorResult("labor_cacl_value 数据异常")
        bids = list(laborCaclValueResult.keys())
        # ------------------------准备劳动工时预测数据 end-----------------#

        # ------------------------准备劳动人数计算 开始-----------------#

        result = TaskViewService.listByDay(cid, did, date)
        if result.isError:
            return result
        data = result.data

        if data is None or len(data) == 0:
            return WebResult.errorResult("task_matrix_ss 未查询到数据")
        taskViewResult = cls.initTaskView(data[0])
        if taskViewResult is None:
            return WebResult.errorResult("task_matrix_ss 数据异常")
        bids.extend(list(taskViewResult.keys()))
        bids = list(set(bids))

        # ------------------------准备劳动人数计算 结束-----------------#

        # ------------------------排班计算 开始-----------------#
        print("# ------------------------排班计算 开始-----------------#")
        schQueryResult = ScheduleViewService.list_sch_byday(cid, did, date)
        if schQueryResult.isError:
            return schQueryResult

        scheduleResult = cls.initScheduleData(schQueryResult.data)
        if scheduleResult is None:
            return WebResult.errorResult("task_schedule 数据异常")
        schTaskBids = []

        viewResultAll = []
        allTaskBid = bids
        for taskBid in scheduleResult:
            # 目前只支持任务。 对应表的储存类型不确定所以不方便做其它类型
            taskBidtoitem = scheduleResult.get(taskBid, {})
            viewResutl = cls.initSchResult(laborCaclValueResult, taskViewResult, taskBidtoitem, taskBid, date)
            if viewResutl is None:
                continue
            schTaskBids.append(taskBid)
            allTaskBid.append(taskBid)
            viewResultAll.append(viewResutl)
        # 获取差集
        bids = list(set(bids).difference(set(schTaskBids)))

        if len(bids) > 0:
            # sch 中没有的任务。 有就用， 没有就补全
            for bid in bids:
                viewResut2 = cls.initCalResult(laborCaclValueResult, taskViewResult, bid, date)
                if viewResut2 is None:
                    continue
                viewResultAll.append(viewResut2)
        taskTypesResult = LaborTaskService.listFromBids(cid, allTaskBid)
        taskTypes = {}
        if taskTypesResult.isSuccess:
            taskTypes = taskTypesResult.data

        # ------------------------整理数据给前端 开始-----------------#
        if len(taskTypes) > 0:
            for item in viewResultAll:
                taskBid = item.get("taskBid", "")
                taskType = taskTypes.get(taskBid, {"taskName": "暂无", "taskType": "暂无"})
                item["taskName"] = taskType.get("taskName")
                item["taskType"] = taskType.get("taskType")

        return WebResult.successData(viewResultAll)
        # ------------------------整理数据给前端 结束-----------------#

    @classmethod
    def initLaborCaclValue(cls, data):
        if data is None:
            return None
        taskBidToWorkTime = {}
        for item in data:
            taskBid = item.get("taskBid", None)
            laborWorkTime = LaborCaclValueService.getLaborWorkTime(item)
            _laborWorkTime = taskBidToWorkTime.get(taskBid, None)
            if _laborWorkTime is not None:
                _laborWorkTime += laborWorkTime
            else:
                _laborWorkTime = laborWorkTime
            taskBidToWorkTime[taskBid] = _laborWorkTime
        return taskBidToWorkTime

    @classmethod
    def initTaskView(cls, data):
        if data is None:
            return None

        startTime = data.get("start_time", None)
        endTime = data.get("end_time", None)
        _bids = json.loads(data.get('task_matrix', "[]"))
        oneStaffBidNum = 0
        if len(_bids) > 0:
            oneStaffBid = _bids[0]
            oneStaffBidNum = len(oneStaffBid)
        # 转成一维数组
        bids = reduce(operator.add, _bids)
        # 计算颗粒度
        diff_min = DateTimeProcess.worktime_interval(startTime, endTime, None)

        # 计算一个任务代表多少分钟
        step = diff_min / oneStaffBidNum
        taskBidToWorkTime = {}
        for i in set(bids):
            taskBidWorkTime = taskBidToWorkTime.get(i, 0)
            num = bids.count(i)
            taskBidToWorkTime[i] = taskBidWorkTime + (num * step)
        return taskBidToWorkTime

    @classmethod
    def initScheduleData(cls, scheduleData):
        if scheduleData is None:
            return None

        taskoutBidToItem = CollectionUtils.group(scheduleData, "outId")
        #     emp, worktime,fillRate
        for taskBid in taskoutBidToItem:
            items = taskoutBidToItem.get(taskBid, [])
            if items is None:
                continue
            typetoitems = CollectionUtils.group(items, "scheme_type")
            # task 要看一下哪个有哪个没有
            taskoutBidToItem[taskBid] = typetoitems

        return taskoutBidToItem

    @classmethod
    def initSchResult(cls, laborCaclValueResult, taskViewResult, taskBidtoitem, taskBid, date):

        if taskBidtoitem is None and laborCaclValueResult is None and taskViewResult is None:
            return None
        # 计算出修改值， 几种类型的总工时

        laborItem = 0
        if laborCaclValueResult is not None:
            laborItem = laborCaclValueResult.get(taskBid, 0)
        taskItem = 0
        if taskViewResult is not None:
            taskItem = taskViewResult.get(taskBid, 0)

        editAll = 0
        empAll = 0
        worktimeAll = 0
        fillRateAll = 0
        violationAll = 0
        effectAll = 0
        if taskBidtoitem is not None:
            for type in taskBidtoitem:
                typeToItems = taskBidtoitem.get(type, [])
                allWorktime = 0
                for item in typeToItems:
                    applyId = item.get("applyId", "")
                    startTime = item.get("startTime", None)
                    endTime = item.get("endTime", None)
                    interval = DateTimeProcess.worktime_full_interval(startTime, endTime)
                    if interval is None:
                        # 日期格式不正确
                        continue

                    if "99999999999999999999999999" == applyId:
                        # 修改 相加所有
                        editAll += interval

                    allWorktime += interval
                if "emp" == type:
                    empAll = allWorktime
                elif "worktime" == type:
                    worktimeAll = allWorktime
                elif "fillRate" == type:
                    fillRateAll = allWorktime
                elif "violation" == type:
                    violationAll = allWorktime
                elif "effect" == type:
                    effectAll = allWorktime

        return cls.calViewResult(laborItem, taskItem, editAll, empAll, worktimeAll, fillRateAll, violationAll,
                                 effectAll, date, taskBid)



    @classmethod
    def initCalResult(cls, laborCaclValueResult, taskViewResult, bid, date):

        if bid is None:
            return None
        laborItem = 0
        if laborCaclValueResult is not None:
            laborItem = laborCaclValueResult.get(bid, 0)
        taskItem = 0
        if taskViewResult is not None:
            taskItem = taskViewResult.get(bid, 0)
        return cls.calViewResult(laborItem, taskItem, 0, 0, 0, 0, 0, 0, date, bid)

    @classmethod
    def calViewResult(cls, laborItem, taskItem, editAll, empAll, worktimeAll, fillRateAll, violationAll,
                      effectAll, date, taskBid):

        # 减去预测工时
        # 日期
        """
        :param taskBid:
        :param laborItem: 预测工时
        :param taskItem: 计算工时
        :param editAll:
        :param empAll:
        :param worktimeAll:
        :param fillRateAll:
        :param violationAll:
        :param effectAll:
        :param date:
        :return:
        """
        return {
                    "date": date,
                    "taskBid": taskBid,
                    "forecastWorktime": laborItem,
                    "calWorkTime": taskItem,
                    "FCsiffV": round(taskItem - laborItem, 2),
                    "editSchWorkTime": editAll,
                    "editDiffV": round(editAll - laborItem, 2),
                    "empWorkTime": empAll,
                    "empDiffV": round(empAll - laborItem, 2),
                    "worktimeAll": worktimeAll,
                    "worktimeDiffV": round(worktimeAll - laborItem, 2),
                    "fillRateAll": fillRateAll,
                    "fillDiffV": round(fillRateAll - laborItem, 2),
                    "violationAll": violationAll,
                    "violationDiffV": round(violationAll - laborItem, 2),
                    "effectAll": effectAll,
                    "effectDiffV": round(effectAll - laborItem, 2)
                }


if __name__ == '__main__':
    pass
    # print(json.dumps(ShiftWorkInspection.list("50000671", 62, "2019-12-01").__str__()))