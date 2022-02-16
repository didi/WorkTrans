#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: labor_cacl_value_service.py
@time: 2020/3/16 10:58
@desc:
'''
import json
import sys

from laborCaclValue.model.labor_cacl_value import LaborCaclValueModel
from laborTask.service.labor_task_service import LaborTaskService
from utils.collectionUtils import CollectionUtils
from utils.dateUtils import DateUtils
from utils.webResult import WebResult


class LaborCaclValueService:

    @classmethod
    def listByDay(cls, cid: str, did: int, day: str):
        if cid is None or len(cid) < 1 or did is None:
            return WebResult.errorResult("cid, did 必填")
        if day is not None:
            dayDate = DateUtils.transTime(day, "%Y-%m-%d")
            if dayDate is None:
                return WebResult.errorResult("day 格式不正确")

        result = LaborCaclValueModel.query(cid, did, None, day, None, None, 0, sys.maxsize)
        if result is None:
            return WebResult.errorResult("查询labor_cacl_value 失败")
        datas = result.get("data", None)
        count = result.get("count", None)
        datas = datas if (datas is not None and len(datas) > 0) else []

        return WebResult.successData(datas, count)

    @classmethod
    def list(cls, cid: str, did: int, laborStandardBid: str, day: str, taskBid: str, time: str, page: str, size: str):

        if cid is None or len(cid) < 1 or did is None:
            return WebResult.errorResult("cid, did 必填")
        if time is not None:
            hourorMin = DateUtils.get_new_time_60_minute(time + ":00")
            if hourorMin is None:
                return WebResult.errorResult("time 格式不正确")
        if day is not None:
            dayDate = DateUtils.transTime(day, "%Y-%m-%d")
            if dayDate is None:
                return WebResult.errorResult("day 格式不正确")

        if page is None or page < 0:
            page = 0
        if size is None or size < 0:
            size = 5

        result = LaborCaclValueModel.query(cid, did, laborStandardBid, day, taskBid, time, page, size)

        if result is None:
            return WebResult.errorResult("查询失败")

        datas = result.get("data", None)
        count = result.get("count", None)
        datas = datas if (datas is not None and len(datas) > 0) else []
        # detail = datas
        # 统计 三个类别 劳动力工时， 上限劳动力， 下限劳动力
        # 一个劳动力标准BID 对应一个taskBid 已找海龙确认 并且 时间点从整点开始

        keytoTask = {}
        for data in datas:
            day = data.get("dayStr", None)
            startTimeStr = data.get("startTimeStr", None)

            data["laborWorkTime"] = cls.getLaborWorkTime(data)
            if day is None or startTimeStr is None:
                # 标记数据不合法 不用
                continue
            hourAndMin = DateUtils.get_new_time_60_minute(startTimeStr + ":00")
            if hourAndMin is None:
                continue
            hour = hourAndMin[0]
            minute = hourAndMin[1]

            key = day + " " + LaborCaclValueService.trfHourAndMin(hour) + ":" + LaborCaclValueService.trfHourAndMin(minute)

            _hasData = keytoTask.get(key, [])

            _hasData.append(data)
            keytoTask[key] = _hasData
        statistics = {}
        if len(keytoTask) > 0:
            for key in keytoTask:
                items = keytoTask.get(key, None)
                #合并 并转换前端统计需要得格式
                transtatisticsData = LaborCaclValueService.transtatisticsData(items)
                if transtatisticsData is None:
                    continue
                statistics[key] = transtatisticsData
        data = {"detail": datas, "statistics": statistics}

        return WebResult.successData(data, count)

    @classmethod
    def getLaborWorkTime(cls, data):
        laborWorkTime = data.get("editValue", 0.0)
        if laborWorkTime < 1:
            laborWorkTime = data.get("forecastValue", 0.0)
        if laborWorkTime < 1:
            laborWorkTime = data.get("caclValue", 0.0)
        return laborWorkTime

    @classmethod
    def getlaborStandardBid(cls, cid: str, did: int):
        if cid is None or len(cid) < 1 or did is None:
            return WebResult.errorResult("获取 劳动力标准BID cid, did 必填")

        result = LaborCaclValueModel.getlaborStandardBid(cid, did)

        if result is None:
            return WebResult.errorResult("暂无劳动力标准BID 数据")

        data = []
        for item in result:
            laborStandardBid = item['laborStandardBid']
            if laborStandardBid is None or len(laborStandardBid) < 1:
                continue
            data.append(item['laborStandardBid'])
        if len(data) < 1:
            return WebResult.errorResult("暂无劳动力标准BID 数据")
        return WebResult.successData(data)

    @classmethod
    def getTaskBid(cls, cid: str, did: int, laborStandardBid: str):
        if cid is None or len(cid) < 1 or did is None:
            return WebResult.errorResult("获取 任务 cid, did  必填")

        result = LaborCaclValueModel.getTaskBid(cid, did, laborStandardBid)

        if result is None:
            return WebResult.errorResult("暂无任务BID 数据")

        data = []
        for item in result:
            data.append(item['taskBid'])
        if len(data) < 1:
            return WebResult.errorResult("暂无任务BID 数据")
        taskBid2Name = LaborTaskService.listForBids(cid, data)
        taskBid2NameResult = {}
        for taskBid in data:
            name = taskBid
            if taskBid2Name.isSuccess:
                taskdata = taskBid2Name.data
                name = taskdata.get(taskBid, taskBid)
            taskBid2NameResult[taskBid] = name
        return WebResult.successData(taskBid2NameResult)


    @classmethod
    def trfHourAndMin(cls, hourOrMin):
        if hourOrMin < 9:
            return "0" + str(hourOrMin)
        return str(hourOrMin)

    @classmethod
    def transtatisticsData(cls, items):
        print(json.dumps(items))
        if items is None:
            return None
        tempTask = {}
        sumlaborWorkTime = 0.0
        summax = 0.0
        summin = 0.0

        for item in items:
            taskBid = item.get("taskBid", None)
            if taskBid is None:
                continue
            _value = tempTask.get(taskBid, {})
            # 修改 预测 计算
            laborWorkTime = cls.getLaborWorkTime(item)
            max_caclValue = item.get("max_caclValue", 0.0)
            min_caclValue = item.get("min_caclValue", 0.0)

            sumlaborWorkTime = sumlaborWorkTime + laborWorkTime
            summax = summax + max_caclValue
            summin = summin + min_caclValue

            laborWorkTime = laborWorkTime + _value.get("laborWorkTime", 0.0)
            maxCaclValue = max_caclValue + _value.get("max_caclValue", 0.0)
            minCaclValue = min_caclValue + _value.get("min_caclValue", 0.0)
            tempTask[taskBid] = {
                "laborWorkTime": laborWorkTime,
                "max_caclValue": maxCaclValue,
                "min_caclValue": minCaclValue
            }
        print(json.dumps(tempTask))
        print(str(sumlaborWorkTime) + ":总   " + str(summax) + "：最大    " + str(summin) + ":最小")
        for taskbid in tempTask:
            item = tempTask[taskbid]
            laborWorkTime = item.get("laborWorkTime")
            max_caclValue = item.get("max_caclValue")
            min_caclValue = item.get("min_caclValue")
            tempTask[taskbid] = {
                "laborWorkTime": round((laborWorkTime/sumlaborWorkTime)*100, 2),
                "max_caclValue": round((max_caclValue/summax)*100, 2),
                "min_caclValue": round((min_caclValue/summin)*100, 2)
            }


        return tempTask

    @classmethod
    def select(cls, cid, didArr, taskBidArr, dayArr):
        if cid is None or len(cid) < 1 or didArr is None or len(didArr) < 1:
            return WebResult.errorCode(400, "cid or didArr is null")

        if dayArr is not None and len(dayArr) > 0:
            for day in dayArr:
                dayDate = DateUtils.transTime(day, "%Y-%m-%d")
                if dayDate is None:
                    return WebResult.errorCode(400, "day format error")

        result = LaborCaclValueModel.select(cid, didArr, taskBidArr, dayArr)
        if result is None:
            return WebResult.errorCode(400, "select data is error")

        if len(result) < 1:
            return WebResult.successResult("select data is empty")

        dayToItems = CollectionUtils.group(result, "dayStr")

        resultData = {}

        for day in dayToItems:
            items = dayToItems.get(day)
            timeToTask = {}
            resultData[day] = timeToTask
            for item in items:
                startTimeStr = item.get("startTimeStr", "null")
                endTimeStr = item.get("endTimeStr", "null")
                taskBid = item.get("taskBid", "null")
                minCaclValue = item.get("min_caclValue", None)
                maxCaclValue = item.get("max_caclValue", None)
                businessValue = cls.getBusinessValue(item)

                timekey = startTimeStr + "-" + endTimeStr
                detail = timeToTask.get(timekey, {})
                detail[taskBid] = {
                    "value": businessValue,
                    "scope": [minCaclValue, maxCaclValue]
                }
                timeToTask[timekey] = detail
        return WebResult.successData(resultData)

    @classmethod
    def getBusinessValue(cls, item):
        # 修改 - 预测 - 计算
        caclValue = item.get("caclValue", None)
        forecastValue = item.get("forecastValue", None)
        editValue = item.get("editValue", None)

        if editValue is not None and editValue > 0:
            return editValue
        elif forecastValue is not None and forecastValue > 0:
            return forecastValue
        elif caclValue is not None and caclValue > 0:
            return caclValue
        else:
            return None







