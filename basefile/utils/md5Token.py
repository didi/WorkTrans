# -*- coding: utf-8 -*-
import hashlib
import datetime


class Token():

    def getToken(self,timeStr):
        # 待加密信息
        appkey='c3d60ed77cd@ee94734@f9cf4180'
        appsecret='194c0006e2d#478d0f99705%216983ce06'
        str=("make token %s,%s,%s" %(appkey,appsecret,timeStr))



        # 创建md5对象
        m = hashlib.md5()

        # Tips
        # 此处必须encode
        # 若写法为m.update(str)  报错为： Unicode-objects must be encoded before hashing
        # 因为python3里默认的str是unicode
        # 或者 b = bytes(str, encoding='utf-8')，作用相同，都是encode为bytes
        b = str.encode(encoding='utf-8')
        m.update(b)
        str_md5 = m.hexdigest()
        #return str_md5

        #print('MD5加密前为 ：' + str)
        #print('MD5加密后为 ：' + str_md5)

        # 另一种写法：b‘’前缀代表的就是bytes
        #str_md5 = hashlib.md5(b'this is a md5 test.').hexdigest()
        #print('MD5加密后为 ：' + str_md5)
        return str_md5




if __name__ == '__main__':

    a = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

    b = Token().getToken(a)
    m = str({"token": b, "timestr": a}).replace(r"'", '"').replace(r"{", '').replace(r"}", '')
    print('\n',m,'\n')

    ip="127.0.0.1:8867"
    ip="ailabsservice.didi.cn"

    m1 = """
       curl -H "Content-Type:application/json" -X POST --data '{%s,"cid":"123456","datas":["11,2019-05-16 12:03:22,2019-05-16 12:03:33,280.00,13,3,80,SPA01,现金,A1,002847306ac359f6016ac3cdd4c10368","13,2019-06-16 12:05:22,2019-05-20 12:03:33,280.00,13,3,80,SPA01,现金,A1,002847306ac359f6016ac3cdd1111111"]}' http://%s/v2/pos/push
       """ % (m, ip)
    print('/v2/pos/push', m1)

    pos_push1 = """
        curl -H "Content-Type:application/json" -X POST --data '{%s,"cid":"123456","companyName":"北京奇点餐饮有限公司","data":[{"did":"11","gmtBill":"2019-05-16 12:03:22","gmtTurnover":"2019-05-16 12:03:33","money":"280.00","peoples":"3","singleSales":"80","payment":"现金","deviceCode":"A1","orderNo":"002847306ac359f6016ac3cdd4c10368"},{"did":"11","gmtBill":"2019-05-17 11:03:36","gmtTurnover":"2019-05-17 11:03:36","money":"170.50","peoples":"2","singleSales":"50","payment":"现金","deviceCode":"A1","orderNo":"002847306ac359f6016ac3beb3d602dc"}]}' http://%s/pos/push
        """ % (m, ip)
    print('/pos/push', pos_push1)

    m2 = """
    curl -H "Content-Type:application/json" -X POST --data '{%s,"cid":"123456","companyName":"北京奇点餐饮有限公司","data":[{"did":"11","gmtBill":"2019-05-16 12:03:22","gmtTurnover":"2019-05-16 12:03:33","money":"280.00","peoples":"3","singleSales":"80","payment":"现金","deviceCode":"A1","orderNo":"002847306ac359f6016ac3cdd4c10368"},{"did":"11","gmtBill":"2019-05-17 11:03:36","gmtTurnover":"2019-05-17 11:03:36","money":"170.50","peoples":"2","singleSales":"50","payment":"现金","deviceCode":"A1","orderNo":"002847306ac359f6016ac3beb3d602dc"}]}' http://%s/pos/modify
    """ % (m, ip)
    print('/pos/modify',m2)

    m3 = """
         curl -H "Content-Type:application/json" -X POST --data '{%s,"preType":"trueGMV","startDay":"2019-11-01","predictType":"CUSTOM","endDay":"2019-11-03","did":4954,"cid":50000031}' http://%s/pos/result
         """ % (m, ip)
    print('/pos/result', m3)


if 1==2:

    # m4 = """
    # curl -H "Content-Type:application/json" -X POST --data '{%s,"cid":"123456","didArr":[6,14],"changedDataArr":[{"forecastDate":"2019-07-29","startTimeStr":"00:00","endTimeStr":"00:15","forecastType":"trueGMV","forecastPosValue":"0.0","changedPosValue":"1080.50"},{"forecastDate": "2019-07-29","startTimeStr": "00:15","endTimeStr": "00:30","forecastType": "truePeoples","forecastPosValue": "0.0","changedPosValue": "4.00"}]}' http://%s/pos/forecastModify
    # """ % (m, ip)
    # print('/pos/forecastModify ',m4)

    m4 = """
        curl -H "Content-Type:application/json" -X POST --data '{%s,"cid":"123456","didArr":[6,14],"changedDataArr":[{"forecastDate":"2019-07-29","startTimeStr":"23:30","endTimeStr":"01:30","forecastType":"trueGMV","forecastPosValue":"0.0","changedPosValue":"1080.50"}]}' http://%s/pos/forecastModify
        """ % (m, ip)
    print('/pos/forecastModify ', m4)

    # 劳动力标准插入insert 14
    m414 = """
        curl -H "Content-Type:application/json" -X POST --data '{%s,"cid":"123456","did":14,"bid":"201903292247340840341012959f0010","operate_type":"insert","mode":"multi","masterType":"order_num","slaveType":"turnover","detailArr":[{"detailRank":1,"masterTypeScale":"10","slaveTypeScale":"100","worktimeMinute":15},{"detailRank":2,"masterTypeScale":"10","slaveTypeScale":"200","worktimeMinute":30},{"detailRank":3,"masterTypeScale":"20","slaveTypeScale":"100","worktimeMinute":30},{"detailRank":4,"masterTypeScale":"20","slaveTypeScale":"200","worktimeMinute":45}]}' http://%s/labor/standard/push
        """ % (m, ip)
    print('/labor/standard/push 插入 14 ',m414)


    # 劳动力标准 更新
    # m4 = """
    # curl -H "Content-Type:application/json" -X POST --data '{%s,"cid":"123456","bid":"201903292247340840341012959f0009","operate_type":"update","mode":"single","masterType":"order_num","slaveType":"turnover","detailArr":[{"detailRank":1,"masterTypeScale":"20","slaveTypeScale":"100","worktimeMinute":35},{"detailRank":2,"masterTypeScale":"20","slaveTypeScale":"200","worktimeMinute":35},{"detailRank":3,"masterTypeScale":"20","slaveTypeScale":"100","worktimeMinute":30},{"detailRank":4,"masterTypeScale":"20","slaveTypeScale":"200","worktimeMinute":45}]}' http://%s/labor/standard/push
    # """ % (m, ip)
    m4 = """
        curl -H "Content-Type:application/json" -X POST --data '{%s,"operate_type":"delete","deleteBids":["20191129161023265023140104560002"]}' http://%s/labor/standard/push
        """ % (m, ip)

    print('/labor/standard/push',m4)


    # 2 -3 计算 task
    # print(
    # '/labor/worktime/forecast',"""
    #     curl -H "Content-Type:application/json" -X POST --data '{%s,"cid":"123456","forecastType":"task","forecast_date_start":"2019-07-01","forecast_date_end":"2019-07-02","didArr":[6,14],"nodeStandardBid":"201903292247340840341012959f0009","nodeBid":"201903292247340840341012959f0001","forecastStandard":"peoples","nodeTimeArr":[{"startTimeStr":"09:00","endTimeStr":"09:15"},{"startTimeStr":"09:15","endTimeStr":"09:30"},{"startTimeStr":"09:30","endTimeStr":"09:45"}],"taskArr":[{"taskBid":"201903292247340840341012959f0001","laborStandardBid":"201903292247340840341012959f0009","forecastStandard":"order_num","taskTimeArr":[{"startTimeStr":"09:00","endTimeStr":"09:15"},{"startTimeStr":"09:15","endTimeStr":"09:30"},{"startTimeStr":"09:30","endTimeStr":"09:45"}]},{"taskBid":"201903292247340840341012959f0002","laborStandardBid":"201903292247340840341012959f0010","forecastStandard":"order_num","taskTimeArr":[{"startTimeStr":"11:00","endTimeStr":"11:15"},{"startTimeStr":"11:15","endTimeStr":"11:30"},{"startTimeStr":"11:30","endTimeStr":"11:45"}]}]}' http://%s/labor/worktime/forecast
    # """ % (m, ip))

    print(
        '/labor/worktime/forecast', """
            curl -H "Content-Type:application/json" -X POST --data '{%s,"cid": "123456","forecastType": "0", "forecast_date_start": "2019-07-12", "forecast_date_end": "2019-07-18", "didArr": [6],"taskArr": [{"taskBid": "201903292247340840341012959f0001", "laborStandardBid": "201903292247340840341012959f0009","forecastStandard": "turnover", "taskTimeArr": [{"startTimeStr": "09:00", "endTimeStr": "09:15"},{"startTimeStr": "09:15", "endTimeStr": "09:30"},{"startTimeStr": "09:30", "endTimeStr": "09:45"}]}]}
            ' http://%s/labor/worktime/forecast
        """ % (m, ip))



    #2接口4 node
    labor_node="""
    curl -H "Content-Type:application/json" -X POST --data '{%s,"cid":"123456","nodeBid":"201903292247340840341012959f0001","nodeStandardBid":"201903292247340840341012959f0009","forecastModifyArr":[{"forecastDate":"2019-07-01","startTimeStr":"09:00","endTimeStr":"09:15","forecastValue":"30","editValue":"60"},{"forecastDate":"2019-07-01","startTimeStr":"09:15","endTimeStr":"09:30","forecastValue":"30","editValue":"0"}]}' http://%s/labor/worktime/forecastModify
    """ % (m, ip)
    print('/labor/worktime/forecastModify - node',labor_node)

    # 2接口4 task
    labor_task = """
    curl -H "Content-Type:application/json" -X POST --data '{%s,"nodeBid":"","cid":"123456","nodeBid":"","forecastModifyArr":[{"forecastStandard":"turnover","taskBid":"201903292247340840341012959f0001","forecastDate":"2019-07-02","startTimeStr":"11:15","endTimeStr":"11:30","forecastValue":"30","editValue":"60","laborStandardBid":"201903292247340840341012959f0009","did":"6"},{"forecastStandard":"turnover","taskBid":"201903292247340840341012959f0002","forecastDate":"2019-07-02","startTimeStr":"11:00","endTimeStr":"11:15","forecastValue":"30","editValue":"0","laborStandardBid":"201903292247340840341012959f0010","did":"14"}]}' http://%s/labor/worktime/forecastModify
    """ % (m, ip)
    print('/labor/worktime/forecastModify - task', labor_task)

    # 3接口3 拆分规则-修改接口
    a = """curl -H "Content-Type:application/json" -X POST --data '{%s,"cid":"123456","bid":"jsj90329124156363056100123cf025l","didArr":[6],"opt":"update","shiftsplitData":[{"ruleCalType":"interval","ruleCpType":"lt","ruleCpNum":"120","dayFusion":true},{"ruleCalType":"shiftNum","ruleCpType":"lt","ruleCpNum":"4","dayFusion":true},{"ruleCalType":"shiftLen","ruleCpType":"lt","ruleCpNum":"240","dayFusion":true},{"ruleCalType":"worktime","ruleCpType":"lt","ruleCpNum":"480","dayFusion":true}]}' http://%s/labor/shiftsplitrule/modify
    """ % (m, ip)
    print('/labor/shiftsplitrule/modify',a)

    # 3接口4 任务详情
    # labor_task_modify = """
    # curl -H "Content-Type:application/json" -X POST --data '{%s,"cid":"123456","taskDetail":[{"taskName":"服务员","bid":"201903291236271250271007959f0211","abCode":"XS","didArr":[6],"taskType":"directwh","opt":"update","worktimeData":[{"worktimeType":"bisTime","worktimeStart":"08:00","worktimeEnd":"22:00"}],"taskSkill":[{"taskSkillBid":"201903291248510440511007959f0216","skillNum":"80"}],"certs":["健康证"]},{"taskName":"莎拉","bid":"201903291241432550431007959f0213","abCode":"SL","didArr":[6],"taskType":"indirectwh","opt":"update","worktimeData":[{"worktimeType":"customTime","worktimeStart":"09:00","worktimeEnd":"23:00"}],"taskSkill":[{"taskSkillBid":"201903291241563630561007959f0214","skillNum":"50"},{"taskSkillBid":"201903291244342970341007959f0215","skillNum":"100"}],"certs":["健康证"]},{"taskName":"中餐","bid":"201903291241563630561007959f0214","abCode":"ZC","didArr":[6],"taskType":"fixedwh","opt":"update","worktimeData":[{"worktimeType":"fixedTime","worktimeStart":"10:30","worktimeEnd":"13:00"}],"taskSkill":[{"taskSkillBid":"201903291250295220291007959f0217","skillNum":"80"}],"certs":["健康证"]},{"taskName":"西餐","bid":"201903291244342970341007959f0215","abCode":"XC","didArr":[6],"taskType":"fixedwh","opt":"update","worktimeData":[{"worktimeType":"fixedTime","worktimeStart":"14:00","worktimeEnd":"22:00"}],"taskSkill":[{"taskSkillBid":"201903291241432550431007959f0213","skillNum":"80"}],"certs":["健康证"]},{"taskName":"洗碗","bid":"201903291248510440511007959f0216","abCode":"XW","didArr":[6],"taskType":"directwh","opt":"update","worktimeData":[{"worktimeType":"bisTime","worktimeStart":"08:00","worktimeEnd":"22:00"}],"taskSkill":[{"taskSkillBid":"201903291241363910361007959f0212","skillNum":"80"}],"certs":["健康证"]},{"taskName":"面点","bid":"201903291250295220291007959f0217","abCode":"XW","didArr":[6],"taskType":"fixedwh","opt":"update","worktimeData":[{"worktimeType":"fixedTime","worktimeStart":"08:00","worktimeEnd":"10:00"}],"taskSkill":[{"taskSkillBid":"201903291250295220291007959f0217","skillNum":"80"}],"certs":["健康证"]},{"taskName":"传菜","bid":"201903291241363910361007959f0212","abCode":"CC","didArr":[6],"taskType":"directwh","opt":"update","worktimeData":[{"worktimeType":"bisTime","worktimeStart":"08:00","worktimeEnd":"22:00"}],"taskSkill":[{"taskSkillBid":"201903291236271250271007959f0211","skillNum":"80"}],"certs":["健康证"]},{"taskName":"收银","bid":"201903291236116910111007959f0210","abCode":"SY","didArr":[6],"taskType":"directwh","opt":"update","worktimeData":[{"worktimeType":"bisTime","worktimeStart":"08:00","worktimeEnd":"22:00"}],"taskSkill":[{"taskSkillBid":"201903291236116910111007959f0210","skillNum":"80"}],"certs":["健康证"]},{"taskName":"吧台","bid":"201903291236061290061007959f0209","abCode":"SY","didArr":[6],"taskType":"directwh","opt":"update","worktimeData":[{"worktimeType":"bisTime","worktimeStart":"08:00","worktimeEnd":"22:00"}],"taskSkill":[{"taskSkillBid":"201903291236061290061007959f0209","skillNum":"80"}],"certs":["健康证"]}]}' http://%s/labor/task/modify
    # """ % (m, ip)

    labor_task_modify = """
        curl -H "Content-Type:application/json" -X POST --data '{%s,"cid":"123456","taskDetail":[{"taskName":"服务员","bid":"201903291236271250271007959f0211","opt":"delete"}]}' http://%s/labor/task/modify
        """ % (m, ip)
    print('/labor/task/modify', labor_task_modify)

    #3 接口1 班次模型
    shiftMod = """
    curl -H "Content-Type:application/json" -X POST --data '{%s,"cid":"123456","bid":"jsj903291241563630561001235D025d","opt":"update","didArr":[6],"shiftModData":[{"shiftBid":"jsj903291241563630561001235c0213","opt":"update","shiftStart":"09:00","shiftEnd":"12:00","isCrossDay":false},{"shiftBid":"jsj903291241563630561001234c0214","shiftStart":"10:00","opt":"update","shiftEnd":"13:00","isCrossDay":false},{"shiftBid":"jsj903291241563630561001234c0215","shiftStart":"09:30","opt":"update","shiftEnd":"14:00","isCrossDay":false},{"shiftBid":"jsj903291241563630561001234c0216","shiftStart":"13:30","opt":"update","shiftEnd":"19:00","isCrossDay":false},{"shiftBid":"jsj903291241563630561001234c0217","shiftStart":"16:30","opt":"update","shiftEnd":"22:00","isCrossDay":false},{"shiftBid":"jsj903291241563630561001234c0218","shiftStart":"17:00","opt":"update","shiftEnd":"23:00","isCrossDay":false},{"shiftBid":"jsj903291241563630561001234c0219","shiftStart":"17:30","opt":"update","shiftEnd":"23:30","isCrossDay":false}]}' http://%s/labor/shiftmod/modify
    """ % (m, ip)
    print('/labor/shiftmod/modify', shiftMod)

    #3 接口2 组合规则
    labor_combi = """
    curl -H "Content-Type:application/json" -X POST --data '{%s,"cid":"123456","bid":"jsj903291241563630561001235g025d","didArr":[6],"opt":"update","combiRuleData":[{"ruleData":"201903291236061290061007959f0209,201903291236116910111007959f0210"},{"ruleData":"201903291248510440511007959f0216,201903291236271250271007959f0211"},{"ruleData":"201903291241363910361007959f0212,201903291236271250271007959f0211"},{"ruleData":"201903291250295220291007959f0217,201903291241432550431007959f0213,201903291244342970341007959f0215"},{"ruleData":"201903291244342970341007959f0215,201903291241563630561007959f0214"}]}' http://%s/labor/combirule/modify
    """ % (m, ip)
    print('/labor/combirule/modify', labor_combi)

    #3 接口6 劳动人口预测修改接口
    labor_manpower_modify = """
    curl -H "Content-Type:application/json" -X POST --data '{%s,"cid":"123456","bid":"201903291241563630561001235f0258","combiRuleData":[{"2019-07-12":[{"combiRule":"20190605101543145043101404020054,20190605101543145043101404020053","combiRuleNewVal":"3-5","combiRuleOldVal":"3-4"},{"combiRule":"20190605101543145043101404020054,20190605101543145043101404020053","combiRuleNewVal":"5-6","combiRuleOldVal":"3-8"}]},{"2019-07-13":[{"combiRule":"20190605101543145043101404020055,20190605101543145043101404020056","combiRuleNewVal":"4-8","combiRuleOldVal":"1-9"},{"combiRule":"20190605101543145043101404020055,20190605101543145043101404020056,57","combiRuleNewVal":"4-8","combiRuleOldVal":"1-9"},{"combiRule":"20190605101543145043101404020055,20190605101543145043101404020056,58","combiRuleNewVal":"4-8","combiRuleOldVal":"1-9"}]}]}' http://%s/labor/manpower/modify
    """ % (m, ip)
    print('/labor/manpower/modify' ,labor_manpower_modify)

    # 3 接口5 劳动人口预测
    labor_manpower_forecast = """
        curl -H "Content-Type:application/json" -X POST --data '{%s,"cid":"123456","forecastType":"1","timeInterval":"30","didArr":[6],"forecastDateStart":"2019-07-12","forecastDateEnd":"2019-07-13","shiftMod":[{"shiftModbid":"201903291241563630561001235D025d","didArr":[6],"shiftModData":[{"shiftBid":"201903291241563630561001235f0215","shiftStart":"14:00","shiftEnd":"19:00","isCrossDay":false},{"shiftBid":"201903291241563630561001234f0214","shiftStart":"20:00","shiftEnd":"03:00","isCrossDay":true}]}],"combirule":[{"combiruleBid":"201903291241563630561001235g025d","didArr":[6],"combiRuleData":[{"ruleData":"201903291241563630561001235g0815,201903291241563630561001275g0815"},{"ruleData":"201903291236061290061007959f0209,201903291236116910111007959f0210"},{"ruleData":"201903291236116910111007959f0210,201903291241363910361007959f0212"},{"ruleData":"201903291236271250271007959f0211,201903291241363910361007959f0212"},{"ruleData":"201903291241563630561007959f0214,201903291248510440511007959f0216"},{"ruleData":"201903291241563630561007959f0214,201903291250295220291007959f0217"},{"ruleData":"201903291248510440511007959f0216,201903291250295220291007959f0217"}]}],"shiftsplitrule":[{"shiftsplitbid":"20190329124156363056100123kg025l","didArr":[6],"shiftsplitData":[{"ruleCalType":"interval","ruleCpType":"lt","ruleCpNum":"60","dayFusion":true},{"ruleCalType":"shiftNum","ruleCpType":"lt","ruleCpNum":"4","dayFusion":true},{"ruleCalType":"shiftLen","ruleCpType":"lt","ruleCpNum":"240","dayFusion":true},{"ruleCalType":"worktime","ruleCpType":"lt","ruleCpNum":"600","dayFusion":true}]}]}' http://%s/labor/manpower/forecast
        """ % (m, ip)

    # labor_manpower_forecast = """
    #         curl -H "Content-Type:application/json" -X POST --data '{%s,"forecastDateEnd":"2019-07-14","forecastType":"0","forecastDateStart":"2019-07-12","shiftMod":[],"shiftsplitrule":[{"shiftsplitbid":"20191130151053475053141304e00001","shiftsplitData":[{"ruleCalType":"interval","ruleCpType":"lt","dayFusion":true,"ruleCpNum":2}],"didArr":[4954]},{"shiftsplitbid":"20191130160940875040141301e70001","shiftsplitData":[{"ruleCalType":"interval","ruleCpType":"lt","dayFusion":true,"ruleCpNum":2}],"didArr":[4954]}],"didArr":[4954],"timeInterval":"30","combirule":[],"cid":"123456"}' http://%s/labor/manpower/forecast
    #         """ % (m, ip)

    # labor_manpower_forecast = """
    #         curl -H "Content-Type:application/json" -X POST --data '{%s,"forecastDateEnd":"2019-12-19","forecastType":"0","forecastDateStart":"2019-12-18","shiftMod":[],"shiftsplitrule":[{"shiftsplitbid":"20191130151053475053141304e00001","shiftsplitData":[{"ruleCalType":"interval","ruleCpType":"lt","dayFusion":"true","ruleCpNum":"120"}],"didArr":[4954]},{"shiftsplitbid":"20191130160940875040141301e70001","shiftsplitData":[{"ruleCalType":"interval","ruleCpType":"lt","dayFusion":"true","ruleCpNum":"120"}],"didArr":[4954]}],"didArr":[4954],"timeInterval":"30","combirule":[],"cid":50000031}' http://%s/labor/manpower/forecast
    #         """ % (m, ip)
    print('/labor/manpower/forecast', labor_manpower_forecast)


    # 4 接口1 员工可用性-修改接口
    available_time_modify  = """
        curl -H "Content-Type:application/json" -X POST --data '{%s,"cid":"123456","availabletime":[{"eid":"10","opt":"update","type":"0","day":"2019-07-12","times":[]},{"eid":"10","opt":"update","type":"2","day":"2019-07-13","times":[{"start":"06:00","end":"12:00"}]},{"eid":"10","opt":"update","type":"1","day":"2019-07-14","times":[]},{"eid":"10","opt":"update","type":"0","day":"2019-07-15","times":[]},{"eid":"10","opt":"update","type":"2","day":"2019-07-16","times":[{"start":"12:00","end":"23:00"}]},{"eid":"10","opt":"update","type":"0","day":"2019-07-17","times":[]},{"eid":"10","opt":"update","type":"1","day":"2019-07-18","times":[]},{"eid":"88","opt":"update","type":"0","day":"2019-07-12","times":[]},{"eid":"88","opt":"update","type":"0","day":"2019-07-13","times":[]},{"eid":"88","opt":"update","type":"0","day":"2019-07-14","times":[]},{"eid":"88","opt":"update","type":"1","day":"2019-07-15","times":[]},{"eid":"88","opt":"update","type":"0","day":"2019-07-16","times":[]},{"eid":"88","opt":"update","type":"1","day":"2019-07-17","times":[]},{"eid":"88","opt":"update","type":"0","day":"2019-07-18","times":[]},{"eid":"141","opt":"update","type":"1","day":"2019-07-12","times":[]},{"eid":"141","opt":"update","type":"0","day":"2019-07-13","times":[]},{"eid":"141","opt":"update","type":"0","day":"2019-07-14","times":[]},{"eid":"141","opt":"update","type":"0","day":"2019-07-15","times":[]},{"eid":"141","opt":"update","type":"2","day":"2019-07-16","times":[{"start":"12:00","end":"23:00"}]},{"eid":"141","opt":"update","type":"0","day":"2019-07-17","times":[]},{"eid":"141","opt":"update","type":"1","day":"2019-07-18","times":[]},{"eid":"256","opt":"update","type":"0","day":"2019-07-12","times":[]},{"eid":"256","opt":"update","type":"1","day":"2019-07-13","times":[]},{"eid":"256","opt":"update","type":"2","day":"2019-07-14","times":[{"start":"06:00","end":"12:00"}]},{"eid":"256","opt":"update","type":"0","day":"2019-07-15","times":[]},{"eid":"256","opt":"update","type":"0","day":"2019-07-16","times":[]},{"eid":"256","opt":"update","type":"1","day":"2019-07-17","times":[]},{"eid":"256","opt":"update","type":"0","day":"2019-07-18","times":[]},{"eid":"369","opt":"update","type":"2","day":"2019-07-12","times":[{"start":"12:00","end":"23:00"}]},{"eid":"369","opt":"update","type":"0","day":"2019-07-13","times":[]},{"eid":"369","opt":"update","type":"0","day":"2019-07-14","times":[]},{"eid":"369","opt":"update","type":"2","day":"2019-07-15","times":[{"start":"06:00","end":"12:00"},{"start":"16:00","end":"23:00"}]},{"eid":"369","opt":"update","type":"1","day":"2019-07-16","times":[]},{"eid":"369","opt":"update","type":"0","day":"2019-07-17","times":[]},{"eid":"369","opt":"update","type":"1","day":"2019-07-18","times":[]},{"eid":"633","opt":"update","type":"0","day":"2019-07-12","times":[]},{"eid":"633","opt":"update","type":"0","day":"2019-07-13","times":[]},{"eid":"633","opt":"update","type":"1","day":"2019-07-14","times":[]},{"eid":"633","opt":"update","type":"0","day":"2019-07-15","times":[]},{"eid":"633","opt":"update","type":"0","day":"2019-07-16","times":[]},{"eid":"633","opt":"update","type":"1","day":"2019-07-17","times":[]},{"eid":"633","opt":"update","type":"0","day":"2019-07-18","times":[]},{"eid":"677","opt":"update","type":"0","day":"2019-07-12","times":[]},{"eid":"677","opt":"update","type":"2","day":"2019-07-13","times":[{"start":"12:00","end":"23:00"}]},{"eid":"677","opt":"update","type":"0","day":"2019-07-14","times":[]},{"eid":"677","opt":"update","type":"1","day":"2019-07-15","times":[]},{"eid":"677","opt":"update","type":"0","day":"2019-07-16","times":[]},{"eid":"677","opt":"update","type":"0","day":"2019-07-17","times":[]},{"eid":"677","opt":"update","type":"1","day":"2019-07-18","times":[]},{"eid":"680","opt":"update","type":"1","day":"2019-07-12","times":[]},{"eid":"680","opt":"update","type":"0","day":"2019-07-13","times":[]},{"eid":"680","opt":"update","type":"0","day":"2019-07-14","times":[]},{"eid":"680","opt":"update","type":"0","day":"2019-07-15","times":[]},{"eid":"680","opt":"update","type":"2","day":"2019-07-16","times":[{"start":"12:00","end":"23:00"}]},{"eid":"680","opt":"update","type":"1","day":"2019-07-17","times":[]},{"eid":"680","opt":"update","type":"0","day":"2019-07-18","times":[]},{"eid":"730","opt":"update","type":"0","day":"2019-07-12","times":[]},{"eid":"730","opt":"update","type":"1","day":"2019-07-13","times":[]},{"eid":"730","opt":"update","type":"2","day":"2019-07-14","times":[{"start":"06:00","end":"12:00"}]},{"eid":"730","opt":"update","type":"0","day":"2019-07-15","times":[]},{"eid":"730","opt":"update","type":"0","day":"2019-07-16","times":[]},{"eid":"730","opt":"update","type":"0","day":"2019-07-17","times":[]},{"eid":"730","opt":"update","type":"1","day":"2019-07-18","times":[]},{"eid":"732","opt":"update","type":"0","day":"2019-07-12","times":[]},{"eid":"732","opt":"update","type":"0","day":"2019-07-13","times":[]},{"eid":"732","opt":"update","type":"0","day":"2019-07-14","times":[]},{"eid":"732","opt":"update","type":"0","day":"2019-07-15","times":[]},{"eid":"732","opt":"update","type":"1","day":"2019-07-16","times":[]},{"eid":"732","opt":"update","type":"1","day":"2019-07-17","times":[]},{"eid":"732","opt":"update","type":"0","day":"2019-07-18","times":[]},{"eid":"791","opt":"update","type":"0","day":"2019-07-12","times":[]},{"eid":"791","opt":"update","type":"0","day":"2019-07-13","times":[]},{"eid":"791","opt":"update","type":"1","day":"2019-07-14","times":[]},{"eid":"791","opt":"update","type":"0","day":"2019-07-15","times":[]},{"eid":"791","opt":"update","type":"0","day":"2019-07-16","times":[]},{"eid":"791","opt":"update","type":"0","day":"2019-07-17","times":[]},{"eid":"791","opt":"update","type":"1","day":"2019-07-18","times":[]}]}' http://%s/sch/availabletime/modify
        """ % (m, ip)
    print('/sch/availabletime/modify', available_time_modify)

    # 4 接口2 员工技能修改
    emp_skill_modify = """
            curl -H "Content-Type:application/json" -X POST --data '{%s,"cid":"123456","skillData":[{"eid":"10","opt":"update","skills":[{"skill":"201903291330290710291007959f0422","skillNum":"100"},{"skill":"201903291330290710291007959f0404","skillNum":"100"}]},{"eid":"88","opt":"update","skills":[{"skill":"201903291321017190011007959f0258","skillNum":"100"}]},{"eid":"141","opt":"update","skills":[{"skill":"201903291248510440511007959f0216","skillNum":"100"},{"skill":"201903290121262530261007959f0010","skillNum":"80"}]},{"eid":"244","opt":"update","skills":[{"skill":"201906121730471320471007959f0014","skillNum":"100"},{"skill":"201903291236271250271007959f0211","skillNum":"100"},{"skill":"201903291236116910111007959f0210","skillNum":"100"}]},{"eid":"256","opt":"update","skills":[{"skill":"201903291241563630561007959f0214","skillNum":"100"},{"skill":"201903291236271250271007959f0211","skillNum":"80"},{"skill":"201903291244342970341007959f0215","skillNum":"70"}]},{"eid":"369","opt":"update","skills":[{"skill":"201903291321017190011007959f0258","skillNum":"100"},{"skill":"201903291244342970341007959f0215","skillNum":"80"}]},{"eid":"472","opt":"update","skills":[{"skill":"201903291236271250271007959f0231","skillNum":"100"},{"skill":"201903291236116910111007959f0210","skillNum":"80"}]},{"eid":"633","opt":"update","skills":[{"skill":"201903291236271250271007959f0211","skillNum":"100"},{"skill":"201903290121262530261007959f0010","skillNum":"90"}]},{"eid":"677","opt":"update","skills":[{"skill":"201903291236271250271007959f0211","skillNum":"60"},{"skill":"201903290121262530261007959f0010","skillNum":"80"}]},{"eid":"680","opt":"update","skills":[{"skill":"201903291241563630561007959f0214","skillNum":"80"},{"skill":"201903291244342970341007959f0215","skillNum":"100"}]},{"eid":"730","opt":"update","skills":[{"skill":"201903291236271250271007959f0211","skillNum":"50"},{"skill":"201903290121262530261007959f0010","skillNum":"50"}]},{"eid":"732","opt":"update","skills":[{"skill":"201903291236271250271007959f0211","skillNum":"60"},{"skill":"201903290121262530261007959f0010","skillNum":"80"}]},{"eid":"791","opt":"update","skills":[{"skill":"201903290121262530261007959f0010","skillNum":"100"},{"skill":"201903291236271250271007959f0211","skillNum":"90"}]}]}' http://%s/sch/empskill/modify
            """ % (m, ip)
    print('/sch/empskill/modify', emp_skill_modify)

    # 4 接口3 员工证书-修改接口
    employee_certificate_modify = """
        curl -H "Content-Type:application/json" -X POST --data '{%s,"cid":"123456","skillData":[{"eid":"10","opt":"update","certs":[{"certname":"健康证","closingdate":"2019-08-10"}]},{"eid":"88","opt":"update","certs":[{"certname":"健康证","closingdate":"2019-07-14"}]},{"eid":"141","opt":"update","certs":[{"certname":"健康证","closingdate":"2019-07-17"}]},{"eid":"244","opt":"update","certs":[{"certname":"健康证","closingdate":"2019-07-12"}]},{"eid":"256","opt":"update","certs":[{"certname":"健康证","closingdate":"2019-08-10"}]},{"eid":"369","opt":"update","certs":[{"certname":"健康证","closingdate":"2019-07-18"}]},{"eid":"472","opt":"update","certs":[{"certname":"健康证","closingdate":"2019-08-10"}]},{"eid":"633","opt":"update","certs":[{"certname":"健康证","closingdate":"2019-08-10"}]},{"eid":"677","opt":"update","certs":[{"certname":"健康证","closingdate":"2019-08-10"}]},{"eid":"680","opt":"update","certs":[{"certname":"健康证","closingdate":"2019-07-16"}]},{"eid":"730","opt":"update","certs":[{"certname":"健康证","closingdate":"2019-08-10"}]},{"eid":"732","opt":"update","certs":[{"certname":"健康证","closingdate":"2019-08-10"}]},{"eid":"791","opt":"update","certs":[{"certname":"健康证","closingdate":"2019-08-10"}]}]}' http://%s/sch/empcert/modify
                """ % (m, ip)
    print('/sch/empcert/modify', employee_certificate_modify)

    # 4 接口4 排班合规性-修改接口
    # compliance_modify = """
    #     curl -H "Content-Type:application/json" -X POST --data '{%s,"cid":"123456","opt":"update","ruleData":[{"ptype":"organizerule","didArr":[6],"eids":[],"ptypeData":[{"ruleType":"skilldemand","ruleCpType":"ge","ruleCpNum":"8","dayFusion":true,"ruletag":"201903291330290710291007959f0404","cycle":"week","shiftId":"","cret":"","timeRange":"1","startDate":"2019-07-01","caution":"warning"},{"ruleType":"skilldemand","ruleCpType":"ge","ruleCpNum":"8","dayFusion":true,"ruletag":"201903291236271250271007959f0231","cycle":"week","shiftId":"","cret":"","timeRange":"1","startDate":"2019-07-01","caution":"warning"},{"ruleType":"skilldemand","ruleCpType":"ge","ruleCpNum":"8","dayFusion":true,"ruletag":"201903291236271250271007959f0211","cycle":"week","shiftId":"","cret":"","timeRange":"1","startDate":"2019-07-01","caution":"warning"},{"ruleType":"skilldemand","ruleCpType":"ge","ruleCpNum":"8","dayFusion":true,"ruletag":"201903291236116910111007959f0210","cycle":"week","shiftId":"","cret":"","timeRange":"1","startDate":"2019-07-01","caution":"warning"},{"ruleType":"cretdemand","ruleCpType":"lt","ruleCpNum":"10","dayFusion":true,"ruletag":"健康证","cycle":"week","shiftId":"","cret":"","timeRange":"1","startDate":"2019-07-01","caution":"warning"},{"ruleType":"shiftdemand","ruleCpType":"ge","ruleCpNum":"10","dayFusion":true,"ruletag":"1","cycle":"week","shiftId":"","cret":"","timeRange":"1","startDate":"2019-07-01","caution":"warning"}]},{"ptype":"emprule","didArr":[],"eids":[10,88,141,244,256,369,472,633,677,680,730,732,791],"ptypeData":[{"ruleType":"timerule","ruleCpType":"gt","ruleCpNum":"480","ruletag":"shiftTime","dayFusion":true,"cycle":"day","shiftId":"","cret":"","timeRange":"1","startDate":"2018-10-02","caution":"hint"},{"ruleType":"timerule","ruleCpType":"gt","ruleCpNum":"600","ruletag":"shiftTime","dayFusion":true,"cycle":"day","shiftId":"","cret":"","timeRange":"1","startDate":"2018-10-02","caution":"warning"},{"ruleType":"timerule","ruleCpType":"gt","ruleCpNum":"720","ruletag":"shiftTime","dayFusion":true,"cycle":"day","shiftId":"","cret":"","timeRange":"1","startDate":"2018-10-02","caution":"warning"},{"ruleType":"timerule","ruleCpType":"gt","ruleCpNum":"2400","ruletag":"shiftTime","dayFusion":true,"cycle":"week","shiftId":"","cret":"","timeRange":"1","startDate":"2018-10-02","caution":"hint"},{"ruleType":"timerule","ruleCpType":"gt","ruleCpNum":"3000","ruletag":"shiftTime","dayFusion":true,"cycle":"week","shiftId":"","cret":"","timeRange":"1","startDate":"2018-10-02","caution":"warning"},{"ruleType":"timerule","ruleCpType":"gt","ruleCpNum":"3600","ruletag":"shiftTime","dayFusion":true,"cycle":"week","shiftId":"","cret":"","timeRange":"1","startDate":"2018-10-02","caution":"forbid"},{"ruleType":"timerule","ruleCpType":"gt","ruleCpNum":"9600","ruletag":"shiftTime","dayFusion":true,"cycle":"month","shiftId":"","cret":"","timeRange":"1","startDate":"2018-10-02","caution":"hint"},{"ruleType":"timerule","ruleCpType":"gt","ruleCpNum":"12000","ruletag":"shiftTime","dayFusion":true,"cycle":"month","shiftId":"","cret":"","timeRange":"1","startDate":"2018-10-02","caution":"warning"},{"ruleType":"timerule","ruleCpType":"gt","ruleCpNum":"14400","ruletag":"shiftTime","dayFusion":true,"cycle":"month","shiftId":"","cret":"","timeRange":"1","startDate":"2018-10-02","caution":"forbid"},{"ruleType":"shiftrule","ruleCpType":"ge","ruleCpNum":"480","ruletag":"shiftLen","dayFusion":true,"cycle":"day","shiftId":"","cret":"","timeRange":"1","startDate":"2018-10-02","caution":"warning"},{"ruleType":"shiftrule","ruleCpType":"le","ruleCpNum":"60","ruletag":"interval","dayFusion":true,"cycle":"day","shiftId":"","cret":"","timeRange":"1","startDate":"2018-10-02","caution":"forbid"},{"ruleType":"shiftrule","ruleCpType":"ge","ruleCpNum":"10","ruletag":"schShiftNum","dayFusion":true,"cycle":"week","shiftId":"","cret":"","timeRange":"1","startDate":"2018-10-02","caution":"hint"},{"ruleType":"shiftrule","ruleCpType":"ge","ruleCpNum":"10","ruletag":"apShiftNum","dayFusion":true,"cycle":"week","shiftId":"1","cret":"","timeRange":"1","startDate":"2018-10-02","caution":"forbid"},{"ruleType":"daysrule","ruleCpType":"ge","ruleCpNum":"3","ruletag":"schDayNumCon","dayFusion":true,"cycle":"week","shiftId":"","cret":"","timeRange":"1","startDate":"2018-10-02","caution":"warning"},{"ruleType":"daysrule","ruleCpType":"ge","ruleCpNum":"3","ruletag":"restNumCon","dayFusion":true,"cycle":"week","shiftId":"","cret":"","timeRange":"1","startDate":"2018-10-02","caution":"warning"},{"ruleType":"daysrule","ruleCpType":"ge","ruleCpNum":"2","ruletag":"noSchNum","dayFusion":true,"cycle":"week","shiftId":"","cret":"","timeRange":"1","startDate":"2018-10-02","caution":"warning"},{"ruleType":"daysrule","ruleCpType":"ge","ruleCpNum":"4","ruletag":"schNumSame","dayFusion":true,"cycle":"week","shiftId":"","cret":"","timeRange":"1","startDate":"2018-10-02","caution":"forbid"},{"ruleType":"daysrule","ruleCpType":"ge","ruleCpNum":"3","ruletag":"restNum","dayFusion":true,"cycle":"week","shiftId":"","cret":"","timeRange":"1","startDate":"2018-10-02","caution":"forbid"},{"ruleType":"cretrule","ruleCpType":"eq","ruleCpNum":"0","ruletag":"schCert","dayFusion":true,"cycle":"","shiftId":"","cret":"健康证","timeRange":"","startDate":"2018-10-02","caution":"forbid"},{"ruleType":"cretrule","ruleCpType":"ge","ruleCpNum":"30","ruletag":"certExpireDays","dayFusion":true,"cycle":"","shiftId":"","cret":"健康证","timeRange":"","startDate":"2018-10-02","caution":"hint"}]}]}' http://%s/sch/compliance/modify
    #             """ % (m, ip)

    # compliance_modify = """
    #         curl -H "Content-Type:application/json" -X POST --data '{%s,"timestr":"2019-11-28 18:17:11.358","token":"a2fec73f4e3e426916a8b3aed839070d","opt":"update","ruleData":[{"didArr":null,"ptype":"emprule","eids":[81,86],"ptypeData":[{"ruletag":"schCert","shiftId":null,"ruleCpType":"eq","ruleType":"cretrule","dayFusion":false,"cert":"最傻二哈","ruleCpNum":1,"cycle":null,"caution":"warning","startDate":null,"timeRange":null}]}],"cid":"50000031"}' http://%s/sch/compliance/modify
    #                 """ % (m, ip)
    compliance_modify = """
                curl -H "Content-Type:application/json" -X POST --data '{%s,"opt":"update","ruleData":[{"didArr":[4954],"ptype":"emprule","eids":[81,86],"ptypeData":[{"ruletag":"noSchNum","ruleCpType":"gt","ruleType":"daysrule","dayFusion":false,"ruleCpNum":10,"cycle":"month","caution":"hint","startDate":"2019-11-04","timeRange":1}]}],"cid":"50000031"}' http://%s/sch/compliance/modify
                        """ % (m, ip)

    print('/sch/compliance/modify', compliance_modify)

    # 4 接口5 员工匹配属性修改
    # emp_matchpro_modify = """
    #             curl -H "Content-Type:application/json" -X POST --data '{%s,"cid":"123456","didArr":[6],"bid":"654321","opt":"delete","deleteBids":["654321"],"matchpros":[{"weight":"1","ruleGroup":"worktime","ruleDesc":"日排班工时（小时)","ruleCpType":"lt","ruletag":"dayWt","ruleCpNum":"240"},{"weight":"2","ruleGroup":"worktime","ruleDesc":"日排班工时（小时)","ruleCpType":"lt","ruletag":"dayWt","ruleCpNum":"480"},{"weight":"3","ruleGroup":"worktime","ruleDesc":"周排班工时（小时)","ruleCpType":"gt","ruletag":"weekWt","ruleCpNum":"1800"},{"weight":"4","ruleGroup":"worktime","ruleDesc":"周排班工时（小时)","ruleCpType":"eq","ruletag":"weekWt","ruleCpNum":"2400"},{"weight":"5","ruleGroup":"worktime","ruleDesc":"月排班工时（小时)","ruleCpType":"gt","ruletag":"monthWt","ruleCpNum":"9000"},{"weight":"6","ruleGroup":"worktime","ruleDesc":"月排班工时（小时)","ruleCpType":"lt","ruletag":"monthWt","ruleCpNum":"12000"},{"weight":"7","ruleGroup":"skillcert","ruleDesc":"任务技能熟练度（百分比)","ruleCpType":"gt","ruletag":"taskSkilled","ruleCpNum":"80"},{"weight":"8","ruleGroup":"skillcert","ruleDesc":"岗位技能熟练度（百分比）","ruleCpType":"gt","ruletag":"positionSkilled","ruleCpNum":"80"},{"weight":"9","ruleGroup":"skillcert","ruleDesc":"具备岗位要求证书（0：无,1：有）","ruleCpType":"eq","ruletag":"positioncert","ruleCpNum":"1"},{"weight":"10","ruleGroup":"shiftrule","ruleDesc":"班次之间间隔（小时）","ruleCpType":"ge","ruletag":"shiftInterval","ruleCpNum":"4"},{"weight":"11","ruleGroup":"shiftrule","ruleDesc":"每日班次个数","ruleCpType":"lt","ruletag":"shiftNum","ruleCpNum":"4"},{"weight":"12","ruleGroup":"otherrule","ruleDesc":"员工雇佣属性（0：兼职，1：全职）","ruleCpType":"eq","ruletag":"hireAttr","ruleCpNum":"1"},{"weight":"13","ruleGroup":"otherrule","ruleDesc":"员工是否愿意加班（0：否，1：是）","ruleCpType":"eq","ruletag":"agreeOverTime","ruleCpNum":"1"},{"weight":"14","ruleGroup":"otherrule","ruleDesc":"员工是否待新人（0：否，1：是）","ruleCpType":"eq","ruletag":"leadNewPeople","ruleCpNum":"1"}]}' http://%s/sch/matchpro/modify
    #             """ % (m, ip)
    emp_matchpro_modify = """
                    curl -H "Content-Type:application/json" -X POST --data '{%s,"cid":"50000031","bid":"654321","opt":"delete","deleteBids":["20191130140732581032154701da0004"]}' http://%s/sch/matchpro/modify
                    """ % (m, ip)

    print('/sch/matchpro/modify', emp_matchpro_modify)


    # 4 接口7 排班结果-修改推送接口
    # cal_modify = """
    #     curl -H "Content-Type:application/json" -X POST --data '{%s,"cid":"123456","applyId":"76542","editData":[{"eid":"23","schDay":"2019-07-12","allWorkTime":"480","workUnit":[{"type":"task","outId":"任务ID","startTime":"2019-07-12 09:00","endTime":"2019-07-12 12:00","workTime":"180"},{"type":"task","outId":"任务ID","startTime":"2019-07-12 13:00","endTime":"2019-07-12 18:00","workTime":"300"}]},{"eid":"23","schDay":"2019-07-13","allWorkTime":"480","workUnit":[{"type":"task","outId":"任务ID","startTime":"2019-07-13 09:00","endTime":"2019-07-13 12:00","workTime":"180"},{"type":"task","outId":"任务ID","startTime":"2019-07-13 13:00","endTime":"2019-07-13 18:00","workTime":"300"}]}]}' http://%s/sch/cal/modify
    #             """ % (m, ip)
    # print('/sch/cal/modify', cal_modify)
    cal_modify = """
                curl -H "Content-Type:application/json" -X POST --data '{%s,"cid":"50000031","editData":[{"schDay":"2019-12-03","eid":"16865","workUnit":[{"outId":"20191129140442595042128604480002","startTime":"2019-12-03 09:00","endTime":"2019-12-03 18:00","type":"task"}]}]}' http://%s/sch/cal/modify
                        """ % (m, ip)
    print('/sch/cal/modify', cal_modify)

    # 4 接口6 排班结果获取接口
    cal_result = """
            curl -H "Content-Type:application/json" -X POST --data '{%s,"cid":"123456","applyId":"54323456","didArr":[6],"recalculation":false,"start":"2019-07-12","end":"2019-07-18","timeInterval":"30","schType":"task","scheme":"effect","emps":[{"eid":"10","specialTime":[]},{"eid":"88","specialTime":[]},{"eid":"141","specialTime":[]},{"eid":"256","specialTime":[]},{"eid":"369","specialTime":[]},{"eid":"633","specialTime":[]},{"eid":"677","specialTime":[]},{"eid":"680","specialTime":[]},{"eid":"730","specialTime":[]},{"eid":"732","specialTime":[]},{"eid":"791","specialTime":[]},{"eid":"12","specialTime":[]},{"eid":"13","specialTime":[]},{"eid":"15","specialTime":[]},{"eid":"32","specialTime":[]},{"eid":"341","specialTime":[]},{"eid":"342","specialTime":[]},{"eid":"351","specialTime":[]},{"eid":"55","specialTime":[]},{"eid":"556","specialTime":[]},{"eid":"557","specialTime":[]},{"eid":"558","specialTime":[]},{"eid":"626","specialTime":[]},{"eid":"669","specialTime":[]},{"eid":"7","specialTime":[]},{"eid":"774419","specialTime":[]},{"eid":"774431","specialTime":[]},{"eid":"774433","specialTime":[]},{"eid":"774435","specialTime":[]},{"eid":"774436","specialTime":[]},{"eid":"774438","specialTime":[]},{"eid":"774440","specialTime":[]},{"eid":"774445","specialTime":[]},{"eid":"774448","specialTime":[]},{"eid":"774449","specialTime":[]},{"eid":"774451","specialTime":[]},{"eid":"774452","specialTime":[]},{"eid":"774454","specialTime":[]},{"eid":"774455","specialTime":[]},{"eid":"774456","specialTime":[]},{"eid":"774480","specialTime":[]},{"eid":"8","specialTime":[]},{"eid":"9","specialTime":[]}]}' http://%s/sch/cal""" % (m, ip)
    print('/sch/cal', cal_result)

a={
    "code": 100,
    "result": "预测成功",
    "data": {
        "2019-07-01": {
            "00:00-00:15": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "00:15-00:30": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "00:30-00:45": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "00:45-01:00": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "01:00-01:15": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "01:15-01:30": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "01:30-01:45": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "01:45-02:00": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "02:00-02:15": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "02:15-02:30": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "02:30-02:45": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "02:45-03:00": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "03:00-03:15": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "03:15-03:30": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "03:30-03:45": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "03:45-04:00": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "04:00-04:15": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "04:15-04:30": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "04:30-04:45": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "04:45-05:00": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "05:00-05:15": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "05:15-05:30": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "05:30-05:45": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "05:45-06:00": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "06:00-06:15": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "06:15-06:30": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "06:30-06:45": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "06:45-07:00": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "07:00-07:15": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "07:15-07:30": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "07:30-07:45": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "07:45-08:00": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "08:00-08:15": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "08:15-08:30": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "08:30-08:45": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "08:45-09:00": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "09:00-09:15": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "09:15-09:30": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "09:30-09:45": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "09:45-10:00": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "10:00-10:15": {
                "20191211103154407054140404c00010": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "10:15-10:30": {
                "20191211103154407054140404c00010": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "10:30-10:45": {
                "20191211103154407054140404c00010": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "10:45-11:00": {
                "20191211103154407054140404c00010": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "11:00-11:15": {
                "20191211103154407054140404c00010": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "11:15-11:30": {
                "20191211103154407054140404c00010": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "11:30-11:45": {
                "20191211103154407054140404c00010": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "11:45-12:00": {
                "20191211103154407054140404c00010": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "12:00-12:15": {
                "20191211103154407054140404c00010": {
                    "value": 120,
                    "scope": [
                        120,
                        120
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 120,
                    "scope": [
                        120,
                        120
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 120,
                    "scope": [
                        120,
                        120
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 120,
                    "scope": [
                        120,
                        120
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 120,
                    "scope": [
                        120,
                        120
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 120,
                    "scope": [
                        120,
                        120
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 120,
                    "scope": [
                        120,
                        120
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 120,
                    "scope": [
                        120,
                        120
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "12:15-12:30": {
                "20191211103154407054140404c00010": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "12:30-12:45": {
                "20191211103154407054140404c00010": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "12:45-13:00": {
                "20191211103154407054140404c00010": {
                    "value": 90,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 90,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 90,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 90,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 90,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 90,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 90,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 90,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "13:00-13:15": {
                "20191211103154407054140404c00010": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "13:15-13:30": {
                "20191211103154407054140404c00010": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "13:30-13:45": {
                "20191211103154407054140404c00010": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "13:45-14:00": {
                "20191211103154407054140404c00010": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "14:00-14:15": {
                "20191211103154407054140404c00010": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "14:15-14:30": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "14:30-14:45": {
                "20191211103154407054140404c00010": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "14:45-15:00": {
                "20191211103154407054140404c00010": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "15:00-15:15": {
                "20191211103154407054140404c00010": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "15:15-15:30": {
                "20191211103154407054140404c00010": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "15:30-15:45": {
                "20191211103154407054140404c00010": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "15:45-16:00": {
                "20191211103154407054140404c00010": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "16:00-16:15": {
                "20191211103154407054140404c00010": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "16:15-16:30": {
                "20191211103154407054140404c00010": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "16:30-16:45": {
                "20191211103154407054140404c00010": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "16:45-17:00": {
                "20191211103154407054140404c00010": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "17:00-17:15": {
                "20191211103154407054140404c00010": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "17:15-17:30": {
                "20191211103154407054140404c00010": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "17:30-17:45": {
                "20191211103154407054140404c00010": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "17:45-18:00": {
                "20191211103154407054140404c00010": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "18:00-18:15": {
                "20191211103154407054140404c00010": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "18:15-18:30": {
                "20191211103154407054140404c00010": {
                    "value": 150,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 150,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 150,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 150,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 150,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 150,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 150,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 150,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "18:30-18:45": {
                "20191211103154407054140404c00010": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "18:45-19:00": {
                "20191211103154407054140404c00010": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "19:00-19:15": {
                "20191211103154407054140404c00010": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "19:15-19:30": {
                "20191211103154407054140404c00010": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "19:30-19:45": {
                "20191211103154407054140404c00010": {
                    "value": 150,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 150,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 150,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 150,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 150,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 150,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 150,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 150,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "19:45-20:00": {
                "20191211103154407054140404c00010": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "20:00-20:15": {
                "20191211103154407054140404c00010": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "20:15-20:30": {
                "20191211103154407054140404c00010": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "20:30-20:45": {
                "20191211103154407054140404c00010": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "20:45-21:00": {
                "20191211103154407054140404c00010": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "21:00-21:15": {
                "20191211103154407054140404c00010": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "21:15-21:30": {
                "20191211103154407054140404c00010": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "21:30-21:45": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "21:45-22:00": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "22:00-22:15": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "22:15-22:30": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "22:30-22:45": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "22:45-23:00": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "23:00-23:15": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "23:15-23:30": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "23:30-23:45": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "23:45-00:00": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            }
        },
        "2019-07-02": {
            "00:00-00:15": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "00:15-00:30": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "00:30-00:45": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "00:45-01:00": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "01:00-01:15": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "01:15-01:30": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "01:30-01:45": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "01:45-02:00": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "02:00-02:15": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "02:15-02:30": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "02:30-02:45": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "02:45-03:00": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "03:00-03:15": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "03:15-03:30": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "03:30-03:45": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "03:45-04:00": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "04:00-04:15": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "04:15-04:30": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "04:30-04:45": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "04:45-05:00": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "05:00-05:15": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "05:15-05:30": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "05:30-05:45": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "05:45-06:00": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "06:00-06:15": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "06:15-06:30": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "06:30-06:45": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "06:45-07:00": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "07:00-07:15": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "07:15-07:30": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "07:30-07:45": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "07:45-08:00": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "08:00-08:15": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "08:15-08:30": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "08:30-08:45": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "08:45-09:00": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "09:00-09:15": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "09:15-09:30": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "09:30-09:45": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "09:45-10:00": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "10:00-10:15": {
                "20191211103154407054140404c00010": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "10:15-10:30": {
                "20191211103154407054140404c00010": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "10:30-10:45": {
                "20191211103154407054140404c00010": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "10:45-11:00": {
                "20191211103154407054140404c00010": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "11:00-11:15": {
                "20191211103154407054140404c00010": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "11:15-11:30": {
                "20191211103154407054140404c00010": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "11:30-11:45": {
                "20191211103154407054140404c00010": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "11:45-12:00": {
                "20191211103154407054140404c00010": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "12:00-12:15": {
                "20191211103154407054140404c00010": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "12:15-12:30": {
                "20191211103154407054140404c00010": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "12:30-12:45": {
                "20191211103154407054140404c00010": {
                    "value": 120,
                    "scope": [
                        120,
                        120
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 120,
                    "scope": [
                        120,
                        120
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 120,
                    "scope": [
                        120,
                        120
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 120,
                    "scope": [
                        120,
                        120
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 120,
                    "scope": [
                        120,
                        120
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 120,
                    "scope": [
                        120,
                        120
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 120,
                    "scope": [
                        120,
                        120
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 120,
                    "scope": [
                        120,
                        120
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "12:45-13:00": {
                "20191211103154407054140404c00010": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "13:00-13:15": {
                "20191211103154407054140404c00010": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "13:15-13:30": {
                "20191211103154407054140404c00010": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 60,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "13:30-13:45": {
                "20191211103154407054140404c00010": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "13:45-14:00": {
                "20191211103154407054140404c00010": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "14:00-14:15": {
                "20191211103154407054140404c00010": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "14:15-14:30": {
                "20191211103154407054140404c00010": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "14:30-14:45": {
                "20191211103154407054140404c00010": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "14:45-15:00": {
                "20191211103154407054140404c00010": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "15:00-15:15": {
                "20191211103154407054140404c00010": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "15:15-15:30": {
                "20191211103154407054140404c00010": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "15:30-15:45": {
                "20191211103154407054140404c00010": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "15:45-16:00": {
                "20191211103154407054140404c00010": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "16:00-16:15": {
                "20191211103154407054140404c00010": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 30,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "16:15-16:30": {
                "20191211103154407054140404c00010": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "16:30-16:45": {
                "20191211103154407054140404c00010": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "16:45-17:00": {
                "20191211103154407054140404c00010": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "17:00-17:15": {
                "20191211103154407054140404c00010": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "17:15-17:30": {
                "20191211103154407054140404c00010": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 90,
                    "scope": [
                        60,
                        90
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "17:30-17:45": {
                "20191211103154407054140404c00010": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "17:45-18:00": {
                "20191211103154407054140404c00010": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "18:00-18:15": {
                "20191211103154407054140404c00010": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "18:15-18:30": {
                "20191211103154407054140404c00010": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "18:30-18:45": {
                "20191211103154407054140404c00010": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "18:45-19:00": {
                "20191211103154407054140404c00010": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 150,
                    "scope": [
                        150,
                        150
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "19:00-19:15": {
                "20191211103154407054140404c00010": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 120,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "19:15-19:30": {
                "20191211103154407054140404c00010": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 120,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "19:30-19:45": {
                "20191211103154407054140404c00010": {
                    "value": 150,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 150,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 150,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 150,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 150,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 150,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 150,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 150,
                    "scope": [
                        120,
                        150
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "19:45-20:00": {
                "20191211103154407054140404c00010": {
                    "value": 90,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 90,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 90,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 90,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 90,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 90,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 90,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 90,
                    "scope": [
                        90,
                        120
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "20:00-20:15": {
                "20191211103154407054140404c00010": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 90,
                    "scope": [
                        90,
                        90
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "20:15-20:30": {
                "20191211103154407054140404c00010": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "20:30-20:45": {
                "20191211103154407054140404c00010": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 60,
                    "scope": [
                        30,
                        60
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "20:45-21:00": {
                "20191211103154407054140404c00010": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 60,
                    "scope": [
                        60,
                        60
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "21:00-21:15": {
                "20191211103154407054140404c00010": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "21:15-21:30": {
                "20191211103154407054140404c00010": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 30,
                    "scope": [
                        30,
                        30
                    ]
                }
            },
            "21:30-21:45": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "21:45-22:00": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "22:00-22:15": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "22:15-22:30": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "22:30-22:45": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "22:45-23:00": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "23:00-23:15": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "23:15-23:30": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "23:30-23:45": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            },
            "23:45-00:00": {
                "20191211103154407054140404c00010": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103130095030140404c00009": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103104704004140404c00008": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211103030448030140404c00007": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102958331058140404c00006": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102923214023140404c00005": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102845913045140404c00004": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102818958018140404c00003": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102753776053140404c00002": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                },
                "20191211102512147012140404c00001": {
                    "value": 0,
                    "scope": [
                        0,
                        0
                    ]
                }
            }
        }
    }
}