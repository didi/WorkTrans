#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: sch_available_time_service.py
@time: 2020/3/20 16:10
@desc:
'''
from typing import List

from schAvailableTime.model.sch_available_time_model import SchAvailableTimeModel
from utils.collectionUtils import CollectionUtils
from utils.webResult import WebResult


class SchAvailableTimeService:

    @classmethod
    def list(cls, cid: str, eid: int, page: int, size: int):

        if cid is None or len(cid) < 1:
            return WebResult.errorResult("cid 必填")
        if page is None or page < 0:
            page = 0
        if size is None or size < 0:
            size = 5

        result = SchAvailableTimeModel.query(cid, eid, page, size)

        if result is None:
            return WebResult.errorResult("查询失败")

        datas = result.get("data", None)
        count = result.get("count", None)

        return WebResult.successData(datas if (datas is not None and len(datas) > 0) else [], count)

    @classmethod
    def select(cls, cid: str, eidArr: List[int], dayArr: List[str]):
        if cid is None or len(cid) < 1 or eidArr is None or len(eidArr) < 1:
            return WebResult.errorCode(400, "cid eidArr 必填")

        result = SchAvailableTimeModel.select(cid, eidArr, dayArr)
        if result is None:
            return WebResult.errorCode(400, "未成功获取数据")

        if len(result) < 1:
            return WebResult.successResult("无数据")

        return cls.transData(result)

    @classmethod
    def transData(cls, result):
        """
        :param result:
        :return:
        """
        daytoItem = CollectionUtils.group(result, 'day')

        if daytoItem is None:
            return WebResult.errorCode(400, "系统异常")
        oneItem = {}
        for day in daytoItem:
            itemList = daytoItem.get(day, None)
            avList = []
            if itemList is None:
                continue
            for item in itemList:
                avList.append({
                    "day": item.get("day", None),
                    "eid": item.get("eid", None),
                    "opt": item.get("opt", None),
                    "type": item.get("type", None),
                    "start": item.get("start", None),
                    "end": item.get("end", None)
                })
            oneItem[day] = avList
        return WebResult.successData(oneItem)


if __name__ == '__main__':
    req={"dayArr":["2019-10-09"],"eidArr":[265],"cid":"1","timestr":"2020-08-06 20:48:56.019","token":"2e83b462981ea30417673ee1f0a7b317"}
    cid = req.get("cid", None)
    eid_arr = req.get("eidArr", None)
    day_arr = req.get("dayArr", None)
    print(SchAvailableTimeModel.select(cid, eid_arr, day_arr))