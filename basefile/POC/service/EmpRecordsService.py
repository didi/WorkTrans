"""
@author: liyabin
@contact: liyabin_i@didiglobal.com
@file: EmpRecordsService.py
@time: 2019-12-19 13:46
@desc:
"""

from typing import List, Tuple, Dict
from POC.model.EmpRecordsDB import EmpRecordsDB
from utils.dateTimeProcess import DateTimeProcess
from POC.bean.Employee import Employee
import datetime, calendar, json


class EmpRecordsService:
    @staticmethod
    def package_emp_record(cid: str, emps: List, forecastDate: str, emp_rule_dict: Dict, applyId:str,scheme_type: str,legalityBids:List) -> Dict:
        '''
        组装成员工历史记录
        :param cid:
        :param emps:
        :param forecastDate:
        :param emp_rule_dict:
        :param scheme_type:
        :param legalityBids:  部门bids
        :return:
        '''

        workTime_dict = EmpRecordsService.read_workTime(cid=cid,emps=emps,forecastDate=forecastDate, emp_rule_dict=emp_rule_dict,legalityBids=legalityBids,applyId=applyId,scheme_type=scheme_type)
        schDayNum_dict = EmpRecordsService.read_schDayNumCon(cid=cid, emps=emps,forecastDate=forecastDate, emp_rule_dict=emp_rule_dict,legalityBids=legalityBids,applyId=applyId,scheme_type=scheme_type)
        restNumCon_dict = EmpRecordsService.read_restNumCon(cid=cid, emps=emps, forecastDate=forecastDate, emp_rule_dict=emp_rule_dict,legalityBids=legalityBids,applyId=applyId,scheme_type=scheme_type)
        shiftNum_dict = EmpRecordsService.read_shiftNum(cid=cid, emps=emps, forecastDate=forecastDate, emp_rule_dict=emp_rule_dict,legalityBids=legalityBids,applyId=applyId,scheme_type=scheme_type)
        schNumSame_dict = EmpRecordsService.read_schNumSame(cid=cid, emps=emps, forecastDate=forecastDate, emp_rule_dict=emp_rule_dict,legalityBids=legalityBids,applyId=applyId,scheme_type=scheme_type)

        employee_records = {}
        for item in emps:
            eid = item.get('eid', '')

            employee_records[cid + "-" + eid] = {
                "work_date_list": schDayNum_dict.get(cid + '-' + eid + '-' + "days", []),
                "dayWorkTime": int(workTime_dict.get(cid + '-' + eid + '-' + "day" + "-" + "shiftTime", 0)),
                "weekWorkTime": int(workTime_dict.get(cid + '-' + eid + '-' + "week" + "-" + "shiftTime", 0)),
                "monthWorkTime": int(workTime_dict.get(cid + '-' + eid + '-' + "month" + "-" + "shiftTime", 0)) \
                    if int(workTime_dict.get(cid + '-' + eid + '-' + "month" + "-" + "shiftTime", 0)) != 0 \
                    else int(workTime_dict.get(cid + '-' + eid + '-' + "week" + "-" + "shiftTime", 0)),
                "dayShiftNum": int(shiftNum_dict.get(cid + '-' + eid + '-' + "day" + "-" + "shiftNum", 0)),
                "weekShiftNum": int(shiftNum_dict.get(cid + '-' + eid + '-' + "week" + "-" + "shiftNum", 0)),
                "monthShiftNum": int(shiftNum_dict.get(cid + '-' + eid + '-' + "month" + "-" + "shiftNum", 0)),
                "schDayNumCon": int(schDayNum_dict.get(cid + "-" + eid + '-week-schDayNumCon', 0)),
                "schDayNumCon_month": int(schDayNum_dict.get(cid + "-" + eid + '-month-schDayNumCon', 0)),
                "restNumCon": int(restNumCon_dict.get(cid + "-" + eid + '-week-restNumCon', 0)),
                "noSchNum": int(restNumCon_dict.get(cid + "-" + eid + '-week-noSchNum', 0)),
                "restNum": int(restNumCon_dict.get(cid + "-" + eid + '-week-restNum', 0)),
                "schNumSame": schNumSame_dict.get(cid + "-" + eid + '-week-schNumSame', {})
            }


        return employee_records

    @staticmethod
    def read_workTime(cid: str, emps: List, forecastDate: str, emp_rule_dict: Dict,legalityBids:List,applyId:str,scheme_type:str):
        '''
        读取工时记录
        :param cid:
        :param emps:
        :param forecastDate:
        :param emp_rule_dict:
        :return:
        '''
        # 记录员工记录
        emp_worktime_records: Dict = {}


        for item in emps:
            eid = item.get('eid', '')
            legalityBidArr = item.get("legalityBidArr",[])
            legalityBidArr.extend(legalityBids)

            for bid in legalityBidArr:

                # TODO:查找该员工的起始日期。
                emp_key = cid + "-" + bid
                rule_list = emp_rule_dict.get(emp_key, '')
                for rule in rule_list:
                    ruleType = rule.get('ruleType', '')
                    ruletag = rule.get('ruletag', '')
                    cycle = rule.get('cycle', '')

                    # 日工时
                    if ruleType == 'timerule' and ruletag == 'shiftTime' and cycle == 'day':
                        startDate = datetime.datetime.combine(rule.get('startDate', ''), datetime.datetime.min.time())
                        forecastDate = datetime.datetime.strptime(forecastDate, '%Y-%m-%d')

                        timeRange = int(rule.get('timeRange', ''))

                        while (forecastDate >= startDate):
                            startDate = startDate + datetime.timedelta(days=timeRange)

                        endDate = startDate
                        endDate = endDate.strftime('%Y-%m-%d')

                        startDate = (startDate - datetime.timedelta(days=timeRange - 1))    \
                            .strftime('%Y-%m-%d') if startDate > forecastDate else startDate.strftime('%Y-%m-%d')
                        forecastDate = forecastDate.strftime('%Y-%m-%d')

                        empRecords: Tuple = EmpRecordsDB.read_workTime(cid=cid, eid=eid, startDate=startDate,
                                                                       endDate=endDate,applyId=applyId,scheme_type=scheme_type)

                        date_of_workTime = {}
                        for empRecord in empRecords:
                            emp_cid = empRecord[0]
                            emp_applyId = empRecord[1]
                            emp_eid = empRecord[2]
                            emp_type = empRecord[3]
                            schDay = empRecord[4].strftime('%Y-%m-%d')
                            emp_workTime = int(empRecord[5])

                            if date_of_workTime.get(schDay, []):
                                date_of_workTime[schDay].append(empRecord)
                            else:
                                date_of_workTime[schDay] = [empRecord]

                        workTime = 0
                        for strList in date_of_workTime.values():
                            strList.sort(key=lambda x: x[1], reverse=True)
                            workTime += strList[0][5]
                        # 记录员工工时
                        emp_worktime_records[cid + '-' + eid + "-" + 'day' + "-" + 'shiftTime'] = int(workTime)

                    # 周工时
                    elif ruleType == 'timerule' and ruletag == 'shiftTime' and cycle == 'week':
                        startDate = datetime.datetime.combine(rule.get('startDate', ''), datetime.datetime.min.time())
                        forecastDate = datetime.datetime.strptime(forecastDate, '%Y-%m-%d')

                        timeRange = int(rule.get('timeRange', ''))

                        while (forecastDate >= startDate):
                            startDate = startDate + datetime.timedelta(weeks=timeRange)

                        endDate = startDate
                        endDate = endDate.strftime('%Y-%m-%d')

                        startDate = (startDate - datetime.timedelta(weeks=timeRange))   \
                            .strftime('%Y-%m-%d') if startDate > forecastDate else startDate.strftime('%Y-%m-%d')
                        forecastDate = forecastDate.strftime('%Y-%m-%d')

                        # ('51000447', '5100044710000022001576493029', '86', 'task', '2019-07-01', 690.0)
                        empRecords: Tuple = EmpRecordsDB.read_workTime(cid=cid, eid=eid, startDate=startDate,
                                                                       endDate=endDate,applyId=applyId,scheme_type=scheme_type)

                        date_of_workTime = {}
                        for empRecord in empRecords:
                            emp_cid = empRecord[0]
                            emp_applyId = empRecord[1]
                            emp_eid = empRecord[2]
                            emp_type = empRecord[3]
                            schDay = empRecord[4].strftime('%Y-%m-%d')
                            emp_workTime = int(empRecord[5])

                            if date_of_workTime.get(schDay, []):
                                date_of_workTime[schDay].append(empRecord)
                            else:
                                date_of_workTime[schDay] = [empRecord]

                            # date_of_workTime[schDay].append(empRecord) if date_of_workTime.get(schDay, []) else \
                            # date_of_workTime[schDay] = [empRecord]

                        workTime = 0
                        for strList in date_of_workTime.values():
                            strList.sort(key=lambda x: x[1], reverse=True)
                            workTime += strList[0][5]
                        # 记录员工工时
                        emp_worktime_records[cid + '-' + eid + "-" + 'week' + "-" + 'shiftTime'] = int(workTime)

                    # 月工时
                    elif ruleType == 'timerule' and ruletag == 'shiftTime' and cycle == 'month':
                        startDate = datetime.datetime.combine(rule.get('startDate', ''), datetime.datetime.min.time())
                        forecastDate = datetime.datetime.strptime(forecastDate, '%Y-%m-%d')

                        timeRange = int(rule.get('timeRange', ''))

                        while (1):
                            # 获取周期内的天数
                            days = 0
                            for i in range(0, int(timeRange)):
                                # days += calendar.monthrange(forecast_date.year if forecast_date.month + i <= 12 else forecast_date.year +1,
                                #                             forecast_date.month + i if forecast_date.month + i <= 12 else (forecast_date.month + i)//12)[1]
                                days += calendar.monthrange(startDate.year if startDate.month + i <= 12 else startDate.year + 1,
                                                            startDate.month + i if startDate.month + i <= 12 else (startDate.month + i) // 12)[1]
                            startDate = startDate + datetime.timedelta(days=days)

                            if forecastDate < startDate:
                                break
                        days = 0
                        if startDate.month - timeRange != 0:
                            days = calendar.monthrange(startDate.year, startDate.month - timeRange)[1]
                        else:
                            days = 31

                        endDate = startDate
                        endDate = endDate.strftime('%Y-%m-%d')

                        startDate = (startDate - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
                        forecastDate = forecastDate.strftime('%Y-%m-%d')

                        empRecords: Tuple = EmpRecordsDB.read_workTime(cid=cid, eid=eid, startDate=startDate,
                                                                       endDate=endDate,applyId=applyId,scheme_type=scheme_type)

                        date_of_workTime = {}
                        for empRecord in empRecords:
                            emp_cid = empRecord[0]
                            emp_applyId = empRecord[1]
                            emp_eid = empRecord[2]
                            emp_type = empRecord[3]
                            schDay = empRecord[4].strftime('%Y-%m-%d')
                            emp_workTime = empRecord[5]

                            if date_of_workTime.get(schDay, []):
                                date_of_workTime[schDay].append(empRecord)
                            else:
                                date_of_workTime[schDay] = [empRecord]

                        workTime = 0
                        for strList in date_of_workTime.values():
                            strList.sort(key=lambda x: x[1], reverse=True)
                            workTime += strList[0][5]
                        # 记录员工工时
                        emp_worktime_records[cid + '-' + eid + "-" + 'month' + "-" + 'shiftTime'] = int(workTime)

        # {'51000447-86-week-shiftTime': 480, '51000447-85-week-shiftTime': 480, '51000447-84-week-shiftTime': 480, '51000447-83-week-shiftTime': 480, '51000447-83-month-shiftTime': 480}
        # print(emp_worktime_records)
        return emp_worktime_records

    @staticmethod
    def read_schDayNumCon(cid: str, emps: List, forecastDate: str, emp_rule_dict: Dict,legalityBids:List,applyId:str,scheme_type:str):
        '''
        读取连续工作天数
        :param cid:
        :param emps:
        :param forecastDate:
        :param emp_rule_dict:
        :return:
        '''
        # 记录员工记录
        emp_schDayNumCon_records: Dict = {}

        for item in emps:
            eid = item.get('eid', '')
            legalityBidArr = item.get("legalityBidArr", [])
            legalityBidArr.extend(legalityBids)

            for bid in legalityBidArr:

                # TODO:查找该员工的起始日期。
                emp_key = cid + "-" + bid
                rule_list = emp_rule_dict.get(emp_key, '')
                for rule in rule_list:
                    ruleType = rule.get('ruleType', '')
                    ruletag = rule.get('ruletag', '')
                    cycle = rule.get('cycle', '')

                    # 天工时
                    if ruleType == 'daysrule' and ruletag == 'schDayNumCon' and cycle == 'day':
                        startDate = datetime.datetime.combine(rule.get('startDate', ''), datetime.datetime.min.time())
                        forecastDate = datetime.datetime.strptime(forecastDate, '%Y-%m-%d')

                        timeRange = int(rule.get('timeRange', ''))

                        while (forecastDate >= startDate):
                            startDate = startDate + datetime.timedelta(days=timeRange)

                        endDate = startDate
                        endDate = endDate.strftime('%Y-%m-%d')

                        startDate = (startDate - datetime.timedelta(days=timeRange - 1)).strftime(
                            '%Y-%m-%d') if startDate > forecastDate else startDate.strftime('%Y-%m-%d')
                        forecastDate = forecastDate.strftime('%Y-%m-%d')

                        empRecords: Tuple = EmpRecordsDB.read_schDayNumCon_for_cycle(cid=cid, eid=eid, startDate=startDate,
                                                                           endDate=endDate,applyId=applyId,scheme_type=scheme_type)

                        # 记录工作日期
                        work_date_list = []
                        for empRecord in empRecords:
                            emp_cid = empRecord[0]
                            emp_applyId = empRecord[1]
                            emp_eid = empRecord[2]
                            emp_schDay = empRecord[3].strftime('%Y-%m-%d')
                            emp_type = empRecord[4]

                            # 添加工作日期
                            work_date_list.append(emp_schDay)

                        if forecastDate not in work_date_list:
                            work_date_list.append(forecastDate)

                        work_date_list.sort()
                        emp_schDayNumCon_records[cid + "-" + eid + "-" + "day" + "-" + "schDayNumCon"] = Employee.search_max_len_dateStr(work_date_list)
                        emp_schDayNumCon_records[cid + "-" + eid + "-" + "days"] = work_date_list

                    # 周工时
                    elif ruleType == 'daysrule' and ruletag == 'schDayNumCon' and cycle == 'week':
                        startDate = datetime.datetime.combine(rule.get('startDate', ''), datetime.datetime.min.time())
                        forecastDate = datetime.datetime.strptime(forecastDate, '%Y-%m-%d')

                        timeRange = int(rule.get('timeRange', ''))

                        while (forecastDate >= startDate):
                            startDate = startDate + datetime.timedelta(weeks=timeRange)

                        endDate = startDate
                        endDate = endDate.strftime('%Y-%m-%d')
                        startDate = (startDate - datetime.timedelta(weeks=1)).strftime(
                            '%Y-%m-%d') if startDate > forecastDate else startDate.strftime('%Y-%m-%d')
                        forecastDate = forecastDate.strftime('%Y-%m-%d')

                        empRecords: Tuple = EmpRecordsDB.read_schDayNumCon_for_cycle(cid=cid, eid=eid,
                                                                                     startDate=startDate,
                                                                                     endDate=endDate, applyId=applyId,
                                                                                     scheme_type=scheme_type)

                        # 记录工作日期
                        work_date_list = []
                        for empRecord in empRecords:
                            emp_cid = empRecord[0]
                            emp_applyId = empRecord[1]
                            emp_eid = empRecord[2]
                            emp_schDay = empRecord[3].strftime('%Y-%m-%d')
                            emp_type = empRecord[4]

                            # 添加工作日期
                            work_date_list.append(emp_schDay)

                        if forecastDate not in work_date_list:
                            work_date_list.append(forecastDate)

                        work_date_list.sort()
                        emp_schDayNumCon_records[
                            cid + "-" + eid + "-" + "week" + "-" + "schDayNumCon"] = Employee.search_max_len_dateStr(
                            work_date_list)
                        emp_schDayNumCon_records[cid + "-" + eid + "-" + "days"] = work_date_list

                            # 月工时
                    elif ruleType == 'daysrule' and ruletag == 'schDayNumCon' and cycle == 'month':
                        startDate = datetime.datetime.combine(rule.get('startDate', ''), datetime.datetime.min.time())
                        forecastDate = datetime.datetime.strptime(forecastDate, '%Y-%m-%d')

                        timeRange = int(rule.get('timeRange', ''))

                        while (1):
                            # 获取周期内的天数
                            days = 0
                            for i in range(0, int(timeRange)):
                                # days += calendar.monthrange(startDate.year, startDate.month + i)[1]
                                days += calendar.monthrange(startDate.year if startDate.month + i <= 12 else startDate.year + 1,
                                                        startDate.month + i if startDate.month + i <= 12 else (startDate.month + i) // 12)[1]
                            startDate = startDate + datetime.timedelta(days=days)

                            if forecastDate < startDate:
                                break

                        days = 0
                        if startDate.month - timeRange > 0:
                            days = calendar.monthrange(startDate.year, startDate.month - timeRange)[1]
                        else:
                            days = 31

                        endDate = startDate
                        endDate = endDate.strftime('%Y-%m-%d')

                        startDate = (startDate - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
                        forecastDate = forecastDate.strftime('%Y-%m-%d')

                        empRecords: Tuple = EmpRecordsDB.read_schDayNumCon_for_cycle(cid=cid, eid=eid,
                                                                                     startDate=startDate,
                                                                                     endDate=endDate, applyId=applyId,
                                                                                     scheme_type=scheme_type)

                        # 记录工作天数
                        work_date_list = []
                        for empRecord in empRecords:
                            emp_cid = empRecord[0]
                            emp_applyId = empRecord[1]
                            emp_eid = empRecord[2]
                            emp_schDay = empRecord[3].strftime('%Y-%m-%d')
                            emp_type = empRecord[4]

                            # 添加工作日期
                            work_date_list.append(emp_schDay)

                        if forecastDate not in work_date_list:
                            work_date_list.append(forecastDate)

                        work_date_list.sort()
                        emp_schDayNumCon_records[cid + "-" + eid + "-" + "month" + "-" + "schDayNumCon"] = Employee.search_max_len_dateStr(work_date_list)
                        emp_schDayNumCon_records[cid + "-" + eid + "-" + "days"] = work_date_list

        # print(emp_schDayNumCon_records)
        return emp_schDayNumCon_records

    @staticmethod
    def read_restNumCon(cid: str, emps: List, forecastDate: str, emp_rule_dict: Dict,legalityBids:List,applyId:str,scheme_type:str):
        '''
        读取连续休息天数
        :param cid:
        :param emps:
        :param forecastDate:
        :param emp_rule_dict:
        :return:
        '''
        # 记录员工记录
        emp_restNumCon_records: Dict = {}

        for item in emps:
            eid = item.get('eid', '')
            legalityBidArr = item.get("legalityBidArr",[])
            legalityBidArr.extend(legalityBids)

            for bid in legalityBidArr:

                # TODO:查找该员工的起始日期。
                emp_key = cid + "-" + bid
                rule_list = emp_rule_dict.get(emp_key, '')
                for rule in rule_list:
                    ruleType = rule.get('ruleType', '')
                    ruletag = rule.get('ruletag', '')
                    cycle = rule.get('cycle', '')

                    # 天工时
                    if ruleType == 'daysrule' and ruletag == 'restNumCon' and cycle == 'day':
                        startDate = datetime.datetime.combine(rule.get('startDate', ''), datetime.datetime.min.time())
                        forecastDate = datetime.datetime.strptime(forecastDate, '%Y-%m-%d')

                        timeRange = int(rule.get('timeRange', ''))

                        while (forecastDate > startDate):
                            startDate = startDate + datetime.timedelta(days=timeRange)

                        endDate = startDate
                        endDate = endDate.strftime('%Y-%m-%d')

                        startDate = (startDate - datetime.timedelta(days=timeRange - 1)).strftime(
                            '%Y-%m-%d') if startDate > forecastDate else startDate.strftime('%Y-%m-%d')

                        end_day = (forecastDate - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
                        forecastDate = forecastDate.strftime('%Y-%m-%d')

                        empRecords: Tuple = EmpRecordsDB.read_schDayNumCon_for_cycle(cid=cid, eid=eid,
                                                                                     startDate=startDate,
                                                                                     endDate=endDate, applyId=applyId,
                                                                                     scheme_type=scheme_type)

                        date_interval = DateTimeProcess.date_interval(start_day=startDate, end_day=end_day)

                        # 记录工作日期
                        work_date_list = []
                        for empRecord in empRecords:
                            emp_cid = empRecord[0]
                            emp_applyId = empRecord[1]
                            emp_eid = empRecord[2]
                            emp_schDay = empRecord[3].strftime('%Y-%m-%d')
                            emp_type = empRecord[4]

                            # 添加工作日期
                            work_date_list.append(emp_schDay)

                            # 找出未工作天数
                            no_work_list = list(set(date_interval).difference(set(work_date_list)))
                            # 得到的list不一定是按顺序，此处进行排序操作
                            no_work_list.sort()

                            # 连续休息天数
                            emp_restNumCon_records[
                                cid + "-" + eid + "-" + "day" + "-" + "restNumCon"] = Employee.search_max_len_dateStr(
                                no_work_list)
                            # 未排班天数
                            emp_restNumCon_records[cid + "-" + eid + "-" + "day" + "-" + "noSchNum"] = len(no_work_list)
                            # 休息天数
                            emp_restNumCon_records[cid + "-" + eid + "-" + "day" + "-" + "restNum"] = len(no_work_list)

                    # 周工时
                    elif ruleType == 'daysrule' and ruletag == 'restNumCon' and cycle == 'week':
                        startDate = datetime.datetime.combine(rule.get('startDate', ''), datetime.datetime.min.time())
                        forecastDate = datetime.datetime.strptime(forecastDate, '%Y-%m-%d')

                        timeRange = int(rule.get('timeRange', ''))

                        while (forecastDate > startDate):
                            startDate = startDate + datetime.timedelta(weeks=timeRange)

                        endDate = startDate
                        endDate = endDate.strftime('%Y-%m-%d')

                        startDate = (startDate - datetime.timedelta(weeks=1)).strftime(
                            '%Y-%m-%d') if startDate > forecastDate else startDate.strftime('%Y-%m-%d')
                        end_day = (forecastDate - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
                        forecastDate = forecastDate.strftime('%Y-%m-%d')

                        empRecords: Tuple = EmpRecordsDB.read_schDayNumCon_for_cycle(cid=cid, eid=eid,
                                                                                     startDate=startDate,
                                                                                     endDate=endDate, applyId=applyId,
                                                                                     scheme_type=scheme_type)

                        date_interval = DateTimeProcess.date_interval(start_day=startDate, end_day=end_day)
                        # 记录工作日期
                        work_date_list = []
                        for empRecord in empRecords:
                            emp_cid = empRecord[0]
                            emp_applyId = empRecord[1]
                            emp_eid = empRecord[2]
                            emp_schDay = empRecord[3].strftime('%Y-%m-%d')
                            emp_type = empRecord[4]

                            # 添加工作日期
                            work_date_list.append(emp_schDay)

                            # 找出未工作天数
                            no_work_list = list(set(date_interval).difference(set(work_date_list)))
                            # 得到的list不一定是按顺序，此处进行排序操作
                            no_work_list.sort()

                            # 连续休息天数
                            emp_restNumCon_records[
                                cid + "-" + eid + "-" + "week" + "-" + "restNumCon"] = Employee.search_max_len_dateStr(
                                no_work_list)
                            # 未排班天数
                            emp_restNumCon_records[cid + "-" + eid + "-" + "week" + "-" + "noSchNum"] = len(no_work_list)
                            # 休息天数
                            emp_restNumCon_records[cid + "-" + eid + "-" + "week" + "-" + "restNum"] = len(no_work_list)


                    # 月工时
                    elif ruleType == 'daysrule' and ruletag == 'restNumCon' and cycle == 'month':
                        startDate = datetime.datetime.combine(rule.get('startDate', ''), datetime.datetime.min.time())
                        forecastDate = datetime.datetime.strptime(forecastDate, '%Y-%m-%d')

                        timeRange = int(rule.get('timeRange', ''))

                        while (1):
                            # 获取周期内的天数
                            days = 0
                            for i in range(0, int(timeRange)):
                                # days += calendar.monthrange(startDate.year, startDate.month + i)[1]
                                days += calendar.monthrange(startDate.year if startDate.month + i <= 12 else startDate.year + 1,
                                                        startDate.month + i if startDate.month + i <= 12 else (startDate.month + i) // 12)[1]
                            startDate = startDate + datetime.timedelta(days=days)

                            if forecastDate < startDate:
                                break

                        days = 0
                        if startDate.month - timeRange != 0:
                            days = calendar.monthrange(startDate.year, startDate.month - timeRange)[1]
                        else:
                            days = 31

                        endDate = startDate
                        endDate = endDate.strftime('%Y-%m-%d')

                        startDate = (startDate - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
                        end_day = (forecastDate - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
                        forecastDate = forecastDate.strftime('%Y-%m-%d')

                        empRecords: Tuple = EmpRecordsDB.read_schDayNumCon_for_cycle(cid=cid, eid=eid,
                                                                                     startDate=startDate,
                                                                                     endDate=endDate, applyId=applyId,
                                                                                     scheme_type=scheme_type)

                        date_interval = DateTimeProcess.date_interval(start_day=startDate, end_day=end_day)
                        # 记录工作天数
                        work_date_list = []
                        for empRecord in empRecords:
                            emp_cid = empRecord[0]
                            emp_applyId = empRecord[1]
                            emp_eid = empRecord[2]
                            emp_schDay = empRecord[3].strftime('%Y-%m-%d')
                            emp_type = empRecord[4]

                            # 添加工作日期
                            work_date_list.append(emp_schDay)

                            # 找出未工作天数
                            no_work_list = list(set(date_interval).difference(set(work_date_list)))
                            # 得到的list不一定是按顺序，此处进行排序操作
                            no_work_list.sort()

                            # 连续休息天数
                            emp_restNumCon_records[cid + "-" + eid + "-" + "month" + "-" + "restNumCon"] = Employee.search_max_len_dateStr(no_work_list)
                            # 未排班天数
                            emp_restNumCon_records[cid + "-" + eid + "-" + "month" + "-" + "noSchNum"] = len(no_work_list)
                            # 休息天数
                            emp_restNumCon_records[cid + "-" + eid + "-" + "month" + "-" + "restNum"] = len(no_work_list)

        # print(emp_restNumCon_records)
        return emp_restNumCon_records

    @staticmethod
    def read_shiftNum(cid: str, emps: List, forecastDate: str, emp_rule_dict: Dict,legalityBids:List,applyId:str,scheme_type:str):
        '''
        读取班次个数
        :param cid:
        :param emps:
        :param forecastDate:
        :param emp_rule_dict:
        :return:
        '''
        # 记录员工记录
        emp_shiftNum_records: Dict = {}

        for item in emps:
            eid = item.get('eid', '')
            legalityBidArr = item.get("legalityBidArr",[])
            legalityBidArr.extend(legalityBids)

            for bid in legalityBidArr:
            # TODO:查找该员工的起始日期。
                emp_key = cid + "-" + bid
                rule_list = emp_rule_dict.get(emp_key, '')
                for rule in rule_list:
                    ruleType = rule.get('ruleType', '')
                    ruletag = rule.get('ruletag', '')
                    cycle = rule.get('cycle', '')

                    # 周工时
                    if ruleType == "shiftrule" and ruletag == 'schShiftNum' and cycle == 'day':

                        startDate = datetime.datetime.combine(rule.get('startDate', ''), datetime.datetime.min.time())
                        forecastDate = datetime.datetime.strptime(forecastDate, '%Y-%m-%d')

                        timeRange = int(rule.get('timeRange', ''))

                        while (forecastDate > startDate):
                            startDate = startDate + datetime.timedelta(days=timeRange)

                        endDate = startDate
                        endDate = endDate.strftime('%Y-%m-%d')

                        startDate = (startDate - datetime.timedelta(days=timeRange - 1)).strftime(
                            '%Y-%m-%d') if startDate > forecastDate else startDate.strftime('%Y-%m-%d')
                        forecastDate = forecastDate.strftime('%Y-%m-%d')

                        empRecords: Tuple = EmpRecordsDB.read_shiftNum(cid=cid, eid=eid, startDate=startDate,
                                                                       endDate=endDate,applyId=applyId,scheme_type=scheme_type)

                        # cid,applyId,eid,schDay,startTime,endTime,workTime
                        date_of_shift = {}
                        for empRecord in empRecords:
                            emp_cid = empRecord[0]
                            emp_applyId = empRecord[1]
                            emp_eid = empRecord[2]
                            emp_schDay = empRecord[3].strftime('%Y-%m-%d')
                            emp_startTime = empRecord[4]
                            emp_endTime = empRecord[5]

                            if date_of_shift.get(emp_schDay, []):
                                date_of_shift[emp_schDay].append(empRecord)
                            else:
                                date_of_shift[emp_schDay] = [empRecord]

                        shiftNum = 0
                        for strList in date_of_shift.values():
                            strList.sort(key=lambda x: x[1], reverse=True)
                            maxApplyId = strList[0][1]
                            maxApplyIdList = [x for x in strList if x[1] == maxApplyId]
                            shiftNum += len(maxApplyIdList)

                        # 记录员工工时
                        emp_shiftNum_records[cid + '-' + eid + "-" + 'day' + "-" + 'shiftNum'] = shiftNum

                    # 周工时
                    elif ruleType == 'shiftrule' and ruletag == 'schShiftNum' and cycle == 'week':
                        startDate = datetime.datetime.combine(rule.get('startDate', ''), datetime.datetime.min.time())
                        forecastDate = datetime.datetime.strptime(forecastDate, '%Y-%m-%d')

                        timeRange = int(rule.get('timeRange', ''))

                        while (forecastDate > startDate):
                            startDate = startDate + datetime.timedelta(weeks=timeRange)

                        endDate = startDate
                        endDate = endDate.strftime('%Y-%m-%d')

                        startDate = (startDate - datetime.timedelta(weeks=timeRange)).strftime(
                            '%Y-%m-%d') if startDate > forecastDate else startDate.strftime('%Y-%m-%d')
                        forecastDate = forecastDate.strftime('%Y-%m-%d')

                        empRecords: Tuple = EmpRecordsDB.read_shiftNum(cid=cid, eid=eid, startDate=startDate,
                                                                       endDate=endDate, applyId=applyId,
                                                                       scheme_type=scheme_type)

                        # cid,applyId,eid,schDay,startTime,endTime,workTime
                        date_of_shift = {}
                        for empRecord in empRecords:
                            emp_cid = empRecord[0]
                            emp_applyId = empRecord[1]
                            emp_eid = empRecord[2]
                            emp_schDay = empRecord[3].strftime('%Y-%m-%d')
                            emp_startTime = empRecord[4]
                            emp_endTime = empRecord[5]

                            if date_of_shift.get(emp_schDay, []):
                                date_of_shift[emp_schDay].append(empRecord)
                            else:
                                date_of_shift[emp_schDay] = [empRecord]

                        shiftNum = 0
                        for strList in date_of_shift.values():
                            strList.sort(key=lambda x: x[1], reverse=True)
                            maxApplyId = strList[0][1]
                            maxApplyIdList = [x for x in strList if x[1] == maxApplyId]
                            shiftNum += len(maxApplyIdList)
                        # 记录员工工时
                        emp_shiftNum_records[cid + '-' + eid + "-" + 'week' + "-" + 'shiftNum'] = shiftNum

                    # 月工时
                    elif ruleType == 'shiftrule' and ruletag == 'schShiftNum' and cycle == 'month':
                        startDate = datetime.datetime.combine(rule.get('startDate', ''), datetime.datetime.min.time())
                        forecastDate = datetime.datetime.strptime(forecastDate, '%Y-%m-%d')

                        timeRange = int(rule.get('timeRange', ''))

                        while (1):
                            # 获取周期内的天数
                            days = 0
                            for i in range(0, int(timeRange)):
                                # days += calendar.monthrange(startDate.year, startDate.month + i)[1]
                                days += \
                                    calendar.monthrange(startDate.year if startDate.month + i <= 12 else startDate.year + 1,
                                                        startDate.month + i if startDate.month + i <= 12 else (
                                                                                                                      startDate.month + i) // 12)[
                                        1]
                            startDate = startDate + datetime.timedelta(days=days)

                            if forecastDate < startDate:
                                break

                        days = 0
                        if startDate.month - timeRange != 0:
                            days = calendar.monthrange(startDate.year, startDate.month - timeRange)[1]
                        else:
                            days = 31

                        endDate = startDate
                        endDate = endDate.strftime('%Y-%m-%d')

                        startDate = (startDate - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
                        forecastDate = forecastDate.strftime('%Y-%m-%d')

                        empRecords: Tuple = EmpRecordsDB.read_shiftNum(cid=cid, eid=eid, startDate=startDate,
                                                                       endDate=endDate, applyId=applyId,
                                                                       scheme_type=scheme_type)
                        # cid,applyId,eid,schDay,startTime,endTime,workTime
                        date_of_shift = {}
                        for empRecord in empRecords:
                            emp_cid = empRecord[0]
                            emp_applyId = empRecord[1]
                            emp_eid = empRecord[2]
                            emp_schDay = empRecord[3].strftime('%Y-%m-%d')
                            emp_startTime = empRecord[4]
                            emp_endTime = empRecord[5]

                            if date_of_shift.get(emp_schDay, []):
                                date_of_shift[emp_schDay].append(empRecord)
                            else:
                                date_of_shift[emp_schDay] = [empRecord]

                        shiftNum = 0
                        for strList in date_of_shift.values():
                            strList.sort(key=lambda x: x[1], reverse=True)
                            maxApplyId = strList[0][1]
                            maxApplyIdList = [x for x in strList if x[1] == maxApplyId]
                            shiftNum += len(maxApplyIdList)
                        # 记录员工工时
                        emp_shiftNum_records[cid + '-' + eid + "-" + 'month' + "-" + 'shiftNum'] = shiftNum

        # {'51000447-86-week-shiftTime': 480, '51000447-85-week-shiftTime': 480, '51000447-84-week-shiftTime': 480, '51000447-83-week-shiftTime': 480, '51000447-83-month-shiftTime': 480}
        #print(emp_shiftNum_records)
        return emp_shiftNum_records

    @staticmethod
    def read_schNumSame(cid: str, emps: List, forecastDate: str, emp_rule_dict: Dict, applyId:str,scheme_type: str,legalityBids:List):
        # 记录员工记录
        emp_schNumSame_records: Dict = {}

        for item in emps:
            eid = item.get('eid', '')
            legalityBidArr = item.get("legalityBidArr",[])
            legalityBidArr.extend(legalityBids)

            for bid in legalityBidArr:

            # TODO:查找该员工的起始日期。
                emp_key = cid + "-" + bid
                rule_list = emp_rule_dict.get(emp_key, '')
                for rule in rule_list:
                    ruleType = rule.get('ruleType', 'timerule')
                    ruletag = rule.get('ruletag', 'shiftTime')
                    cycle = rule.get('cycle', 'day')

                    # 比较的值
                    ruleCpType = rule.get('ruleCpType', 'lt')
                    ruleCpNum = rule.get('ruleCpNum', '0')

                    if ruleType == 'daysrule' and ruletag == 'schNumSame' and cycle == 'week':
                        startDate = datetime.datetime.combine(rule.get('startDate', ''), datetime.datetime.min.time())
                        forecastDate = datetime.datetime.strptime(forecastDate, '%Y-%m-%d')

                        timeRange = int(rule.get('timeRange', ''))

                        while (forecastDate > startDate):
                            startDate = startDate + datetime.timedelta(weeks=timeRange)

                        endDate = startDate
                        endDate = endDate.strftime('%Y-%m-%d')

                        startDate = (startDate - datetime.timedelta(weeks=1)).strftime(
                            '%Y-%m-%d') if startDate > forecastDate else startDate.strftime('%Y-%m-%d')
                        end_day = (forecastDate - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
                        forecastDate = forecastDate.strftime('%Y-%m-%d')

                        empRecords: Tuple = EmpRecordsDB.read_schNumSame(cid=cid, startDate=startDate, endDate=end_day,
                                                                         applyId=applyId,scheme_type=scheme_type)

                        # 记录工作日期
                        work_time_list = {}

                        for empRecord in empRecords:
                            emp_cid = empRecord[0]
                            emp_applyId = empRecord[1]
                            emp_eid = empRecord[2]
                            emp_schDay = empRecord[3].strftime('%Y-%m-%d')
                            emp_type = empRecord[4]
                            emp_startTime = empRecord[5].split(" ")[-1]
                            emp_endTime = empRecord[6].split(" ")[-1]

                            if cid != emp_cid or eid != emp_eid: continue

                            key = emp_eid + '-' + emp_schDay
                            if key not in work_time_list:
                                work_time_list[key] = emp_startTime + "-" + emp_endTime
                            else:

                                if emp_startTime in work_time_list[key] and '***' not in work_time_list[key]:
                                    # 开始时间是已有工作的结束事件，更新结束时间
                                    start_time = work_time_list[key].split('-')[0]
                                    work_time_list[key] = start_time + "-" + emp_endTime

                                elif emp_startTime in work_time_list[key] and '***' in work_time_list[key]:
                                    # 因记录已经排序，所以形如:'09:00-11:00***13:00-14:00',startTime为'14：00'

                                    # 将两个时间段切割
                                    time_arr = work_time_list[key].split('***')
                                    last_time = time_arr[-1]
                                    last_time = last_time.split('-')[0] + '-' + emp_endTime
                                    time_arr[-1] = last_time

                                    timestr2 = '***'.join(time_arr)
                                    # print(timestr2)

                                    work_time_list[key] = timestr2

                                elif emp_startTime not in work_time_list[key]:
                                    # 开始时间不包含在员工已有工作时间中，拼接
                                    work_time_list[key] = work_time_list[key] + '***' + emp_startTime + "-" + emp_endTime

                            # 相同排班记录
                            emp_schNumSame_records[cid + "-" + eid + "-" + "week" + "-" + "schNumSame"] = work_time_list

                    # 月工时
                    elif ruleType == 'daysrule' and ruletag == 'schNumSame' and cycle == 'month':
                        startDate = datetime.datetime.combine(rule.get('startDate', ''), datetime.datetime.min.time())
                        forecastDate = datetime.datetime.strptime(forecastDate, '%Y-%m-%d')

                        timeRange = int(rule.get('timeRange', ''))

                        while (1):
                            # 获取周期内的天数
                            days = 0
                            for i in range(0, int(timeRange)):
                                # days += calendar.monthrange(startDate.year, startDate.month + i)[1]
                                days += \
                                    calendar.monthrange(startDate.year if startDate.month + i <= 12 else startDate.year + 1,
                                                        startDate.month + i if startDate.month + i <= 12 else (startDate.month + i) // 12)[1]
                            startDate = startDate + datetime.timedelta(days=days)

                            if forecastDate < startDate:
                                break

                        days = 0
                        if startDate.month - timeRange != 0:
                            days = calendar.monthrange(startDate.year, startDate.month - timeRange)[1]
                        else:
                            days = 31

                        endDate = startDate
                        endDate = endDate.strftime('%Y-%m-%d')

                        startDate = (startDate - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
                        end_day = (forecastDate - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
                        forecastDate = forecastDate.strftime('%Y-%m-%d')

                        empRecords: Tuple = EmpRecordsDB.read_schNumSame(cid=cid, startDate=startDate, endDate=end_day,
                                                                         applyId=applyId, scheme_type=scheme_type)

                        # 记录工作日期
                        work_time_list = {}

                        for empRecord in empRecords:
                            emp_cid = empRecord[0]
                            emp_applyId = empRecord[1]
                            emp_eid = empRecord[2]
                            emp_schDay = empRecord[3].strftime('%Y-%m-%d')
                            emp_type = empRecord[4]
                            emp_startTime = empRecord[5].split(" ")[-1]
                            emp_endTime = empRecord[6].split(" ")[-1]

                            if cid != emp_cid or eid != emp_eid: continue

                            key = emp_eid + '-' + emp_schDay
                            if key not in work_time_list:
                                work_time_list[key] = emp_startTime + "-" + emp_endTime
                            else:

                                if emp_startTime in work_time_list[key] and '***' not in work_time_list[key]:
                                    # 开始时间是已有工作的结束事件，更新结束时间
                                    start_time = work_time_list[key].split('-')[0]
                                    work_time_list[key] = start_time + "-" + emp_endTime

                                elif emp_startTime in work_time_list[key] and '***' in work_time_list[key]:
                                    # 因记录已经排序，所以形如:'09:00-11:00***13:00-14:00',startTime为'14：00'

                                    # 将两个时间段切割
                                    time_arr = work_time_list[key].split('***')
                                    last_time = time_arr[-1]
                                    last_time = last_time.split('-')[0] + '-' + emp_endTime
                                    time_arr[-1] = last_time

                                    timestr2 = '***'.join(time_arr)
                                    # print(timestr2)

                                    work_time_list[key] = timestr2

                                elif emp_startTime not in work_time_list[key]:
                                    # 开始时间不包含在员工已有工作时间中，拼接
                                    work_time_list[key] = work_time_list[key] + '***' + emp_startTime + "-" + emp_endTime

                            # 相同排班记录
                            emp_schNumSame_records[cid + "-" + eid + "-" + "month" + "-" + "schNumSame"] = work_time_list

        # print(emp_restNumCon_records)

        # 计数
        for emp_record in emp_schNumSame_records:
            worktime_dict = emp_schNumSame_records[emp_record]

            count = {}
            for value in worktime_dict.values():
                if value in count:
                    count[value] += 1
                else:
                    count[value] = 1
            emp_schNumSame_records[emp_record] = count

        return emp_schNumSame_records


if __name__ == '__main__':
    pass
