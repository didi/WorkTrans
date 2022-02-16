#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: goods_statistics_handle.py
@time: 2020/3/5 16:40
@desc:
'''
import json

from tornado.web import RequestHandler

from base.service.base_service import BaseService
from utils.authenticated import  authenticated
from utils.webResult import WebResult
from utils.myLogger import infoLog
from viewGoodsDf.service.goods_statistics_service import GoodsStatisticsService


class GoodsStatisticsHandle(RequestHandler):

    def post(self, route, *args, **kwargs):
        infoLog.info('handler name: %s; route: %s; request body: %s' % (str("GoodsStatisticsHandle"), str(route), str(self.request.body.decode('utf-8')).replace('\n', '')))
        if route == "getCid":
            self.write(self.getCid().__str__())
        elif route == 'getDid':
            self.write(self.getDid().__str__())
        elif route == 'getGoods':
            self.write(self.getGoods().__str__())
        elif route == 'calTrend':
            self.write(self.calTrend().__str__())
        elif route == 'calAnalysis':
            self.write(self.calAnalysis().__str__())
        else:
            self.write(WebResult.errorCode(404, "请求不存在").__str__())

    @authenticated(verify_is_admin=False, role=["滴滴", "喔趣"])
    def getCid(self):
        """
        不用传递参数直接请求
        :return:
        """

        return BaseService.getCids("view_goods_df")

    @authenticated(role=["滴滴", "喔趣"])
    def getDid(self):
        """
        {"cid", "123456"}
        :return:
        """
        try:
            req = json.loads(self.request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return WebResult.errorResult("json 解析失败")
        cid = req.get("cid", None)
        if cid is None:
            return WebResult.errorResult("cid 必传")
        return BaseService.getDids("view_goods_df", cid)

    @authenticated(role=["滴滴", "喔趣"])
    def getGoods(self):

        try:
            req = json.loads(self.request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return WebResult.errorResult("json 解析失败")
        cid = req.get("cid", None)
        did = req.get("did", None)
        if cid is None or did is None:
            return WebResult.errorResult("cid 或则 did 必传")

        return GoodsStatisticsService.getGoodsBid(cid, did)

    @authenticated(role=["滴滴", "喔趣"])
    def calTrend(self):
        try:
            req = json.loads(self.request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return WebResult.errorResult("json 解析失败")

        cid = req.get("cid", None)
        did = req.get("did", None)
        type = req.get("type", None)
        goods = req.get("goods", None)
        startTime = req.get("startTime", None)
        endTime = req.get("endTime", None)
        restrictTime = req.get("restrictTime", None)
        page = req.get("page", None)
        size = req.get("size", None)

        status, msg = self.checkCalTrendPram(cid, did, type, startTime, endTime)

        if not status:
            return WebResult.errorResult(msg)

        return GoodsStatisticsService.calTrend(cid, did, type, goods, startTime, endTime, restrictTime, page, size)

    @authenticated(role=["滴滴", "喔趣"])
    def calAnalysis(self):
        try:
            req = json.loads(self.request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return WebResult.errorResult("json 解析失败")

        cid = req.get("cid", None)
        did = req.get("did", None)
        type_ = req.get("type_", None)
        goods = req.get("goods", None)
        start_time = req.get("startTime", None)
        end_time = req.get("endTime", None)
        restrict_time = req.get("restrictTime", None)

        status, msg = self.checkCalTrendPram(cid, did, type_, start_time, end_time)

        if not status:
            return WebResult.errorResult(msg)

        return GoodsStatisticsService.dataAnalysis(cid, did, type_, goods, start_time, end_time, restrict_time)

    @authenticated(role=["滴滴", "喔趣"])
    def checkCalTrendPram(self, cid, did, type, startTime, endTime):
        if cid is None or did is None or type is None or startTime is None or endTime is None:
            return False, "cid, did, type, startTime, endTime 不能为空"
        return True, ""

