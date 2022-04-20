'''
create by liyabin
'''

from typing import Dict,List,Tuple
import datetime
from utils.dateTimeProcess import DateTimeProcess
from POC.model.forecast_task_DB import ForecastTaskDB

class Employee:

    def __init__(self,cid:str,eid:str,work_date_list:List,skill:list,skillNum:list,cret_closingdate:Dict,
                 dayWorkTime:int,weekWorkTime:int,monthWorkTime:int,available_timeList:List,tasks:List,bids:List,
                 dayShiftNum:int,weekShiftNum:int,monthShiftNum:int,schDayNumCon_week:int,schDayNumCon_month:int,restNumCon:int,noSchNum:int,
                 restNum:int,schNumSame:Dict,isNew:str = 'no',hireType:str = 'full',agreeOverTime:str = 'no',leadNew:str = 'no'):
        """
        员工基础属性
        :param cid: 公司id
        :param eid: 工号
        :param skill: 技能id
        :param skillNum: 技能值
        :param certname: 证书名称
        :param closingdate: 到期时间
        :param dayWorkTime: 日工时
        :param weekWorkTime: 周工时
        :param monthWorkTime: 月工时
        """
        self.cid = cid
        # 未分配任务，默认""
        self.did = ""
        self.eid = eid
        self.work_date_list = work_date_list
        self.skill = skill
        self.skillNum = skillNum
        self.cret_closingdate = cret_closingdate
        self.dayWorkTime = dayWorkTime
        self.weekWorkTime = weekWorkTime
        self.monthWorkTime = monthWorkTime
        # 格式： {"日期":"06:00-12:00"}
        #self.available = available
        self.available_timeList = available_timeList
        # 被分配的任务列表
        self.tasks = tasks
        # 被排班次个数
        self.dayShiftNum = dayShiftNum
        self.weekShiftNum = weekShiftNum
        self.monthShiftNum = monthShiftNum
        # 匹配属性
        self.weight = 1
        # 合规性
        self.bids = bids
        self.caution = ""
        # 员工连续排班天数
        self.schDayNumCon_week = schDayNumCon_week
        self.schDayNumCon_month = schDayNumCon_month

        # 连续休息天数
        self.restNumCon = restNumCon
        # 未排班天数
        self.noSchNum = noSchNum
        # 休息天数
        self.restNum = restNum
        # 相同排班天数
        self.schNumSame = schNumSame

        # 违反软约束的个数
        self.break_rule_num = 0
        # 违反的约束列表
        self.break_rule_list = []

        # 匹配属性
        # 是否为新人（yes, no）
        self.isNew = True if isNew == 'yes' else False
        # 雇佣类型（full: 全职， part: 兼职）
        self.hireType = True if hireType == 'full' else False
        # 是否同意加班（yes, no）
        self.agreeOverTime = True if agreeOverTime == 'yes' else False
        # 是否愿意带新人（yes, no）
        self.leadNew = True if leadNew == 'yes' else False

        self.forbid_rule_set = set()


    def set_forbid_rule_set(self,forbid_rule_set):
        '''
        设置违反规则集合
        :param forbid_rule_set:
        :return:
        '''
        self.forbid_rule_set = forbid_rule_set

    def set_break_rule_list(self,break_rule_list):
        '''
        添加违反的约束
        :param break_rule_list:
        :return:
        '''
        self.break_rule_list.extend(break_rule_list)

    def set_shift_num(self):
        '''
        设置班次个数
        :return:
        '''
        self.dayShiftNum += 1
        self.weekShiftNum += 1
        self.monthShiftNum += 1

    def set_cret_closingDate(self,cret_closingdate):
        '''
        设置证书及到期时间
        :param cret_closingdate:
        :return:
        '''
        self.cret_closingdate = cret_closingdate

    def set_available_time(self,available,type,available_timeList):
        '''
        设置员工可用性（日期：时间）
        :param available:
        :return:
        '''
        self.available = available
        self.type = type
        self.available_timeList = available_timeList

    def set_break_rule_num(self,break_rule_num):
        '''
        添加违反软约束的个数
        :param break_rule_num:
        :return:
        '''
        self.break_rule_num += break_rule_num

    def set_worktime(self,workTime:int,emp_matchpro:Tuple):
        '''
        设置劳动工时,同时修改员工匹配属性的优先级
        :param dayWorkTime:
        :return:
        '''
        self.dayWorkTime += workTime
        self.weekWorkTime += workTime
        self.monthWorkTime += workTime

        for rule_info in emp_matchpro:
            cid = rule_info[0]
            did = rule_info[1]
            weight = int(rule_info[2])
            ruleGroup = rule_info[3]
            ruleCpType = rule_info[4]
            ruletag = rule_info[5]
            ruleCpNum = int(rule_info[6])

            if(self.cid == cid and ruleGroup == "worktime"):
                # 日工时
                if(ruletag == "dayWt" and ruleCpType == "lt"):
                    if(self.dayWorkTime < ruleCpNum):
                        self.weight = weight
                        break
                elif(ruletag == "dayWt" and ruleCpType == "le"):
                    if(self.dayWorkTime <= ruleCpNum):
                        self.weight = weight
                        break
                elif (ruletag == "dayWt" and ruleCpType == "eq"):
                    if (self.dayWorkTime == ruleCpNum):
                        self.weight = weight
                        break
                elif (ruletag == "dayWt" and ruleCpType == "ge"):
                    if (self.dayWorkTime >= ruleCpNum):
                        self.weight = weight
                        break
                elif (ruletag == "dayWt" and ruleCpType == "gt"):
                    if (self.dayWorkTime > ruleCpNum):
                        self.weight = weight
                        break
                # 周工时
                elif (ruletag == "weekWt" and ruleCpType == "lt"):
                    if (self.weekWorkTime < ruleCpNum):
                        self.weight = weight
                        break
                elif (ruletag == "weekWt" and ruleCpType == "le"):
                    if (self.weekWorkTime <= ruleCpNum):
                        self.weight = weight
                        break
                elif (ruletag == "weekWt" and ruleCpType == "eq"):
                    if (self.weekWorkTime == ruleCpNum):
                        self.weight = weight
                        break
                elif (ruletag == "weekWt" and ruleCpType == "ge"):
                    if (self.weekWorkTime >= ruleCpNum):
                        self.weight = weight
                        break
                elif (ruletag == "weekWt" and ruleCpType == "gt"):
                    if (self.weekWorkTime > ruleCpNum):
                        self.weight = weight
                        break
                # 月工时
                elif (ruletag == "monthWt" and ruleCpType == "lt"):
                    if (self.monthWorkTime < ruleCpNum):
                        self.weight = weight
                        break
                elif (ruletag == "monthWt" and ruleCpType == "le"):
                    if (self.monthWorkTime <= ruleCpNum):
                        self.weight = weight
                        break
                elif (ruletag == "monthWt" and ruleCpType == "eq"):
                    if (self.monthWorkTime == ruleCpNum):
                        self.weight = weight
                        break
                elif (ruletag == "monthWt" and ruleCpType == "ge"):
                    if (self.monthWorkTime >= ruleCpNum):
                        self.weight = weight
                        break
                elif (ruletag == "monthWt" and ruleCpType == "gt"):
                    if (self.monthWorkTime > ruleCpNum):
                        self.weight = weight
                        break

    def set_weight_for_hireType(self,emp_matchpro:Tuple):
        '''
        根据雇佣属性初始化匹配优先级
        :param emp_matchpro:
        :return:
        '''
        # cid,did,weight,ruleGroup,ruleCpType,ruletag,ruleCpNum
        # ('123456', '6', '12', 'otherrule', 'eq', 'hireAttr', '1')
        for rule_info in emp_matchpro:
            cid = rule_info[0]
            did = rule_info[1]
            weight = int(rule_info[2])
            ruleGroup = rule_info[3]
            ruleCpType = rule_info[4]
            ruletag = rule_info[5]
            ruleCpNum = int(rule_info[6])

            if(self.cid == cid and ruleGroup == "otherrule"):
                # 雇佣属性
                if(ruletag == "hireAttr" and ruleCpType == "eq"):
                    if ruleCpNum == '1':
                        self.weight = weight

    def set_did(self,did:str):
        self.did = did

    def set_caution(self,caution:str):
        self.caution = caution

    def set_not_work(self,no_work_list):
        # 计算连续休息时间
        self.restNumCon = self.search_max_len_dateStr(no_work_list)
        # 未排班天数
        self.noSchNum = len(no_work_list)
        # 休息天数
        self.restNum = len(no_work_list)

    def set_con_work(self):
        # 改变员工连续排班天数
        self.schDayNumCon = self.search_max_len_dateStr(self.work_date_list)
        # self.restNumCon = 0

    @staticmethod
    def search_max_len_dateStr(date_str_list):
        '''
        计算 员工连续排班天数
        :param date_str_list:
        :return:
        '''

        if not date_str_list: return 0
        if len(date_str_list) == 1: return 1

        len_ = 1
        max_len = 1
        for i in range(1, len(date_str_list)):
            if (DateTimeProcess.change_date_str(date_str_list[i - 1], 1) == date_str_list[i]):
                len_ = len_ + 1
            elif (len_ > max_len):
                max_len = len_
                len_ = 1

        return max_len if max_len > len_ else len_


    @staticmethod
    def get_emp_info_list(cid:str,legalityBids:List,emps:List,forecast_day: str,task_all_info:Dict,emp_matchpro:Tuple,employee_records:Dict,timeSize:int,emp_info_tuple) -> List:
        # 获取间接任务的技能
        indirectwh_skill_set = set()
        for task_dict in task_all_info.values():
            if (task_dict["taskType"] == "indirectwh"):
                task_skill = task_dict["taskSkillBids"].split(",")
                for skill in task_skill:
                    indirectwh_skill_set.add(skill)

        # 对员工进行处理
        emp_id_list = []

        # 提取匹配属性
        # {eid:{四种匹配属性}}
        emp_match = {}

        # 映射员工和bids
        emp_of_bids:Dict = {}

        # TODO:记录特殊事件段，不能安排任务
        emp_specialTime_dict = {}
        # {'123456-256': {'2017-07-13': ['01:00-02:00', '03:00-04:00'], '2017-07-12': ['01:00-02:00']}}
        for emp in emps:
            eid = str(emp["eid"])

            # 员工合规性bids,用于检索和校验员工合规性规则
            legalityBidArr = emp.get("legalityBidArr",[])
            # 添加 部门规则
            legalityBidArr.extend(legalityBids)

            isNew = emp.get('isNew',"")#['isNew']
            hireType = emp.get('hireType','') #['hireType']
            agreeOverTime = emp.get('agreeOverTime','')#['agreeOverTime']
            leadNew = emp.get('leadNew','')#['leadNew']

            emp_match[eid] = {"isNew": isNew, "hireType": hireType, "agreeOverTime": agreeOverTime, "leadNew": leadNew}

            emp_of_bids[eid] = legalityBidArr

            flag = ForecastTaskDB.prePcrocess_empAvailable(cid, eid, forecast_day)
            if not flag:  # 数据库操作失败
                return []

            emp_id_list.append(eid)
            emp_specialTime_dict[cid + "-" + str(eid)] = {}

            # 处理specialTime
            if ("specialTime" in emp):

                specialTime: List = emp["specialTime"]

                for item in specialTime:
                    special_date = item["startTime"].split(" ")[0]
                    startTime = item["startTime"].split(" ")[1]
                    special_end_date = item["endTime"].split(" ")[0]
                    endTime = item["endTime"].split(" ")[1]

                    # 非跨天
                    if(special_date == special_end_date):
                        if(special_date not in emp_specialTime_dict[str(cid) + "-" + str(eid)]):
                            emp_specialTime_dict[str(cid) + "-" + str(eid)][special_date] = [startTime+"-"+endTime]

                        elif(special_date in emp_specialTime_dict[str(cid) + "-" + str(eid)]):
                            emp_specialTime_dict[str(cid) + "-" + str(eid)][special_date].append(startTime + "-" + endTime)

                    # 跨天
                    if(special_date < special_end_date):
                        days:List = DateTimeProcess.date_interval(start_day=special_date,end_day=special_end_date)
                        if(len(days) == 2):

                            if (special_date not in emp_specialTime_dict[str(cid) + "-" + str(eid)]):
                                emp_specialTime_dict[str(cid) + "-" + str(eid)][special_date] = [startTime + "-" + "24:00"]

                            elif (special_date in emp_specialTime_dict[str(cid) + "-" + str(eid)]):
                                emp_specialTime_dict[str(cid) + "-" + str(eid)][special_date].append(startTime + "-" + "24:00")

                            if endTime != '00:00':
                                if (special_end_date not in emp_specialTime_dict[str(cid) + "-" + str(eid)]):
                                    emp_specialTime_dict[str(cid) + "-" + str(eid)][special_end_date] = ['00:00' + "-" + endTime]

                                elif (special_end_date in emp_specialTime_dict[str(cid) + "-" + str(eid)]):
                                    emp_specialTime_dict[str(cid) + "-" + str(eid)][special_end_date].append('00:00' + "-" + endTime)

                        elif(len(days) > 2):
                            start_day = days[0]
                            end_day = days[-1]
                            if (start_day not in emp_specialTime_dict[str(cid) + "-" + str(eid)]):
                                emp_specialTime_dict[str(cid) + "-" + str(eid)][start_day] = [startTime + "-" + "24:00"]

                            elif (start_day in emp_specialTime_dict[str(cid) + "-" + str(eid)]):
                                emp_specialTime_dict[str(cid) + "-" + str(eid)][start_day].append(startTime + "-" + "24:00")
                            if endTime != '00:00':
                                if (end_day not in emp_specialTime_dict[str(cid) + "-" + str(eid)]):
                                    emp_specialTime_dict[str(cid) + "-" + str(eid)][end_day] = ['00:00' + "-" + endTime]

                                elif (end_day in emp_specialTime_dict[str(cid) + "-" + str(eid)]):
                                    emp_specialTime_dict[str(cid) + "-" + str(eid)][end_day].append('00:00' + "-" + endTime)

                            for day in days[1:-1]:
                                if (day not in emp_specialTime_dict[str(cid) + "-" + str(eid)]):
                                    emp_specialTime_dict[str(cid) + "-" + str(eid)][day] = ['00:00' + "-" + '24:00']

                                elif (day in emp_specialTime_dict[str(cid) + "-" + str(eid)]):
                                    emp_specialTime_dict[str(cid) + "-" + str(eid)][day].append(
                                        '00:00' + "-" + '24:00')

        # TODO：员工信息处理并实例化
        # 获取该公司当天可用的全部员工
        #emp_info_tuple = ForecastTaskDB.read_emp_info(cid,forecast_day)

        # 存储员工实例
        emp_list = []

        # print(emp_match)

        # 指定员工中 可用员工列表
        # avail_emp_list = []
        for emp_info in emp_info_tuple:
            # cid, eid, type, start, end, day, skills, skillNums, certname, closingdate
            cid = emp_info[0]
            eid = emp_info[1]
            # 如果该员工
            if(eid not in emp_id_list):continue

            bids = emp_of_bids.get(eid,[])

            type = emp_info[2]
            starts = emp_info[3]
            ends = emp_info[4]
            # datetime.date 转换为 datetime.datetime
            day = datetime.datetime.strptime(str(emp_info[5]),'%Y-%m-%d')
            skills = emp_info[6] if emp_info[6] else ""
            skillNums = emp_info[7] if emp_info[7] else "0"
            certname = emp_info[8] if emp_info[8] else ""
            # datetime.date
            closingdate = datetime.datetime.strptime('1900-01-01','%Y-%m-%d')
            if emp_info[9] is not None:
                closingdate = datetime.datetime.strptime(str(emp_info[9]),'%Y-%m-%d')

            skills_list = skills.split(",")
            skillNums_list = skillNums.split(",")

            available_timeList = []
            if(type == "0"):
                available_timeList = [1] * (24 * 60 // timeSize)
                if(len(emp_specialTime_dict[cid+"-"+eid]) > 0 and forecast_day in emp_specialTime_dict[cid+"-"+eid]):
                    emp_specialTime_timeStr_List = emp_specialTime_dict[str(cid) + "-" + str(eid)][forecast_day]
                    specialTime_timeList = DateTimeProcess.timeStr_to_timeList(timeStrList=emp_specialTime_timeStr_List,timeSize=timeSize)

                    avail_timeList_matrix = np.array(available_timeList)
                    speci_timeList_matrix = np.array(specialTime_timeList)

                    available_timeList = (avail_timeList_matrix - speci_timeList_matrix).tolist()

            elif(type == '1'):
                available_timeList = [0] * (24 * 60 // timeSize)

            elif(type == "2"):
                starts = starts.split(",")
                ends = ends.split(",")
                timeStrList = []
                for i in range(len(starts)):
                    # 时间为 00：00：00 进行截取 化为 00：00
                    timeStrList.append(starts[i][:-3]+"-"+ends[i][:-3])

                available_timeList = DateTimeProcess.timeStr_to_timeList(timeStrList=timeStrList,timeSize=timeSize)
                if (len(emp_specialTime_dict[str(cid) + "-" + str(eid)]) > 0 and forecast_day in emp_specialTime_dict[
                    str(cid) + "-" + str(eid)]):
                    emp_specialTime_timeStr_List = emp_specialTime_dict[str(cid) + "-" + str(eid)][forecast_day]
                    specialTime_timeList = DateTimeProcess.timeStr_to_timeList(timeStrList=emp_specialTime_timeStr_List,
                                                                               timeSize=timeSize)

                    avail_timeList_matrix = np.array(available_timeList)
                    speci_timeList_matrix = np.array(specialTime_timeList)

                    result_matrix = avail_timeList_matrix - speci_timeList_matrix
                    # 两数相减 如果为负数置为0，避免 休息时间有重叠的情况
                    result_matrix[result_matrix < 0] = 0
                    available_timeList = result_matrix.tolist()

            for skill in list(indirectwh_skill_set):
                if skill in skills_list:
                    continue
                skills_list.append(skill)
                skillNums_list.append("100")

            # 获取个人匹配属性
            emp_match_for_eid = emp_match.get(eid, {"isNew": 'no', "hireType": 'full', "agreeOverTime": 'no',
                                                    "leadNew": 'no'})

            # 历史排班记录
            if((cid+"-"+eid) in employee_records):

                emp = Employee(cid=cid, eid=eid,work_date_list=employee_records[str(cid) + "-" + str(eid)]["work_date_list"],
                               skill=skills_list, skillNum=skillNums_list,
                               cret_closingdate={certname: closingdate},dayWorkTime=0,
                               weekWorkTime=employee_records[cid+"-"+eid]["weekWorkTime"],
                               monthWorkTime=employee_records[cid+"-"+eid]["monthWorkTime"],
                               available_timeList=available_timeList,
                               tasks=[],bids=bids,
                               dayShiftNum=0,
                               weekShiftNum=employee_records[cid+"-"+eid]["weekShiftNum"],
                               monthShiftNum=employee_records[cid+"-"+eid]["monthShiftNum"],
                               schDayNumCon_week=employee_records[cid+"-"+eid]["schDayNumCon"],
                               schDayNumCon_month=employee_records[cid + "-" + eid]["schDayNumCon_month"],
                               restNumCon=employee_records[cid+"-"+eid]["restNumCon"],
                               noSchNum=employee_records[cid+"-"+eid]["noSchNum"],
                               restNum=employee_records[cid+"-"+eid]["restNum"],
                               schNumSame=employee_records[cid+"-"+eid]['schNumSame'],
                               isNew=emp_match_for_eid['isNew'],
                               hireType=emp_match_for_eid['hireType'],
                               agreeOverTime=emp_match_for_eid['agreeOverTime'],
                               leadNew=emp_match_for_eid['leadNew'])

                # 根据雇佣属性初始化匹配优先级
                emp.set_weight_for_hireType(emp_matchpro=emp_matchpro)

                emp_list.append(emp)
                # avail_emp_list.append(emp.eid)

            # 首次排班
            else:
                emp = Employee(cid=cid,eid=eid,work_date_list=[],skill=skills_list,skillNum=skillNums_list,cret_closingdate={certname:closingdate},
                               dayWorkTime=0,weekWorkTime=0,monthWorkTime=0,available_timeList=available_timeList,tasks=[],bids=bids,
                               dayShiftNum=0,weekShiftNum=0,monthShiftNum=0,schDayNumCon_week=0,schDayNumCon_month=0,restNumCon=0,noSchNum=0,restNum=0,schNumSame={},
                               isNew=emp_match_for_eid['isNew'],hireType=emp_match_for_eid['hireType'],agreeOverTime=emp_match_for_eid['agreeOverTime'],
                               leadNew=emp_match_for_eid['leadNew'])

                # 根据雇佣属性初始化匹配优先级
                emp.set_weight_for_hireType(emp_matchpro=emp_matchpro)

                emp_list.append(emp)
                # avail_emp_list.append(emp.eid)

        return emp_list

    @staticmethod
    def testDate(specialTime,cid,eid):
        emp_specialTime_dict = {}
        emp_specialTime_dict[cid + "-" + str(eid)] = {}
        for item in specialTime:
            special_date = item["startTime"].split(" ")[0]
            startTime = item["startTime"].split(" ")[1]
            special_end_date = item["endTime"].split(" ")[0]
            endTime = item["endTime"].split(" ")[1]

            # 非跨天
            if (special_date == special_end_date):
                if (special_date not in emp_specialTime_dict[str(cid) + "-" + str(eid)]):
                    emp_specialTime_dict[str(cid) + "-" + str(eid)][special_date] = [startTime + "-" + endTime]

                elif (special_date in emp_specialTime_dict[str(cid) + "-" + str(eid)]):
                    emp_specialTime_dict[str(cid) + "-" + str(eid)][special_date].append(startTime + "-" + endTime)

            # 跨天
            if (special_date < special_end_date):
                days: List = DateTimeProcess.date_interval(start_day=special_date, end_day=special_end_date)
                if (len(days) == 2):

                    if (special_date not in emp_specialTime_dict[str(cid) + "-" + str(eid)]):
                        emp_specialTime_dict[str(cid) + "-" + str(eid)][special_date] = [startTime + "-" + "24:00"]

                    elif (special_date in emp_specialTime_dict[str(cid) + "-" + str(eid)]):
                        emp_specialTime_dict[str(cid) + "-" + str(eid)][special_date].append(startTime + "-" + "24:00")

                    if endTime != '00:00':
                        if (special_end_date not in emp_specialTime_dict[str(cid) + "-" + str(eid)]):
                            emp_specialTime_dict[str(cid) + "-" + str(eid)][special_end_date] = [
                                '00:00' + "-" + endTime]

                        elif (special_end_date in emp_specialTime_dict[str(cid) + "-" + str(eid)]):
                            emp_specialTime_dict[str(cid) + "-" + str(eid)][special_end_date].append(
                                '00:00' + "-" + endTime)

                elif (len(days) > 2):
                    start_day = days[0]
                    end_day = days[-1]
                    if (start_day not in emp_specialTime_dict[str(cid) + "-" + str(eid)]):
                        emp_specialTime_dict[str(cid) + "-" + str(eid)][start_day] = [startTime + "-" + "24:00"]

                    elif (start_day in emp_specialTime_dict[str(cid) + "-" + str(eid)]):
                        emp_specialTime_dict[str(cid) + "-" + str(eid)][start_day].append(startTime + "-" + "24:00")
                    if endTime != '00:00':
                        if (end_day not in emp_specialTime_dict[str(cid) + "-" + str(eid)]):
                            emp_specialTime_dict[str(cid) + "-" + str(eid)][end_day] = ['00:00' + "-" + endTime]

                        elif (end_day in emp_specialTime_dict[str(cid) + "-" + str(eid)]):
                            emp_specialTime_dict[str(cid) + "-" + str(eid)][end_day].append('00:00' + "-" + endTime)

                    for day in days[1:-1]:
                        if (day not in emp_specialTime_dict[str(cid) + "-" + str(eid)]):
                            emp_specialTime_dict[str(cid) + "-" + str(eid)][day] = ['00:00' + "-" + '24:00']

                        elif (day in emp_specialTime_dict[str(cid) + "-" + str(eid)]):
                            emp_specialTime_dict[str(cid) + "-" + str(eid)][day].append(
                                '00:00' + "-" + '24:00')
        return emp_specialTime_dict

if __name__ == '__main__':
    specialTime = [{'startTime':'2019-07-19 00:00','endTime':'2019-07-20 01:00'}]
    cid ,eid = '123456','11'
    emp_specialTime_dict = Employee.testDate(specialTime, cid, eid)
    print(emp_specialTime_dict)

    # date_str = Employee.search_max_len_dateStr(
    #     ['2020-05-13', '2020-05-14', '2020-05-15', '2020-05-16', '2020-05-18', '2020-05-19', '2020-05-29', '2020-05-30',
    #      '2020-05-31'])
    #
    # print(date_str)
