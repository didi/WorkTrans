#!/usr/bin/env python
# encoding: utf-8


from utils.myLogger import infoLog


class SettingsHandler(tornado.web.RequestHandler):

    def post(self):
        raw_data = self.request.body
        '''
        m = str(raw_data, encoding="utf-8")
        paramDict = {}
        for a in m.split('&'):
            p, k = a.split('=')
            paramDict[p] = k
        print('paramDict', paramDict)

        cid=paramDict.get('cid',None) #是	string	客户公司id
        companyName = paramDict.get('companyName', None)  # 否	string	客户公司名称
        data = paramDict.get('data', None)  # array	pos具体数据

        did = paramDict.get('did', None)  # 是	String	部门id（组织id，或者门店id）
        gmtBill=paramDict.get('gmtBill', None) #是	String	开单时间
        gmtTurnover = paramDict.get('gmtTurnover', None)  #否	String	营业结算时间

        money = paramDict.get('money', None)  # 是	String	营业额
        peoples = paramDict.get('peoples', None)  # 否	Integer	人数
        singleSales = paramDict.get('singleSales', None)  #否	Integer	单品销量
        payment = paramDict.get('payment', None)  # 否	String	结算方式
        deviceCode = paramDict.get('deviceCode', None)  # 否	String	收银设备号
        orderNo = paramDict.get('orderNo', None)  #否	String	订单号
        '''

        infoLog.info('raw_data:%s' % raw_data)

        save_result = {'code': 100, 'result': 'success'}

        # todo : res=QuerySettingsDBService.setQuerySettings()
        self.write(save_result)
