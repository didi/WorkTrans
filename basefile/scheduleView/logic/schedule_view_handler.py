#!/usr/bin/env python
# encoding: utf-8
"""
@author: pengyd
@file: schedule_view_handler.py
@time: 2020/3/25 17:14
@desc:
"""
import json
from abc import ABC


from scheduleView.service.schedule_view_service import ScheduleViewService
from utils.authenticated import authenticated
from utils.webResult import WebResult
from utils.myLogger import infoLog


class ScheduleViewHandler(RequestHandler, ABC):

    def post(self, route, *args, **kwargs):
        infoLog.info('handler name: %s; route: %s; request body: %s' % (
            str("ScheduleViewHandler"), str(route), str(self.request.body.decode('utf-8')).replace('\n', '')))
        if route == "list":
            print(self.list().__str__())
            self.write(self.list().__str__())
        elif route == "getApplyId":
            self.write(self.getApplyId().__str__())
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
        date_str = req.get("date_str", None)
        apply_id = req.get("apply_id", None)
        scheme_type = req.get("scheme_type", None)
        return ScheduleViewService.list(cid, did, date_str, apply_id, scheme_type)

    @authenticated(role=["滴滴", "喔趣"])
    def getApplyId(self):
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
        return ScheduleViewService.getApplyId(cid, did)
