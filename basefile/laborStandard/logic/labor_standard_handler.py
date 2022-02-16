#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: labor_standard_handler.py
@time: 2020/3/13 17:14
@desc:
'''
import json
import traceback

from tornado.web import RequestHandler

from laborStandard.service.labor_standard_service import LaborStandardService
from utils.apiFilter import apiFilter
from utils.authenticated import authenticated
from utils.myLogger import infoLog
from utils.webResult import WebResult


class LaborStandardHandler(RequestHandler):

    def post(self, route, *args, **kwargs):
        infoLog.info('handler name: %s; route: %s; request body: %s' % (
            str("LaborStandardHandler"), str(route), str(self.request.body.decode('utf-8')).replace('\n', '')))
        if route == "list":
            self.write(self.list().__str__())
        elif route == "select":
            self.write(self.select().__str__())
        else:
            self.write(WebResult.errorCode(404, "请求不存在").__str__())

    @authenticated(role=["滴滴", "喔趣"])
    def list(self):
        """
         {"cid":"123456"}
        :return:
        """
        try:
            req = json.loads(self.request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return WebResult.errorResult("json 解析失败")
        cid = req.get("cid", None)
        page = req.get("page", None)
        size = req.get("size", None)
        return LaborStandardService.list(cid, page, size)

    @apiFilter()
    def select(self):
        """
         {"cid":"123456", "bidArr":1}
        :return:
        """
        try:
            req = json.loads(self.request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return WebResult.errorResult("json 解析失败")
        cid = req.get("cid", None)
        bid_arr = req.get("bidArr", None)

        try:
            return LaborStandardService.listForBidArr(cid, bid_arr)
        except Exception as e:
            infoLog.error(traceback.format_exc())
            return WebResult.errorCode(400, "系统异常")
