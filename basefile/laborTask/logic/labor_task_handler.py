#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: labor_task_handler.py
@time: 2020/3/13 16:50
@desc:
'''
import json

from tornado.web import RequestHandler

from laborTask.service.labor_task_service import LaborTaskService
from utils.apiFilter import apiFilter
from utils.authenticated import authenticated
from utils.webResult import WebResult
from utils.myLogger import infoLog




class LaborTaskHandler(RequestHandler):

    def post(self, route, *args, **kwargs):
        infoLog.info('handler name: %s; route: %s; request body: %s' % (
            str("LaborTaskHandler"), str(route), str(self.request.body.decode('utf-8')).replace('\n', '')))
        if route == "list":
            self.write(self.list().__str__())
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
        page = req.get("page", None)
        size = req.get("size", None)
        return LaborTaskService.list(cid, did, page, size)

    @apiFilter()
    def select(self):
        try:
            req = json.loads(self.request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return WebResult.errorResult("json 解析失败")
        cid = req.get("cid", None)
        did = req.get("did", None)
        bid_arr = req.get("bidArr", None)
        return LaborTaskService.select(cid, did, bid_arr)


