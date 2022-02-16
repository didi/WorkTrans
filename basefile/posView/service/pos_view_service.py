#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: pos_view_service.py
@time: 2020/4/13 11:38
@desc:
'''
import json
from typing import List

from posView.model.pos_view_model import PosViewModel
from utils.collectionUtils import CollectionUtils
from utils.dateUtils import DateUtils
from utils.webResult import WebResult


class PosViewService:

    @classmethod
    def select(cls, cid: str, didArr: List[str], startTime: str, endTime: str):
        if cid is None or len(cid) < 1 or didArr is None or len(didArr) < 1:
            return WebResult.errorCode(400, "cid or didArr is null")

        _startTime = DateUtils.transTime(startTime, "%Y-%m-%d")
        _endTime = DateUtils.transTime(endTime, "%Y-%m-%d")
        if _startTime is None or _endTime is None:
            return WebResult.errorCode(400, "startTime or endTime format error")

        result = PosViewModel.select(cid, didArr, startTime + " 00:00", endTime + " 23:59")
        if result is None:
            return WebResult.errorCode(400, "select data  error")
        if len(result) < 1:
            return WebResult.errorCode(400, "select data empty")

        didToItems = CollectionUtils.group(result, "did")
        resultData = {}

        for did in didToItems:
            didItems = didToItems.get(did)
            shikeToItems = {}
            resultData[did] = shikeToItems
            for _didItems in didItems:
                shike = _didItems.get("shike", "null")
                businessGMV = cls.getBusiness(_didItems, "GMV")
                businessOrders = cls.getBusiness(_didItems, "Orders")
                businessPeoples = cls.getBusiness(_didItems, "Peoples")
                shikeToItems[shike] = {
                    "GMV":businessGMV,
                    "order": businessOrders,
                    "peoples": businessPeoples
                }
        print(resultData)
        return WebResult.successData(resultData)



    @classmethod
    def getBusiness(cls, _didItems, param):
        if _didItems is None or param is None:
            return None
        true = 'true' + param
        predict = 'predict' + param
        adjust = 'adjust' + param
        trueData = _didItems.get(true, None)
        predictData = _didItems.get(predict, None)
        adjustData = _didItems.get(adjust, None)

        if adjustData is not None and adjustData > 0:
           return adjustData
        elif predictData is not None and predictData > 0:
            return predictData
        elif trueData is not None and trueData > 0:
            return predictData
        else:
            return None


