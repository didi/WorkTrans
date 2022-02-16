import datetime,calendar
from typing import Dict,Tuple,List,Set
from POC.bean.Employee import Employee



class InitRecord:
    @staticmethod
    def init_dayworkTime(emp:Employee,emp_rule_dict:Dict,forecast_date:str,ptype:str) -> bool:
        '''
        生成员工记录
        初始化周期数据 -- 工时
        用于第二天的初始化
        :param emp:
        :param emp_rule_dict:
        :param forecast_date:
        :param ptype:
        :return:
        '''
        key = emp.cid+'-'+emp.eid+'-'+ptype

        forecast_date = datetime.datetime.strptime(forecast_date, "%Y-%m-%d")

        emp_rule:List = emp_rule_dict.get(key,'')

        for item in emp_rule:

            ruleType = item["ruleType"]
            ruletag = item["ruletag"]
            # 班次工时 合规性

            if (ruleType == "timerule" and ruletag == "shiftTime"):
                startDate = item["startDate"]
                timeRange = int(item["timeRange"])
                cycle = item["cycle"]
                # 需要对应上当前时间

                if (cycle == "day" and (forecast_date + datetime.timedelta(days=1) - datetime.datetime.strptime(str(startDate), '%Y-%m-%d')).days % (1 * timeRange) == 0):
                    return True

        return False

    @staticmethod
    def init_weekWorkTime(emp: Employee, emp_rule_dict: Dict, forecast_date: str, ptype: str) -> bool:
        '''
        生成员工记录
        初始化周期数据 -- 工时
        用于第二天的初始化
        :param emp:
        :param emp_rule_dict:
        :param forecast_date:
        :param ptype:
        :return:
        '''
        key = emp.cid + '-' + emp.eid + '-' + ptype

        forecast_date = datetime.datetime.strptime(forecast_date, "%Y-%m-%d")

        emp_rule: List = emp_rule_dict.get(key, '')

        for item in emp_rule:

            ruleType = item["ruleType"]
            ruletag = item["ruletag"]
            # 班次工时 合规性

            if (ruleType == "timerule" and ruletag == "shiftTime"):
                startDate = item["startDate"]
                timeRange = int(item["timeRange"])
                cycle = item["cycle"]
                # 需要对应上当前时间

                if (cycle == "week" and (forecast_date + datetime.timedelta(days=1) - datetime.datetime.strptime(str(startDate),'%Y-%m-%d')).days % (7 * timeRange) == 0):
                    return True

        return False

    @staticmethod
    def init_monthWorkTime(emp: Employee, emp_rule_dict: Dict, forecast_date: str, ptype: str) -> bool:
        '''
        生成员工记录
        初始化周期数据 -- 工时
        用于第二天的初始化
        :param emp:
        :param emp_rule_dict:
        :param forecast_date:
        :param ptype:
        :return:
        '''
        key = emp.cid + '-' + emp.eid + '-' + ptype

        forecast_date = datetime.datetime.strptime(forecast_date, "%Y-%m-%d")

        emp_rule: List = emp_rule_dict.get(key, '')

        for item in emp_rule:

            ruleType = item["ruleType"]
            ruletag = item["ruletag"]
            # 班次工时 合规性

            if (ruleType == "timerule" and ruletag == "shiftTime"):
                startDate = item["startDate"]
                timeRange = int(item["timeRange"])
                cycle = item["cycle"]
                # 需要对应上当前时间

                if (cycle == "month"):
                    # 获取周期内的天数
                    days = 0
                    for i in range(0, int(timeRange)):
                        days += calendar.monthrange(forecast_date.year if forecast_date.month + i <= 12 else forecast_date.year +1,
                                                    forecast_date.month + i if forecast_date.month + i <= 12 else (forecast_date.month + i)//12)[1]
                    if ((forecast_date + datetime.timedelta(days=1) - datetime.datetime.strptime(str(startDate),'%Y-%m-%d')).days % days == 0):
                        return True
        return False

    @staticmethod
    def init_schDayNumCon(emp:Employee,emp_rule_dict:Dict,forecast_date:str,ptype:str):
        '''
        连续工作天数
        :param emp:
        :param emp_rule_dict:
        :param forecast_date:
        :param ptype:
        :return:
        '''
        key = emp.cid + '-' + emp.eid + '-' + ptype

        forecast_date = datetime.datetime.strptime(forecast_date, "%Y-%m-%d")

        emp_rule: List = emp_rule_dict.get(key, '')

        for item in emp_rule:

            ruleType = item["ruleType"]
            ruletag = item["ruletag"]
            # 班次工时 合规性

            if (ruleType == "dayrule" and ruletag == "schDayNumCon"):
                startDate = item["startDate"]
                timeRange = int(item["timeRange"])
                cycle = item["cycle"]
                # 需要对应上当前时间

                if (cycle == "day" and (forecast_date + datetime.timedelta(days=1) - datetime.datetime.strptime(str(startDate),'%Y-%m-%d')).days % (1 * timeRange) == 0):
                    return True
                elif (cycle == "week" and (forecast_date + datetime.timedelta(days=1) - datetime.datetime.strptime(str(startDate),'%Y-%m-%d')).days % (7 * timeRange) == 0):
                    return True
                elif (cycle == "month"):
                    # 获取周期内的天数
                    days = 0
                    for i in range(0, int(timeRange)):
                        days += calendar.monthrange(forecast_date.year, forecast_date.month + i)[1]
                    if ((forecast_date + datetime.timedelta(days=1) - datetime.datetime.strptime(str(startDate),'%Y-%m-%d')).days % days == 0):
                        return True
        return False

    @staticmethod
    def init_restNumCon(emp:Employee,emp_rule_dict:Dict,forecast_date:str,ptype:str):
        '''
        连续休息天数
        :param emp:
        :param emp_rule_dict:
        :param forecast_date:
        :param ptype:
        :return:
        '''
        key = emp.cid + '-' + emp.eid + '-' + ptype

        forecast_date = datetime.datetime.strptime(forecast_date, "%Y-%m-%d")

        emp_rule: List = emp_rule_dict.get(key, '')

        for item in emp_rule:

            ruleType = item["ruleType"]
            ruletag = item["ruletag"]
            # 班次工时 合规性

            if (ruleType == "dayrule" and ruletag == "restNumCon"):
                startDate = item["startDate"]
                timeRange = int(item["timeRange"])
                cycle = item["cycle"]
                # 需要对应上当前时间

                if (cycle == "day" and (
                        forecast_date + datetime.timedelta(days=1) - datetime.datetime.strptime(str(startDate),
                                                                                                '%Y-%m-%d')).days % (
                        1 * timeRange) == 0):
                    return True
                elif (cycle == "week" and (
                        forecast_date + datetime.timedelta(days=1) - datetime.datetime.strptime(str(startDate),
                                                                                                '%Y-%m-%d')).days % (
                              7 * timeRange) == 0):
                    return True
                elif (cycle == "month"):
                    # 获取周期内的天数
                    days = 0
                    for i in range(0, int(timeRange)):
                        days += calendar.monthrange(forecast_date.year, forecast_date.month + i)[1]
                    if ((forecast_date + datetime.timedelta(days=1) - datetime.datetime.strptime(str(startDate),
                                                                                                 '%Y-%m-%d')).days % days == 0):
                        return True
        return False

    @staticmethod
    def init_noSchNum(emp:Employee,emp_rule_dict:Dict,forecast_date:str,ptype:str):
        '''
        未排班天数
        :param emp:
        :param emp_rule_dict:
        :param forecast_date:
        :param ptype:
        :return:
        '''
        key = emp.cid + '-' + emp.eid + '-' + ptype

        forecast_date = datetime.datetime.strptime(forecast_date, "%Y-%m-%d")

        emp_rule: List = emp_rule_dict.get(key, '')

        for item in emp_rule:

            ruleType = item["ruleType"]
            ruletag = item["ruletag"]
            # 班次工时 合规性

            if (ruleType == "dayrule" and ruletag == "noSchNum"):
                startDate = item["startDate"]
                timeRange = int(item["timeRange"])
                cycle = item["cycle"]
                # 需要对应上当前时间

                if (cycle == "day" and (
                        forecast_date + datetime.timedelta(days=1) - datetime.datetime.strptime(str(startDate),
                                                                                                '%Y-%m-%d')).days % (
                        1 * timeRange) == 0):
                    return True
                elif (cycle == "week" and (
                        forecast_date + datetime.timedelta(days=1) - datetime.datetime.strptime(str(startDate),
                                                                                                '%Y-%m-%d')).days % (
                              7 * timeRange) == 0):
                    return True
                elif (cycle == "month"):
                    # 获取周期内的天数
                    days = 0
                    for i in range(0, int(timeRange)):
                        days += calendar.monthrange(forecast_date.year, forecast_date.month + i)[1]
                    if ((forecast_date + datetime.timedelta(days=1) - datetime.datetime.strptime(str(startDate),
                                                                                                 '%Y-%m-%d')).days % days == 0):
                        return True
        return False

    @staticmethod
    def init_restNum(emp:Employee,emp_rule_dict:Dict,forecast_date:str,ptype:str):
        '''
        休息天数
        :param emp:
        :param emp_rule_dict:
        :param forecast_date:
        :param ptype:
        :return:
        '''
        key = emp.cid + '-' + emp.eid + '-' + ptype

        forecast_date = datetime.datetime.strptime(forecast_date, "%Y-%m-%d")

        emp_rule: List = emp_rule_dict.get(key, '')

        for item in emp_rule:

            ruleType = item["ruleType"]
            ruletag = item["ruletag"]
            # 班次工时 合规性

            if (ruleType == "dayrule" and ruletag == "restNum"):
                startDate = item["startDate"]
                timeRange = int(item["timeRange"])
                cycle = item["cycle"]
                # 需要对应上当前时间

                if (cycle == "day" and (
                        forecast_date + datetime.timedelta(days=1) - datetime.datetime.strptime(str(startDate),
                                                                                                '%Y-%m-%d')).days % (
                        1 * timeRange) == 0):
                    return True
                elif (cycle == "week" and (
                        forecast_date + datetime.timedelta(days=1) - datetime.datetime.strptime(str(startDate),
                                                                                                '%Y-%m-%d')).days % (
                              7 * timeRange) == 0):
                    return True
                elif (cycle == "month"):
                    # 获取周期内的天数
                    days = 0
                    for i in range(0, int(timeRange)):
                        days += calendar.monthrange(forecast_date.year, forecast_date.month + i)[1]
                    if ((forecast_date + datetime.timedelta(days=1) - datetime.datetime.strptime(str(startDate),
                                                                                                 '%Y-%m-%d')).days % days == 0):
                        return True
        return False


    '''
    if(e.dayWorkTime > 0):
                    # 临时工 不进行记录
                    if(int(e.eid) <0):continue

                    e.work_date_list.append(day)
                    employee_records[e.cid + "-" + e.eid]["work_date_list"] = e.work_date_list
                    # 工时
                    employee_records[e.cid + "-" + e.eid]["dayWorkTime"] = 0 if(InitRecord.init_dayworkTime(emp=e,emp_rule_dict=emp_rule_dict,forecast_date=day,ptype='emprule')) else e.dayWorkTime
                    employee_records[e.cid + "-" + e.eid]["weekWorkTime"] = 0 if (InitRecord.init_weekWorkTime(emp=e, emp_rule_dict=emp_rule_dict, forecast_date=day,ptype='emprule')) else e.weekWorkTime
                    employee_records[e.cid + "-" + e.eid]["monthWorkTime"] = 0 if (InitRecord.init_monthWorkTime(emp=e, emp_rule_dict=emp_rule_dict, forecast_date=day,ptype='emprule')) else e.monthWorkTime

                    # 班次
                    employee_records[e.cid + "-" + e.eid]["dayShiftNum"] = e.dayShiftNum
                    employee_records[e.cid +"-"+ e.eid]["weekShiftNum"] = e.weekShiftNum
                    employee_records[e.cid +"-"+ e.eid]["monthShiftNum"] = e.monthShiftNum

                    # 改变员工域的值
                    e.set_con_work()
                    # 设置dayrule
                    employee_records[e.cid + "-" + e.eid]["schDayNumCon"] = 0 if(InitRecord.init_schDayNumCon(emp=e, emp_rule_dict=emp_rule_dict, forecast_date=day,ptype='emprule')) else e.schDayNumCon
                    employee_records[e.cid + "-" + e.eid]["restNumCon"] = 0 if (InitRecord.init_restNumCon(emp=e, emp_rule_dict=emp_rule_dict, forecast_date=day,ptype='emprule')) else e.restNumCon
                    employee_records[e.cid + "-" + e.eid]["noSchNum"] = 0 if (InitRecord.init_noSchNum(emp=e, emp_rule_dict=emp_rule_dict, forecast_date=day,ptype='emprule')) else e.noSchNum
                    employee_records[e.cid + "-" + e.eid]["restNum"] = 0 if (InitRecord.init_restNum(emp=e, emp_rule_dict=emp_rule_dict, forecast_date=day,ptype='emprule')) else e.restNum

                elif(e.dayWorkTime == 0):
                    # 临时工 不进行记录
                    if (int(e.eid) < 0): continue

                    employee_records[e.cid + "-" + e.eid]["work_date_list"] = e.work_date_list
                    # 工时
                    # 工时
                    employee_records[e.cid + "-" + e.eid]["dayWorkTime"] = 0 if (InitRecord.init_dayworkTime(emp=e, emp_rule_dict=emp_rule_dict, forecast_date=day,ptype='emprule')) else e.dayWorkTime
                    employee_records[e.cid + "-" + e.eid]["weekWorkTime"] = 0 if (InitRecord.init_weekWorkTime(emp=e, emp_rule_dict=emp_rule_dict, forecast_date=day,ptype='emprule')) else e.weekWorkTime
                    employee_records[e.cid + "-" + e.eid]["monthWorkTime"] = 0 if (InitRecord.init_monthWorkTime(emp=e, emp_rule_dict=emp_rule_dict, forecast_date=day,ptype='emprule')) else e.monthWorkTime

                    # 班次
                    employee_records[e.cid + "-" + e.eid]["dayShiftNum"] = e.dayShiftNum
                    employee_records[e.cid + "-" + e.eid]["weekShiftNum"] = e.weekShiftNum
                    employee_records[e.cid + "-" + e.eid]["monthShiftNum"] = e.monthShiftNum

                    # 改变员工域的值
                    no_work_list = list(set(forecast_days[0:day_index+1]).difference(set(e.work_date_list)))
                    # 得到的list不一定是按顺序，此处进行排序操作
                    no_work_list.sort()
                    e.set_not_work(no_work_list=no_work_list)

                    #设置dayrule
                    employee_records[e.cid + "-" + e.eid]["schDayNumCon"] = 0 if (InitRecord.init_schDayNumCon(emp=e, emp_rule_dict=emp_rule_dict, forecast_date=day,ptype='emprule')) else e.schDayNumCon
                    employee_records[e.cid + "-" + e.eid]["restNumCon"] = 0 if (InitRecord.init_restNumCon(emp=e, emp_rule_dict=emp_rule_dict, forecast_date=day,ptype='emprule')) else e.restNumCon
                    employee_records[e.cid + "-" + e.eid]["noSchNum"] = 0 if (InitRecord.init_noSchNum(emp=e, emp_rule_dict=emp_rule_dict, forecast_date=day,ptype='emprule')) else e.noSchNum
                    employee_records[e.cid + "-" + e.eid]["restNum"] = 0 if (InitRecord.init_restNum(emp=e, emp_rule_dict=emp_rule_dict, forecast_date=day,ptype='emprule')) else e.restNum
    '''