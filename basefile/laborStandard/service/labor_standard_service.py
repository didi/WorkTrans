#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: labor_standard_service.py
@time: 2020/3/13 17:14
@desc:
'''
from typing import List

from laborStandard.model.labor_standard_model import LaborStandardModel
from utils.collectionUtils import CollectionUtils
from utils.webResult import WebResult


class LaborStandardService:

    @classmethod
    def list(cls, cid: str, page: int, size: int):

        if cid is None or len(cid) < 1:
            return WebResult.errorResult("cid did 必填")
        if page is None or page < 0:
            page = 0
        if size is None or size < 0:
            size = 5

        result = LaborStandardModel.query(cid, page, size)

        if result is None:
            return WebResult.errorResult("查询失败")

        datas = result.get("data", None)
        count = result.get("count", None)

        return WebResult.successData(datas if (datas is not None and len(datas) > 0) else [], count)

    @classmethod
    def listForBidArr(cls, cid, bidArr: List[str]):
        if cid is None or len(cid) < 1:
            return WebResult.errorCode(400, "cid 必填")

        result = LaborStandardModel.listForBidArr(cid, bidArr)
        if result is None:
            return WebResult.errorCode(400, "未成功获取数据")

        if len(result) < 1:
            return WebResult.successResult("无数据")
        return cls.transData(result)

    @classmethod
    def transData(cls, result):
        """
        {
        "cid": "123456",

        "bid":"201903291236271250271007959f0211",
        "mode":"single",

        "masterType":"turnover",

        "slaveType":"",

        "detailArr":[

            {

                "detailRank":1,

                "masterTypeScale":"100",

                "masterTypeMinScale":"0",

                "slaveTypeScale":"",

                "slaveTypeMinScale":"",

                "worktimeMinute":15

            }
        ]
        }
        :param result:
        :return:
        """

        bidToList = CollectionUtils.group(result, "bid")
        if bidToList is None:
            return WebResult.errorCode(400, "系统异常")
        resultData = []
        for bid in bidToList:
            datas = bidToList.get(bid)
            if datas is None or len(datas) < 1:
                continue
            sameBidToDetail = {
                "cid": None,
                "bid": None,
                "mode": None,
                "masterType": None,
                "slaveType": None,
            }
            detailArr = []
            for item in datas:

                cls.setK(item, sameBidToDetail, "cid")
                cls.setK(item, sameBidToDetail, "bid")
                cls.setK(item, sameBidToDetail, "mode")
                cls.setK(item, sameBidToDetail, "masterType")
                cls.setK(item, sameBidToDetail, "slaveType")
                masterTypeMaxScale = item.get("masterTypeScale", None)
                masterTypeMinScale = item.get("masterTypeMinScale", None)
                slaveTypeMaxScale = item.get("slaveTypeScale", None)
                slaveTypeMinScale = item.get("slaveTypeMinScale", None)
                detailArr.append({
                    "detailRank": item.get("detailRank", None),
                    "masterTypeScale": masterTypeMaxScale,
                    "masterTypeMinScale": masterTypeMinScale,
                    "slaveTypeScale": slaveTypeMaxScale,
                    "slaveTypeMinScale": slaveTypeMinScale,
                    "worktimeMinute": item.get("worktimeMinute", None)
                })
            sameBidToDetail["detailArr"] = detailArr
            resultData.append(sameBidToDetail)
        return WebResult.successData(resultData)


    @classmethod
    def setK(cls, item, sameBidToDetail, k):
        v = sameBidToDetail.get(k)
        if v is None:
            itemV = item.get(k, None)
            if itemV is not None:
                sameBidToDetail[k] = itemV
                # sameBidToDetail.update(k, itemV)

