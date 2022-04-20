#!/usr/bin/env python
# encoding: utf-8
"""
@author: pengyd
@file: task_view_handler.py
@time: 2020/3/19 10:40
@desc:
"""
import json
from abc import ABC

from laborTaskView.service.task_view_service import TaskViewService
from utils.apiFilter import apiFilter
from utils.authenticated import authenticated
from utils.webResult import WebResult
from utils.myLogger import infoLog


class TaskViewHandler(RequestHandler, ABC):

    def post(self, route, *args, **kwargs):
        infoLog.info('handler name: %s; route: %s; request body: %s' % (
            str("TaskViewHandler"), str(route), str(self.request.body.decode('utf-8')).replace('\n', '')))
        if route == "list":
            self.write(self.list().__str__())
        elif route == "select":
            self.write(self.select().__str__())
        else:
            self.write({"code": 404, "result": "请求不存在"})

    @authenticated(role=["滴滴", "喔趣"])
    def list(self):
        """
         {"cid":"123456", "did":1, "date":"2019-02-09"}
        :return:
        """
        try:
            req = json.loads(self.request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return WebResult.errorResult("json 解析失败")
        cid = req.get("cid", None)
        date = req.get("date", None)
        did = req.get("did", None)
        page = req.get("page", None)
        size = req.get("size", None)
        t_type = req.get("type", None)
        return TaskViewService.list(cid, did, date, t_type, page, size)

    @apiFilter()
    def select(self):
        """
         {"cid":"123456", "did":1, "date":"2019-02-09"}
        :return:
        """
        try:
            req = json.loads(self.request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return WebResult.errorResult("json 解析失败")
        cid = req.get("cid", None)
        did = req.get("did", None);
        did_arr = None
        if did is not None:
            did_arr = [did]
        forecast_type = req.get("forecastType", None)
        start_date = req.get("startDate", None)
        end_date = req.get("endDate", None)
        return TaskViewService.select(cid, did_arr, forecast_type, start_date, end_date)



