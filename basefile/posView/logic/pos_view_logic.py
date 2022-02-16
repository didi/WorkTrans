#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: pos_view_logic.py
@time: 2020/4/13 11:37
@desc:
'''
import json

from tornado.web import RequestHandler

from posView.service.pos_view_service import PosViewService
from utils.apiFilter import apiFilter
from utils.webResult import WebResult
from utils.myLogger import infoLog


class PosViewHandler(RequestHandler):

    def post(self, route, *args, **kwargs):
        infoLog.info('handler name: %s; route: %s; request body: %s' %(str("PosViewHandler"), str(route),
                     str(self.request.body.decode('utf-8')).replace('\n', '')))
        if route == "select":
            self.write(self.select().__str__())
        else:
            self.write(WebResult.errorCode(404, "请求不存在").__str__())

    @apiFilter()
    def select(self):
        try:
            req = json.loads(self.request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return WebResult.errorResult("json 解析失败")
        cid = req.get("cid", None)
        did_arr = req.get("didArr", None)
        start_time = req.get("startTime", None)
        end_time = req.get("endTime", None)
        return PosViewService.select(cid, did_arr, start_time, end_time)
