# !/usr/bin/env python
# -*- coding:utf-8 -*-

from forecastPOS.model.querySettingsDB import QuerySettingsDBModel




class QuerySettingsDBService():

    def setQuerySettings(self, cid,companyName,periodicType,weekIndex,startDay,dayCount,note,effectStartDate,EffectEndDate):
     return QuerySettingsDBModel.setQuerySettings(self, cid,companyName,periodicType,weekIndex,startDay,dayCount,note,effectStartDate,EffectEndDate)