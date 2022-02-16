#!/usr/bin/env python
# encoding: utf-8
"""
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: goods_statistics_service.py
@time: 2020/3/3 15:27
@desc:
"""

import datetime
import json

from utils import MathUtils
from utils.webResult import WebResult
from viewGoodsDf.service.view_goods_service import ViewGoodsService


class GoodsStatisticsService:

    @classmethod
    def getCidFromGoods(cls):
        cids = ViewGoodsService.getCid()
        data = []
        for item in cids:
            data.append(item['cid'])

        return WebResult.successData(data)

    @classmethod
    def getDidFromGoods(cls, cid: str):
        if cid is None or len(cid) < 1:
            return WebResult.errorResult("参数不正确")
        dids = ViewGoodsService.getDid(cid)
        data = []
        for item in dids:
            data.append(item['did'])

        return WebResult.successData(data)

    @classmethod
    def getGoodsBid(cls, cid: str, did: int):
        if cid is None or len(cid) < 1 or did is None or did < 1:
            return WebResult.errorResult("参数不正确")

        goodsBids = ViewGoodsService.getGoodsBids(cid, did)
        data = []
        for item in goodsBids:
            data.append(item['goods_bid'])

        return WebResult.successData(data)

    @classmethod
    def dataAnalysis(cls, cid: str, did: int, type: str, goodsBid: str, startTime: str, endTime: str, restrictTime: str):
        """
        根据查询 条件获取对应的数值统计 不需要分页
        :param cid:
        :param did:
        :param type:  GMV, peoples, orders
        :param goodsBid: "123"
        :param startTime: "2020-03-03"
        :param endTime: "2020-03-04"
        :param restrictStart: "08:00" or None(全部)
        :param restrictEnd: "12:00" or None(全部)
        :return:
        """

        checkResult = GoodsStatisticsService.checkCalTrendParam(cid, did, type, startTime, endTime, restrictTime)

        if checkResult is not None:
            return checkResult

        result = {}

        if restrictTime is not None:
            # 增加了限制
            dates = []
            cls.getDates(dates, endTime, startTime)
            shikes = cls.dates2Shike(dates, restrictTime)
            listsResult = ViewGoodsService.listByShikes(cid, did, goodsBid, shikes, None, None)

        else:
            listsResult = ViewGoodsService.listByShike(cid, did, goodsBid, startTime, endTime, False, None, None)

        if listsResult is None or len(listsResult["data"]) < 1:
            return WebResult.errorResult("无数据")

    #      循环 lists 根据 shike 对应四个 值， 真实，预测， 修改，业务  根据不同的值去计算  整理每一个对应list

        result = {}

        calGMV = type == "GMV"
        calPeoples = type == "peoples"
        calOrders = type == "orders"
        lists = listsResult["data"]
        detail = {}
        for item in lists:
            shike = item.get("shike")

            trueData = 0
            predict = 0
            adjust = 0
            if calGMV:
                trueData = item.get("true_gmv", 0)
                predict = item.get("predict_gmv", 0)
                adjust = item.get("adjust_gmv", 0)
            elif calPeoples:
                trueData = item.get("true_peoples", 0)
                predict = item.get("predict_peoples", 0)
                adjust = item.get("adjust_peoples", 0)
            elif calOrders:
                trueData = item.get("true_orders", 0)
                predict = item.get("predict_orders", 0)
                adjust = item.get("adjust_orders", 0)
            calData = result.get(shike, None)

            businessVal = cls.getBusinessVal(trueData, predict, adjust)
            isNew = calData is None

            calData = cls.getCalData(adjust, businessVal, calData, predict, trueData)

            calData, _result = cls.getAnalysisCalData(adjust, businessVal, calData, isNew, predict, trueData)

            result[shike] = calData
            businessValResult = _result["businessValResult"]
            businessValResult["date"] = shike
            detail[shike] = businessValResult
            # 3.10号修改只要业务数据
            # calTrueDataArr = []
            # calPredictArr = []
            # calAdjustArr = []
            calBusinessValArr = []
            # 以时间点位单位 整合数据数组
            for key in result:
                timeItem = result.get(key)
                # timeTrueData = timeItem.get("trueData")
                # timePredict = timeItem.get("predict")
                # timeAdjust = timeItem.get("adjust")
                timeBusinessVal = timeItem.get("businessVal")
                # calTrueDataArr.append(timeTrueData)
                # calPredictArr.append(timePredict)
                # calAdjustArr.append(timeAdjust)
                calBusinessValArr.append(timeBusinessVal)

        # trueDataResult = cls.statistical_combination(calTrueDataArr)
        # predictResult = cls.statistical_combination(calPredictArr)
        # adjustResult = cls.statistical_combination(calAdjustArr)
        businessValResult = cls.statistical_combination(calBusinessValArr)

        return WebResult.successData({
                # "trueData": trueDataResult,
                # "predict": predictResult,
                # "adjust": adjustResult,
                "businessData": businessValResult,
                "detail": detail
            })





    @classmethod
    def getAnalysisCalData(cls, adjust, businessVal, calData, isNew, predict, trueData):
        """
        整理数据 calDdata 基础上 把相加数据统计到数组里边   dataAnalysis 专用方法
        :param adjust: 手动调整数据
        :param businessVal: 业务数据
        :param calData: 循环数据容器
        :param isNew: 当前循环体内是否为新数据
        :param predict: 预测数据
        :param trueData: 真实数据
        :return:  3月 10 号修改只要业务数据
        """
        # _trueDataArr = []
        # _predictArr = []
        # _adjustArr = []
        _businessValArr = []
        result = {}
        if isNew:
            # _trueDataArr = [trueData]
            # _predictArr = [predict]
            # _adjustArr = [adjust]
            _businessValArr = [businessVal]
        else:

            # _trueDataArr = calData.get("trueDataArr", [])
            # _trueDataArr.append(trueData)
            # _predictArr = calData.get("predictArr", [])
            # _predictArr.append(predict)
            # _adjustArr = calData.get("adjustArr", [])
            # _adjustArr.append(adjust)
            _businessValArr = calData.get("businessValArr", [])
            _businessValArr.append(businessVal)

        # calData["trueDataArr"] = _trueDataArr
        # calData["predictArr"] = _predictArr
        # calData["adjustArr"] = _adjustArr
        calData["businessValArr"] = _businessValArr

        # trueDataResult = cls.statistical_combination(_trueDataArr)
        # predictResult = cls.statistical_combination(_predictArr)
        # adjustResult = cls.statistical_combination(_adjustArr)
        businessValResult = cls.statistical_combination(_businessValArr)

        # result["trueDataResult"] = trueDataResult
        # result["predictResult"] = predictResult
        # result["adjustResult"] = adjustResult
        result["businessValResult"] = businessValResult

        return calData, result

    @classmethod
    def getCalData(cls, adjust, businessVal, calData, predict, trueData):
        """

        :param adjust: 调整数据
        :param businessVal: 业务数据
        :param calData: 循环数据容器
        :param predict: 预测数据
        :param trueData: 真实数据
        :return: 如果 calData 存在， 各类型数据 ++ ， 如果不存在世界赋值返回对应格式
        """
        if calData is None:

            calData = {
                "trueData": trueData,
                "predict": predict,
                "adjust": adjust,
                "businessVal": businessVal
            }
        else:
            _trueData = calData.get("trueData", 0)
            _predict = calData.get("predict", 0)
            _adjust = calData.get("adjust", 0)
            _businessVal = calData.get("businessVal", 0)
            calData["trueData"] = trueData + _trueData
            calData["predict"] = predict + _predict
            calData["adjust"] = adjust + _adjust
            calData["businessVal"] = businessVal + _businessVal
        return calData

    @classmethod
    def calTrend(cls, cid: str, did: int, type: str, goodsBid: str, startTime: str, endTime: str, restrictTime: str, page: int, size: int):
        """
        根据查询 条件获取对应的数值统计
        :param cid:
        :param did:
        :param type:  GMV, peoples, orders
        :param goodsBid: "123"
        :param startTime: "2020-03-03"
        :param endTime: "2020-03-04"
        :param restrictStart: "08:00" or None(全部)
        :param restrictEnd: "12:00" or None(全部)
        :return:
        """

        checkResult = GoodsStatisticsService.checkCalTrendParam(cid, did, type, startTime, endTime, restrictTime)

        if checkResult is not None:
            return checkResult

        result = {}

        if page is None or page < 0:
            page = 0
        if size is None or size < 0:
            size = 0

        if restrictTime is not None:
            # 增加了限制
            dates = []
            cls.getDates(dates, endTime, startTime)
            shikes = cls.dates2Shike(dates, restrictTime)
            listsResult = ViewGoodsService.listByShikes(cid, did, goodsBid, shikes, page, size)

        else:
            listsResult = ViewGoodsService.listByShike(cid, did, goodsBid, startTime, endTime, False, page, size)

        calGMV = type == "GMV"
        calPeoples = type == "peoples"
        calOrders = type == "orders"

        if listsResult is None or len(listsResult["data"]) < 1:
            return WebResult.errorResult("无数据")
        lists = listsResult["data"]
        count = listsResult["count"]
        for item in lists:
            shike = item.get("shike")
            trueData = 0
            predict = 0
            adjust = 0
            if calGMV:
                trueData = item.get("true_gmv", 0)
                predict = item.get("predict_gmv", 0)
                adjust = item.get("adjust_gmv", 0)
            elif calPeoples:
                trueData = item.get("true_peoples", 0)
                predict = item.get("predict_peoples", 0)
                adjust = item.get("adjust_peoples", 0)
            elif calOrders:
                trueData = item.get("true_orders", 0)
                predict = item.get("predict_orders", 0)
                adjust = item.get("adjust_orders", 0)
            calData = result.get(shike, None)

            businessVal = cls.getBusinessVal(trueData, predict, adjust)

            calData = cls.getCalData(adjust, businessVal, calData, predict, trueData)
            calData["date"] = shike
            result[shike] = calData
        # result["count"] = count
        return WebResult.successData(result, count)

    @classmethod
    def getDates(cls, dates, endTime, startTime):
        """
        private 专用方法
        :param dates: 存放日期数组容器
        :param endTime: 结束时间
        :param startTime: 开始时间
        :return: 开始时间 结束时间对应 其中每一天的数组
        """
        datestart = datetime.datetime.strptime(startTime, '%Y-%m-%d')
        dateend = datetime.datetime.strptime(endTime, '%Y-%m-%d')
        while datestart <= dateend:
            dates.append(datestart)
            datestart += datetime.timedelta(days=1)

    @classmethod
    def checkCalTrendParam(cls, cid, did, type, startTime, endTime, restrictTime):
        """
        统计查询条件检查方法
        :param cid: 必填
        :param did: 必填
        :param type: 必填
        :param startTime: 必填 yyyy-MM-dd
        :param endTime: 必填 yyyy-MM-dd
        :param restrictTime: 非必填 hh:mm
        :return: None 校验通过， "长度大于1" 校验异常
        """
        result = []
        if cid is None or len(cid) < 1 or did is None or type is None or startTime is None or endTime is None:
            result.append("cid, did, type, startTime, endTime 不能为空")

        if type not in ["GMV", "peoples", "orders"]:
            result.append("type 类型不正确")

        try:
            datetime.datetime.strptime(startTime, '%Y-%m-%d')
            datetime.datetime.strptime(endTime, '%Y-%m-%d')

        except ValueError:
            result.append("startTime, endTime 格式不正确")
        # 分开判断 支持单个传递
        if restrictTime is not None:

            try:
                datetime.datetime.strptime(restrictTime, '%H:%M')

            except ValueError:
                result.append("restrictEnd 格式不正确")

        if len(result) < 1:
            return None

        return WebResult.errorResult( ','.join(item for item in result))

    @classmethod
    def dates2Shike(cls, dates, restrictTime):
        """

        :param dates: 日期容器
        :param restrictTime: hh:mm
        :return: 日期 + hh:mm 数组返回
        """
        if dates is None or restrictTime is None:
            return None
        shikes = []
        for date in dates:
            shikes.append(date.strftime('%Y-%m-%d') + " " + restrictTime)
        return shikes

    @classmethod
    def getBusinessVal(cls, trueData, predict, adjust):
        """
        获取业务数据   优先 调整 - 预测 - 真实
        :param trueData:
        :param predict:
        :param adjust:
        :return:
        """
        businessVal = 0
        if adjust > 0:
            businessVal = adjust
        elif predict > 0:
            businessVal = predict
        elif trueData > 0:
            businessVal = trueData

        return businessVal


    @classmethod
    def statistical_combination(cls, arr):
        """
        计算统计数据
        :param arr: [数据对应数组]
        :return:
        """
        # 为零个数
        zeroNum = MathUtils.get_zero_num(arr)
        # 中位数
        median = format(MathUtils.get_median(arr),'.2f')
        # 平均值
        ave = format(MathUtils.get_average(arr),'.2f')
        # 方差
        variance = format(MathUtils.get_variance(arr),'.2f')
        # 25%

        Q1 = MathUtils.percentile(arr, 25)
        # 50%
        Q2 = MathUtils.percentile(arr, 50)
        # 75%
        Q3 = MathUtils.percentile(arr, 75)

        # 大于百分比 80%
        gtEighty = MathUtils.percentile_more_count(arr, 80)

        # 小于百分比 20%
        ltTwenty = MathUtils.percentile_less_count(arr, 20)

        # 大于百分比 90%
        gtNinety = MathUtils.percentile_more_count(arr, 90)

        # 小于百分比 10%
        ltTen = MathUtils.percentile_less_count(arr, 10)

        # 大于百分比 95%
        gtNinetyFive = MathUtils.percentile_more_count(arr, 95)

        # 小于百分比 5%
        ltFive = MathUtils.percentile_less_count(arr, 5)

        return cls.makeUp(len(arr), zeroNum, median, ave, variance, Q1, Q2, Q3, gtEighty, ltTwenty, gtNinety, ltTen, gtNinetyFive,
                          ltFive)

    @classmethod
    def makeUp(cls, count, zeroNum, median, ave, variance, Q1, Q2, Q3, gtEighty, ltTwenty, gtNinety, ltTen,
               gtNinetyFive, ltFive):
        """
        组合前端需要格式
        :param count:
        :param zeroNum:
        :param median:
        :param ave:
        :param variance:
        :param Q1:
        :param Q2:
        :param Q3:
        :param gtEighty:
        :param ltTwenty:
        :param gtNinety:
        :param ltTen:
        :param gtNinetyFive:
        :param ltFive:
        :return:
        """
        return {
            # // 总数
            "count": count,
            # // 为零个数
            "zeroNum": zeroNum,
            # // 四分数 25%
            "quartileQ1": Q1,
            # 50%
            "quartileQ2": Q2,
            # 75%
            "quartileQ3": Q3,
            # // 平均
            "average": ave,
            # // 中位
            "median": median,
            # // 方差
            "variance": variance,
            # // 大于80 % 个数
            "gtEighty": gtEighty,
            # // 小于 20 %
            "ltTwenty": ltTwenty,
            # // 大于90 %
            "gtNinety": gtNinety,
            # // 小于10 %
            "ltTen": ltTen,
            # // 大于95 %
            "gtNinetyFive": gtNinetyFive,
            # // 小于5 %
            "ltFive": ltFive
            # 为零个数
        }



if __name__ == '__main__':
    # print(GoodsStatisticsService.getGoodsBid("123456", 1))

    {
        "cid": "123456",
        "did": 12,
        "type": "GMV",
        "goods": None,
        "startTime": "2020-03-03",
        "endTime": "2020-03-04",
        "restrictStart": None,
        "restrictEnd": None
    }
    print(GoodsStatisticsService.dataAnalysis("123456", 1, "GMV", None, "2020-03-01", "2020-03-12",  None))
    # shikes = ["2018-02-03 12:00", "2018-02-03 13:00"]
    # print(tuple(shikes))

