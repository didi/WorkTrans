#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: labor_cacl_value_handler.py
@time: 2020/3/16 13:28
@desc:
'''
import json

from tornado.web import RequestHandler

from laborCaclValue.service.labor_cacl_value_service import LaborCaclValueService
from utils.authenticated import authenticated
from utils.webResult import WebResult
from utils.myLogger import infoLog


class LaborCaclValueHandler(RequestHandler):

    def post(self, route, *args, **kwargs):
        infoLog.info('handler name: %s; route: %s; request body: %s' % (
            str("LaborCaclValueHandler"), str(route), str(self.request.body.decode('utf-8')).replace('\n', '')))
        if route == "list":
            self.write(self.list().__str__())
        elif route == "getlaborStandardBid":
            self.write(self.getlaborStandardBid().__str__())
        elif route == "getTaskBid":
            self.write(self.getTaskBid().__str__())
        elif route == "select":
            self.write(self.select().__str__())
        else:
            self.write(WebResult.errorCode(404, "请求不存在").__str__())

    @authenticated(role=["滴滴", "喔趣"])
    def list(self):
        """
         {"cid":"123456", "did":1}
        :return:
        """
        try:
            req = json.loads(self.request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return WebResult.errorResult("json 解析失败")
        cid = req.get("cid", None)
        did = req.get("did", None)
        labor_standard_bid = req.get("laborStandardBid", None)
        day = req.get("day", None)
        task_bid = req.get("taskBid", None)
        time = req.get("time", None)

        page = req.get("page", None)
        size = req.get("size", None)
        return LaborCaclValueService.list(cid, did, labor_standard_bid, day, task_bid, time, page, size)

    @authenticated(role=["滴滴", "喔趣"])
    def getlaborStandardBid(self):
        try:
            req = json.loads(self.request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return WebResult.errorResult("json 解析失败")
        cid = req.get("cid", None)
        did = req.get("did", None)
        return LaborCaclValueService.getlaborStandardBid(cid, did)

    @authenticated(role=["滴滴", "喔趣"])
    def getTaskBid(self):
        try:
            req = json.loads(self.request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return WebResult.errorResult("json 解析失败")
        cid = req.get("cid", None)
        did = req.get("did", None)
        labor_standard_bid = req.get("laborStandardBid", None)
        return LaborCaclValueService.getTaskBid(cid, did, labor_standard_bid)

    # @apiFilter()
    def select(self):
        try:
            req = json.loads(self.request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return WebResult.errorResult("json 解析失败")
        cid = req.get("cid", None)
        did_arr = req.get("didArr", None)
        task_bid_arr = req.get("taskBidArr", None)
        day_arr = req.get("dayArr", None)
        return LaborCaclValueService.select(cid, did_arr, task_bid_arr, day_arr)
