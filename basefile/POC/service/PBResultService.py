"""
by lyy
阶段四接口6-获取排班结果
2019-11-25
"""
"""
方法一：严格按第三阶段排出来的任务矩阵，最后将1小时及以下的独立的非固定任务舍弃。
"""
from datetime import datetime,timedelta
from typing import List, Dict, Any, Union, Tuple
import itertools
from  utils.HistoryShiftUtils import HistoryShiftUtils
from dateutil.relativedelta import *
#from utils.dateUtils import DateUtils
#from config.db import conf
from POC.model.PBResult_db import PBResultDB
from functools import cmp_to_key
from collections import Counter
import copy

class PBResultService:
    """
     版本：最新 2019-10-28
     作者：lyy
     """

    @staticmethod
    def PaiBanResult(raw_data):
        #save_result = {'code': 0, 'result': '未处理'}
        #matrix:阶段3生成的任务矩阵;raw_data：阶段四接口6传入的json字典，拿出员工的可用时段，排班时使用
        import json
        applyId = raw_data['applyId']
        cid = raw_data['cid']
        didArr = raw_data['didArr']
        start = raw_data['start'] #排班开始日期
        end = raw_data['end'] #排班结束日期
        schType = raw_data['schType']#排班类型，目前只有任务类型，后期可能会有其他的
        emps = raw_data['emps']
        timeInterval = float(raw_data['timeInterval']) #时间间隔，分钟
        all_tnum = int((60/timeInterval)*24) #一天总共被分为多少格
        scheme = raw_data['scheme'] #排班方案（worktime(工时最少), emp（人员最少）, effect（时效最优）, violation（违反规则较少）， fillRate(满足率)）

        def numtostr(num):
            # 将数字转换成时间字符串
            # 输入是数字5.5 --> 字符串05:30
            # 若字符串长度不足2时，自动将字符串前补0，使长度为2
            h = str(num).split('.')[0].zfill(2)
            m = float('0.' + str(num).split('.')[1])
            if m == 0:
                res = h + ':00'
            else:
                res = h + ':' + str(int(m * 60))
            return res

        def strtonum(time):
            # 将字符串时间转化为数字
            # 输入字符串格式是：08：30，返回数字8.5
            h = int(time.split(':')[0])
            m = float(time.split(':')[1]) / 60
            res = h + m
            return res

        #获取所有要排的日期列表
        def get_PBdate(start, end):
            import datetime
            date_li = [start]  # 返回所有要排的日期列表
            start = datetime.datetime.strptime(start, '%Y-%m-%d').date()
            end = datetime.datetime.strptime(end, '%Y-%m-%d').date()
            xc_days = (end - start).days  # 两个日期相差的天数
            i = 0
            d1 = start
            while i < xc_days:
                i += 1
                d1 += datetime.timedelta(days=1)  # 加一天
                date_li.append(str(d1))
            return date_li

        # 先把员工的不可用时间整理成列表:
        # {eid1:{开始-结束日期1：[开始时间，结束时间],
        #       开始-结束日期2：[开始时间，结束时间]},
        #  eid2:{开始-结束日期1：[开始时间，结束时间],
        #       开始-结束日期2：[开始时间，结束时间]}
        # }
        #返回所有员工的不可用时段（special time）字典
        def emp_notime(emps):
            emps_notime = {} #员工的不可用时段，不一定是全部待排员工，因为有可能员工没有不可用时段，都是可用的
            emps_li = [] #所有待排员工eid
            for emp in emps: #emp:dict，一个emp代表一个员工 的不可用时段
                emp_notime = {}#某个员工的不可用时段
                eid = emp['eid']
                emps_li.append(eid)
                if len(emp['specialTime']) != 0:
                    for st in emp['specialTime']: #st: dict,一个st就是一个不可用时段
                        startDate = st['startTime'].split(' ')[0]#2019-07-12
                        startTime = st['startTime'].split(' ')[1]#14:00
                        endDate = st['endTime'].split(' ')[0]#2019-07-12
                        endTime = st['endTime'].split(' ')[1]#16:00
                        emp_notime[startDate+'*'+endDate]=[startTime,endTime]
                    emps_notime[eid] = emp_notime
            print('emps_notime=',emps_notime)
            return emps_notime,emps_li

        #获取班次模板数据（开始时间，结束时间，是否跨天）
        def get_shiftMod(cid,did,shiftid):
            res, flag = PBResultDB.select_shiftMod(cid,did,shiftid)
            #if flag:#数据库操作成功
            return res,flag

        #员工可用性判断
        def emp_time(eid,cid,date,task_starttime,task_endtime):
            # {eid:[type,(s,e),(s,e)]}
            res = PBResultDB.select_empAvailableTime(cid,date)
            #print('res=',res)
            if eid in res:
                if res[eid][0] == '1':
                    res_flag = 1 #不可排
                elif res[eid][0] == '0':
                    res_flag = 0  # 可排
                else:#2  部分可排
                    #print('******8')
                    res_flag = 1 #默认不可排
                    for time in res[eid][1:]:
                        s = strtonum(str(time[0]))
                        e = strtonum(str(time[1]))
                        if (task_starttime >= s) and (task_endtime <= e):
                            res_flag = 0
                            break
            else:
                res_flag = 1

            return res_flag

        #判断员工某天是否可用
        def emp_type(cid,date):
            # {eid:[type,(s,e),(s,e)]}
            res = PBResultDB.select_empAvailableTime(cid,date)
            #print('eid,res=', eid,res)
            return res

        #返回所有要排的员工属性字典，{eid:{各种属性}},和所有要排的员工eid列表
        def emps_attr(emps,cid):
            emp_matchpro = {}
            #emps_eid = []
            for emp in emps:
                eid = emp['eid']
                # 属性字典,day_wt 日排班工时(分钟)，  nopb_days 未排班天数，  rest_days 休息天数，day_shiftNum 日班次个数
                # now_shiftlen 正在排的班次的长度即工时数，等排下一个班次时重新置0，用来计算班次长度这个规则
                #lasttask_endtime 上个任务的结束时间 用来计算班次间隔
                #interval 班次间隔
                attributes = {'now_shiftlen':0,'lasttask_endtime':0,'interval':100,'taskid_set':set()}
                emp_skilldata, flag = PBResultDB.select_empSkills(eid, cid)#{技能ID：技能值,技能ID：技能值,...}
                attributes['skill'] = emp_skilldata  # 属性字典中增加技能属性
                emp_certdata, flag = PBResultDB.select_empCerts(eid, cid)# {证书名称：到期日期,证书名称：到期日期,...}
                attributes['certs'] = emp_certdata  # 属性字典中增加证书属性
                emp_matchpro[eid] = attributes
                #emps_eid.append(eid)
            print('emp_matchpro=',emp_matchpro)
            return emp_matchpro

        #获取当天的任务排班矩阵和可组合列表【【任务1，任务2】，【任务1，任务4】】
        def receive_matrix(cid,did,date,mode):
            result,flag = PBResultDB.select_record(cid, did,date,mode)
            return result,flag

        #根据任务ID，找出该任务对应的技能ID列表
        def get_skillID(taskID,cid, did):
            skillID,flag = PBResultDB.select_skillID(taskID,cid, did)
            return skillID,flag

        # 根据任务ID，找出该任务对应的证书列表（有可能对应多个证书）
        def get_certsname(taskID,cid, did):
            certsname,flag = PBResultDB.select_certsname(taskID,cid, did)
            return certsname,flag

        #根据技能ID找到对应员工,返回【员工ID,eid,...】
        def get_empID(skillID,cid):
            empid, flag = PBResultDB.select_empID(skillID,cid)
            #emp_skill = sorted(emp_skill.items(),key=lambda x:x[1],reverse=True)#根据技能值倒序排序
            return empid,flag

        # 获取拥有要求证书的员工id列表
        def get_empID_c(certsname, cid):
            empid, flag = PBResultDB.select_empID_certs(certsname, cid)
            return empid, flag
        #工时匹配属性数值比较结果
        def bjres(ruledata,num):
            bbj_num = float(ruledata[0][2])
            if ruledata[0][1] == 'lt':  # <
                if num < bbj_num:
                    fuhe_flag = 0  # 0 符合  1 不符合
                else:
                    fuhe_flag = 1
            elif ruledata[0][1] == 'le':  # <=
                if num <= bbj_num:
                    fuhe_flag = 0  # 0 符合  1 不符合
                else:
                    fuhe_flag = 1
            elif ruledata[0][1] == 'eq':  # =
                if num == bbj_num:
                    fuhe_flag = 0  # 0 符合  1 不符合
                else:
                    fuhe_flag = 1
            elif ruledata[0][1] == 'ge':  # >=
                if num >= bbj_num:
                    fuhe_flag = 0  # 0 符合  1 不符合
                else:
                    fuhe_flag = 1
            elif ruledata[0][1] == 'gt':  # >
                if num > bbj_num:
                    fuhe_flag = 0  # 0 符合  1 不符合
                else:
                    fuhe_flag = 1
            return fuhe_flag

        #比较类型,看是否符合匹配规则（部分）
        def is_fuhe(ruledata,emp_matchpro,eid,ruletag,skillid,certsname,task_starttime):
            if ruletag == 'skill':
                gz_num = float(ruledata[0][2])
                num = float(emp_matchpro[eid][ruletag][skillid])
                if ruledata[0][1] == 'lt':  # <
                    if  num < gz_num:
                        fuhe_flag = 0  # 0 符合  1 不符合
                    else:
                        fuhe_flag = 1
                elif ruledata[0][1] == 'le':  # <=
                    if num <= gz_num:
                        fuhe_flag = 0  # 0 符合  1 不符合
                    else:
                        fuhe_flag = 1
                elif ruledata[0][1] == 'eq':  # =
                    if num == gz_num:
                        fuhe_flag = 0  # 0 符合  1 不符合
                    else:
                        fuhe_flag = 1
                elif ruledata[0][1] == 'ge':  # >=
                    if num >= gz_num:
                        fuhe_flag = 0  # 0 符合  1 不符合
                    else:
                        fuhe_flag = 1
                elif ruledata[0][1] == 'gt':  # >
                    if num > gz_num:
                        fuhe_flag = 0  # 0 符合  1 不符合
                    else:
                        fuhe_flag = 1
            elif ruletag == 'certs':
                if ruledata[0][1] == 'eq' and ruledata[0][2]=='1':  # 要求具备证书
                    if certsname in emp_matchpro[eid][ruletag]:
                        fuhe_flag = 0  # 0 符合  1 不符合
                    else:
                        fuhe_flag = 1
                elif ruledata[0][1] == 'eq' and ruledata[0][2]=='0':  # bu要求具备证书
                    fuhe_flag = 0 #不要求具备证书时，有没有该证书都是符合的
            elif ruletag == 'shiftInterval':#
                timejg = task_starttime - emp_matchpro[eid]['lasttask_endtime']  # 间隔=当前任务的开始时间-上个任务的结束时间
                gz_num = float(ruledata[0][2])
                if ruledata[0][1] == 'lt':  # <
                    if timejg < gz_num:
                        fuhe_flag = 0  # 0 符合  1 不符合
                    else:
                        fuhe_flag = 1
                elif ruledata[0][1] == 'le':  # <=
                    if timejg <= gz_num:
                        fuhe_flag = 0  # 0 符合  1 不符合
                    else:
                        fuhe_flag = 1
                elif ruledata[0][1] == 'eq':  # =
                    if timejg == gz_num:
                        fuhe_flag = 0  # 0 符合  1 不符合
                    else:
                        fuhe_flag = 1
                elif ruledata[0][1] == 'ge':  # >=
                    if timejg >= gz_num:
                        fuhe_flag = 0  # 0 符合  1 不符合
                    else:
                        fuhe_flag = 1
                elif ruledata[0][1] == 'gt':  # >
                    if timejg > gz_num:
                        fuhe_flag = 0  # 0 符合  1 不符合
                    else:
                        fuhe_flag = 1

            return fuhe_flag # 0 符合  1 不符合

        def fuhe(ruledata,eid,rulename,j,rule):
            #emp_pbwt = {}  # 排班周期内，每天的工时情况
            #emp_pbsn = {}  # 排班周期内，每天的班次个数情况
            if rulename == 'dayWt':
                wh = rule[eid][j]#该员工当天的工时情况
                fuhe_flag = bjres(ruledata,wh)
            elif rulename == 'weekWt':
                pass
            elif rulename == 'shiftNum':
                num = rule[eid][j]
                fuhe_flag = bjres(ruledata, num)
            return fuhe_flag

        #员工匹配属性规则检查，{eid:[0,0,1,1,0],...}
        def emp_matchPro(cid,did,eid_li,emp_matchpro,skillid,certsname,task_starttime,j,emp_pbwt,emp_pbsn):
            emps_match = {} #所有员工的匹配检查结果字典，{eid:[0,0,1,1,0],...}
            for eid in eid_li:
                match = []  # 匹配规则检查结果列表，[0,0,1,1,0],0符合  1不符合
                weight = 1 #默认优先级从1开始,1表示优先级最高
                while weight < 15:
                    #ruledata [(规则名称，比较类型，比较数值)]
                    ruledata, flag = PBResultDB.select_rule(did, cid, weight)
                    if len(ruledata[0]) != 0:#这个优先级有规则
                        if ruledata[0][0] == 'dayWt':#日排班工时（分钟)
                            rulename = 'dayWt'
                            rule = emp_pbwt
                            #fuhe_flag = is_fuhe(ruledata,emp_matchpro,eid,ruletag,skillid,certsname,task_starttime)
                            fuhe_flag = fuhe(ruledata, eid, rulename, j,rule)
                            match.append(fuhe_flag)
                        elif ruledata[0][0] == 'weekWt':
                            ruletag = 'weekWt'
                            #fuhe_flag = is_fuhe(ruledata,emp_matchpro,eid,ruletag,skillid,certsname,task_starttime)
                            #fuhe_flag = fuhe(ruledata, eid, rulename, j, emp_pbwt)
                            #match.append(fuhe_flag)
                        elif ruledata[0][0] == 'monthWt':
                            ruletag = 'monthWt'
                            #fuhe_flag = is_fuhe(ruledata,emp_matchpro,eid,ruletag,skillid,certsname,task_starttime)
                            #match.append(fuhe_flag)
                        elif ruledata[0][0] == 'shiftNum':#每日班次个数
                            rulename = 'shiftNum'
                            rule = emp_pbsn
                            #fuhe_flag = is_fuhe(ruledata,emp_matchpro,eid,ruletag,skillid,certsname,task_starttime)
                            fuhe_flag = fuhe(ruledata, eid, rulename, j, rule)
                            match.append(fuhe_flag)
                        elif ruledata[0][0] == 'taskSkilled':#任务技能熟练度
                            ruletag = 'skill'
                            fuhe_flag = is_fuhe(ruledata,emp_matchpro,eid,ruletag,skillid,certsname,task_starttime)
                            match.append(fuhe_flag)
                        # elif ruledata[0][0] == 'positioncert':#具备岗位要求证书（0：无,1：有）
                        #     ruletag = 'certs'
                        #     fuhe_flag = is_fuhe(ruledata,emp_matchpro,eid,ruletag,skillid,certsname,task_starttime)
                        #     match.append(fuhe_flag)
                        elif ruledata[0][0] == 'shiftInterval':#班次之间间隔，属性字典里上个任务的结束时间
                            ruletag = 'shiftInterval'

                            fuhe_flag = is_fuhe(ruledata,emp_matchpro,eid,ruletag,skillid,certsname,task_starttime)
                            match.append(fuhe_flag)
                    else:
                        break

                    weight += 1
                emps_match[eid] = match
            return emps_match

        # 自定义方法，字典按value比较优先级
        def dict_compare(one_emp, two_emp):
            length = len(one_emp[1])
            i = 0
            while i < length:
                if one_emp[1][i] != two_emp[1][i]:
                    return one_emp[1][i] - two_emp[1][i]
                    # return two_emp[1][i] - one_emp[1][i]
                else:
                    i += 1
            return 0

        # 排出员工的优先级，返回员工的优先级列表.emp_order:[('e', [0, 0, 0, 0]), ('a', [0, 0, 1, 0]), ('d', [1, 1, 1, 0])]
        def emp_priority(emp_order):
            emps_order = [] #员工优先级顺序表，正序，优先级最低的在最前面
            for item in emp_order:
                emps_order.append(item[0])
            return emps_order #['e','a','d']

        #判断该员工在这个任务段内可不可用
        def emp_special(eid,date,task_starttime,task_endtime,emps_notime):
            if eid not in emps_notime:
                flag = 0
            else:
                times = emps_notime[eid]  # {开始*结束:[t1,t2],...}
                for k,v in times.items():
                    if (k.split('*')[0] == date) and (k.split('*')[1] == date):#员工不可用开始结束日期等于给定日期
                        s,e = strtonum(v[0]) ,strtonum(v[1]) #不可用开始、结束时间转换成数字，便于和任务时间比较
                        if task_starttime >= e:#任务开始时间在结束时间之后，这个人可以排
                            flag = 0
                        elif task_endtime <= s:#任务结束时间在开始时间之前，这个人可以排
                            flag = 0
                        else:#其余均不可排
                            flag = 1
                    elif (k.split('*')[0] == date) and (k.split('*')[1] != date):
                        # 员工不可用开始日期等于给定日期,结束日期大于给定
                        s, e = strtonum(v[0]), strtonum(v[1])  # 不可用开始、结束时间转换成数字，便于和任务时间比较
                        if task_endtime <= s:#任务结束时间在不可用开始之前，可排
                            flag = 0
                        else:#其余均不可排
                            flag = 1
                    elif (k.split('*')[1] == date) and (k.split('*')[0] != date):
                        # 员工不可用结束日期等于给定日期,开始日期小于给定
                        s, e = strtonum(v[0]), strtonum(v[1])
                        if task_starttime >= e:#任务开始时间在不可用结束之后，可排
                            flag = 0
                        else:
                            flag = 1

            return flag #0 可排，1  不可排

        # 时数、天数、部分班次规则判断是否符合
        # def emp_daysrule(lx, num, caution, score, nums):
        #     num = float(num)  # 规则数值,被比较数值
        #     flag = 0
        #     if lx == 'lt':  # 比较类型 <
        #         if caution == 'forbid':
        #             if nums >= num:
        #                 flag = 0  # 符合硬性规则
        #             else:
        #                 flag = 1  # 不符合硬性规则，直接返回
        #                 return flag, score
        #         else:
        #             if nums >= num:
        #                 score = score  # 符合软性规则，分数不变
        #             else:
        #                 score -= 1  # 不符合软性规则，扣一分
        #     elif lx == 'le':  # 比较类型 <=
        #         if caution == 'forbid':
        #             if nums > num:
        #                 flag = 0  # 符合硬性规则
        #             else:
        #                 flag = 1  # 不符合硬性规则，直接返回
        #                 return flag, score
        #         else:
        #             if nums > num:
        #                 score = score  # 符合软性规则，分数不变
        #             else:
        #                 score -= 1  # 不符合软性规则，扣一分
        #     elif lx == 'eq':  # 比较类型 ==
        #         if caution == 'forbid':
        #             if nums != num:
        #                 flag = 0  # 符合硬性规则
        #             else:
        #                 flag = 1  # 不符合硬性规则，直接返回
        #                 return flag, score
        #         else:
        #             if nums != num:
        #                 score = score  # 符合软性规则，分数不变
        #             else:
        #                 score -= 1  # 不符合软性规则，扣一分
        #     elif lx == 'ge':  # 比较类型 >=
        #         if caution == 'forbid':
        #             if nums < (num - 1):
        #                 flag = 0  # 符合硬性规则
        #             else:
        #                 flag = 1  # 不符合硬性规则，直接返回
        #                 return flag, score
        #         else:
        #             if nums < num:
        #                 score = score  # 符合软性规则，分数不变
        #             else:
        #                 score -= 1  # 不符合软性规则，扣一分
        #     elif lx == 'gt':  # 比较类型 >
        #         if caution == 'forbid':
        #             if nums <= num:
        #                 flag = 0  # 符合硬性规则
        #             else:
        #                 flag = 1  # 不符合硬性规则，直接返回
        #                 return flag, score
        #         else:
        #             if nums <= num:
        #                 score = score  # 符合软性规则，分数不变
        #             else:
        #                 score -= 1  # 不符合软性规则，扣一分
        #
        #     return flag, score

        def emp_daysrule(lx, num, caution, nums):
            num = float(num)  # 规则数值,被比较数值
            flag = 0 #默认没有违反硬性规则
            soft_flag = 0 #默认没有违反软规则
            if lx == 'lt':  # 比较类型 <
                if caution == 'forbid':
                    if nums >= num:
                        flag = 0  # 符合硬性规则
                    else:
                        flag = 1  # 不符合硬性规则，直接返回
                        return flag, soft_flag
                else:
                    if nums >= num:
                        soft_flag = 0  # 符合软性规则
                    else:
                        #score -= 1  # 不符合软性规则，扣一分
                        soft_flag = 1
            elif lx == 'le':  # 比较类型 <=
                if caution == 'forbid':
                    if nums > num:
                        flag = 0  # 符合硬性规则
                    else:
                        flag = 1  # 不符合硬性规则，直接返回
                        return flag, soft_flag
                else:
                    if nums > num:
                        #score = score  # 符合软性规则，分数不变
                        soft_flag = 0
                    else:
                        #score -= 1  # 不符合软性规则，扣一分
                        soft_flag = 1
            elif lx == 'eq':  # 比较类型 ==
                if caution == 'forbid':
                    if nums != num:
                        flag = 0  # 符合硬性规则
                    else:
                        flag = 1  # 不符合硬性规则，直接返回
                        return flag, soft_flag
                else:
                    if nums != num:
                        #score = score  # 符合软性规则，分数不变
                        soft_flag = 0
                    else:
                        #score -= 1  # 不符合软性规则，扣一分
                        soft_flag = 1
            elif lx == 'ge':  # 比较类型 >=
                if caution == 'forbid':
                    if nums < (num - 1):
                        flag = 0  # 符合硬性规则
                    else:
                        flag = 1  # 不符合硬性规则，直接返回
                        return flag, soft_flag
                else:
                    if nums < num:
                        #score = score  # 符合软性规则，分数不变
                        soft_flag = 0
                    else:
                        #score -= 1  # 不符合软性规则，扣一分
                        soft_flag = 1
            elif lx == 'gt':  # 比较类型 >
                if caution == 'forbid':
                    if nums <= num:
                        flag = 0  # 符合硬性规则
                    else:
                        flag = 1  # 不符合硬性规则，直接返回
                        return flag, soft_flag
                else:
                    if nums <= num:
                        #score = score  # 符合软性规则，分数不变
                        soft_flag = 0
                    else:
                        #score -= 1  # 不符合软性规则，扣一分
                        soft_flag = 1

            return flag, soft_flag

        #部分不同类型规则取数校验
        # def check_ruleType(dataType,ruletag,k,caution,flag,score,beg_ind,end_ind,eid,date,emp_pblist,emp_pbwt,emp_pbsn,emp_matchpro,emp_shiftlen,emp_interval):
        #     #continue_flag = 0 #默认有以下规则
        #     if ruletag == 'schDayNumCon':  # 连续排班天数
        #         if dataType == 0:  # 非历史排班校验
        #             num_li = [len(list(v)) for k, v in itertools.groupby(emp_pblist[eid][beg_ind:(end_ind + 1)]) if k == 1]
        #             if len(num_li) == 0:
        #                 nums = 0
        #             else:
        #                 nums = max(num_li)
        #             flag, score = emp_daysrule(k[1], k[2], caution, score, nums)
        #     elif ruletag == 'restNumCon':  # 连续休息天数
        #         if dataType == 0:  # 非历史排班校验
        #             num_li = [len(list(v)) for k, v in itertools.groupby(emp_pblist[eid][beg_ind:(end_ind + 1)]) if k == 2]
        #             if len(num_li) == 0:#若没有休息，即没有元素2
        #                 nums = 0
        #             else:
        #                 nums = max(num_li)
        #             flag, score = emp_daysrule(k[1], k[2], caution, score, nums)
        #     elif ruletag == 'noSchNum':  # 未排班天数
        #         if dataType == 0:  # 非历史排班校验
        #             nums = emp_pblist[eid][beg_ind:(end_ind+1)].count(0)
        #             flag, score = emp_daysrule(k[1], k[2], caution, score, nums)
        #     elif ruletag == 'restNum':  # 休息天数
        #         if dataType == 0:  # 非历史排班校验
        #             nums = emp_pblist[eid][beg_ind:(end_ind+1)].count(2)
        #             flag, score = emp_daysrule(k[1], k[2], caution, score, nums)
        #     elif ruletag == 'shiftTime':  # 总工时，type字段没有用
        #         if dataType == 0:  # 非历史排班校验
        #             nums = sum(emp_pbwt[eid][beg_ind:(end_ind + 1)])
        #             flag, score = emp_daysrule(k[1], k[2], caution, score, nums)
        #     elif ruletag == 'schShiftNum':  # 已排班次个数，type字段没有用
        #         if dataType == 0:  # 非历史排班校验
        #             nums = sum(emp_pbsn[eid][beg_ind:(end_ind + 1)])
        #             flag, score = emp_daysrule(k[1], k[2], caution, score, nums)
        #     elif ruletag == 'shiftLen':  # 班次长度
        #         if dataType == 0:#非历史排班校验
        #             nums = emp_matchpro[eid]['now_shiftlen']
        #             flag, score = emp_daysrule(k[1], k[2], caution, score, nums)
        #         else:#历史排班校验
        #             for nums in emp_shiftlen[eid]:
        #                 flag, score = emp_daysrule(k[1], k[2], caution, score, nums)
        #                 if flag == 1:
        #                     break
        #     elif ruletag == 'interval':  # 班次间隔
        #         if dataType == 0:  # 非历史排班校验
        #             nums = emp_matchpro[eid]['interval']
        #             flag, score = emp_daysrule(k[1], k[2], caution, score, nums)
        #         else:
        #             for nums in emp_interval[eid]:
        #                 flag, score = emp_daysrule(k[1], k[2], caution, score, nums)
        #                 if flag == 1:
        #                     break
        #     elif ruletag == 'certExpireDays':  # k[4] 证书名称
        #         if dataType == 0:  # 非历史排班校验
        #             close_date = emp_matchpro[eid]['certs'][k[4]]  # 该证书的到期日期
        #             close_date = datetime.strptime(close_date, '%Y-%m-%d').date()
        #             nums = (close_date - date).days
        #             flag, score = emp_daysrule(k[1], k[2], caution, score, nums)
        #     # else:
        #     #     continue_flag = 1 # 未找到以上的规则，继续下一轮循环
        #     return flag, score

        def check_ruleType(dataType,ruletag,k,caution,flag,score,beg_ind,end_ind,eid,date,emp_pblist,emp_pbwt,emp_pbsn,emp_matchpro,emp_shiftlen,emp_interval):
            #continue_flag = 0 #默认有以下规则
            if ruletag == 'schDayNumCon':  # 连续排班天数
                if dataType == 0:  # 非历史排班校验
                    num_li = [len(list(v)) for k, v in itertools.groupby(emp_pblist[eid][beg_ind:(end_ind + 1)]) if k == 1]
                    if len(num_li) == 0:
                        nums = 0
                    else:
                        nums = max(num_li)
                    flag, soft_flag = emp_daysrule(k[1], k[2], caution, nums)
                    if (soft_flag == 1) and (ruletag not in score):
                        score[ruletag] = 1
            elif ruletag == 'restNumCon':  # 连续休息天数
                if dataType == 0:  # 非历史排班校验
                    num_li = [len(list(v)) for k, v in itertools.groupby(emp_pblist[eid][beg_ind:(end_ind + 1)]) if k == 2]
                    if len(num_li) == 0:#若没有休息，即没有元素2
                        nums = 0
                    else:
                        nums = max(num_li)
                    flag, soft_flag = emp_daysrule(k[1], k[2], caution, nums)
                    if (soft_flag == 1) and (ruletag not in score):
                        score[ruletag] = 1
            elif ruletag == 'noSchNum':  # 未排班天数
                if dataType == 0:  # 非历史排班校验
                    nums = emp_pblist[eid][beg_ind:(end_ind+1)].count(0)
                    flag, soft_flag = emp_daysrule(k[1], k[2], caution, nums)
                    if (soft_flag == 1) and (ruletag not in score):
                        score[ruletag] = 1
            elif ruletag == 'restNum':  # 休息天数
                if dataType == 0:  # 非历史排班校验
                    nums = emp_pblist[eid][beg_ind:(end_ind+1)].count(2)
                    flag, soft_flag = emp_daysrule(k[1], k[2], caution, nums)
                    if (soft_flag == 1) and (ruletag not in score):
                        score[ruletag] = 1
            elif ruletag == 'shiftTime':  # 总工时，type字段没有用
                if dataType == 0:  # 非历史排班校验
                    nums = sum(emp_pbwt[eid][beg_ind:(end_ind + 1)])
                    flag, soft_flag = emp_daysrule(k[1], k[2], caution, nums)
                    if (soft_flag == 1) and (ruletag not in score):
                        score[ruletag] = 1
            elif ruletag == 'schShiftNum':  # 已排班次个数，type字段没有用
                if dataType == 0:  # 非历史排班校验
                    nums = sum(emp_pbsn[eid][beg_ind:(end_ind + 1)])
                    flag, soft_flag = emp_daysrule(k[1], k[2], caution, nums)
                    if (soft_flag == 1) and (ruletag not in score):
                        score[ruletag] = 1
            elif ruletag == 'shiftLen':  # 班次长度
                if dataType == 0:#非历史排班校验
                    nums = emp_matchpro[eid]['now_shiftlen']
                    flag, soft_flag = emp_daysrule(k[1], k[2], caution, nums)
                    if (soft_flag == 1) and (ruletag not in score):
                        score[ruletag] = 1
                else:#历史排班校验
                    for nums in emp_shiftlen[eid]:
                        flag, soft_flag = emp_daysrule(k[1], k[2], caution, nums)
                        if flag == 1:
                            break
                        if (soft_flag == 1) and (ruletag not in score):
                            score[ruletag] = 1
            elif ruletag == 'interval':  # 班次间隔
                if dataType == 0:  # 非历史排班校验
                    nums = emp_matchpro[eid]['interval']
                    flag, soft_flag = emp_daysrule(k[1], k[2], caution, nums)
                    if (soft_flag == 1) and (ruletag not in score):
                        score[ruletag] = 1
                else:
                    for nums in emp_interval[eid]:
                        flag, soft_flag = emp_daysrule(k[1], k[2], caution, nums)
                        if flag == 1:
                            break
                        if (soft_flag == 1) and (ruletag not in score):
                            score[ruletag] = 1
            elif ruletag == 'certExpireDays':  # k[4] 证书名称
                if dataType == 0:  # 非历史排班校验
                    close_date = emp_matchpro[eid]['certs'][k[4]]  # 该证书的到期日期
                    close_date = datetime.strptime(close_date, '%Y-%m-%d').date()
                    nums = (close_date - date).days
                    flag, soft_flag = emp_daysrule(k[1], k[2], caution, nums)
                    if (soft_flag == 1) and (ruletag not in score):
                        score[ruletag] = 1
            # else:
            #     continue_flag = 1 # 未找到以上的规则，继续下一轮循环
            return flag, score

        # 历史排班数据处理 history_data->dic {eid:{day1:[(任务ID,s,e,工时),(s,e),..], day2:[(),()]}}
        # rule_start 规则开始日期  rule_end 规则结束日期 pb_start 排班开始日期
        def handle_HistoryData(rule_start, pb_start, cid, eid):
            emp_pblist = {}  # 每天是否排班、休息情况{eid:[],eid:[],,,,} 0 可用但未排班 2 当天休息不可用，1 当天排班
            emp_pbwt = {}  # 每天的工时情况
            emp_pbsn = {}  # 每天的班次个数情况
            emp_shiftlen = {}  # 所有的班次长度
            emp_interval = {}  # 所有的班次间隔（分钟）
            emp_no_time = {}  # 员工不可用时间段列表(指定班次和相同排班校验产生的)
            days = (pb_start - rule_start).days  # 排班开始和规则开始之间的天数差，12号到14号，差2天，只统计12、13的历史数据，因为14号已经是这次排班的开始日期了
            history_day = get_PBdate(str(rule_start), str(pb_start))[:-1]  # 最后一个日期(排班开始日期)不要,我所要的历史日期数据
            pa = {eid: history_day}
            history_data = HistoryShiftUtils.getHistory(pa)  # 调用获取历史数据方法

            emp_pbwt[eid] = [0 for i in range(days)]
            emp_pblist[eid] = [0 for i in range(days)]
            emp_pbsn[eid] = [0 for i in range(days)]
            emp_shiftlen[eid] = []
            emp_interval[eid] = []

            for i in range(len(history_day)):
                date = history_day[i]
                res = emp_type(cid, date)
                if eid in res:
                    if res[eid][0] == 1:  # 不可用
                        emp_pblist[eid][i] = 2  # 该员工当天排班矩阵状态为休息（不可用）

                if len(history_data[eid][date]) != 0:  # 历史数据中这一天有排班任务，如果休息则是空列表
                    emp_pblist[eid][i] = 1
                    history_data[eid][date].sort(key=lambda x: strtonum(x[1].split(' ')[1][:5]))  # 按班次开始时间升序排序
                    #print('x[1].split(' ')[1][:5])=',history_data[eid][date][0][1].split(' ')[1][:5])
                    for j in range(len(history_data[eid][date])):
                        wt = history_data[eid][date][j]
                        emp_pbwt[eid][i] += float(wt[3])  # 工时累加
                        emp_pbsn[eid][i] += 1  # 当天的班次个数+1
                        emp_shiftlen[eid].append(wt[3])  # 增加一个班次长度数据
                        if (j > 0) and (j < len(history_data[eid][date])):
                            jg = (strtonum(wt[1].split(' ')[1][:5]) - strtonum(history_data[eid][date][j-1][2].split(' ')[1][:5])) * 60
                            emp_interval[eid].append(jg)
                else:
                    continue
                    # emp_pblist[eid][i] = 2  # 该员工当天排班矩阵状态为休息（不可用）
            #print('历史数据处理完毕！',eid)
            return emp_pblist, emp_pbwt, emp_pbsn, emp_shiftlen, emp_interval, days

        #历史排班合规性校验
        def check_history_data(eid,ruletag,k, caution, score,rule_start, pb_start, cid,emp_matchpro,flag):
            emp_pblist,emp_pbwt,emp_pbsn,emp_shiftlen,emp_interval,days = handle_HistoryData(rule_start, pb_start, cid,eid)

            flag, score = check_ruleType(1,ruletag, k, caution,flag, score,0,(days-1),eid,
                                         '',emp_pblist,emp_pbwt,emp_pbsn,emp_matchpro,emp_shiftlen,emp_interval)
            #print('历史排班合规性校验校验完毕！',eid)

            return flag, score,emp_pblist,emp_pbwt,emp_pbsn

        #规则周期
        def cycleRule(begin,end,pb_start,pb_end,ruletag, k, caution, flag, score, eid, date,
                                             emp_pblist, emp_pbwt, emp_pbsn, emp_matchpro ):
            # 规则开始结束日期在排班周期内(比排班开始结束日期要小)
            if (begin >= pb_start) and (end <= pb_end):
                beg_ind = (begin - pb_start).days  # 规则开始日期在排班周期中的index
                end_ind = (end - pb_start).days
                # dataType,ruletag,k,caution,flag,score,beg_ind,end_ind,eid,date,emp_pblist,emp_pbwt,emp_pbsn,emp_matchpro,emp_shiftlen,emp_interval
                flag, score = check_ruleType(0, ruletag, k, caution, flag, score, beg_ind, end_ind, eid, date,
                                             emp_pblist, emp_pbwt, emp_pbsn, emp_matchpro, '', '')
            # 规则开始在排班开始之前，规则结束在排班结束之后
            elif begin < pb_start and end > pb_end:
                # 再加上历史数据，先校验历史数据的部分合规性
                history_emp_pblist, history_emp_pbwt, history_emp_pbsn, history_emp_shiftlen, history_emp_interval, days = handle_HistoryData(
                    begin, pb_start, cid, eid)
                history_flag, score = check_ruleType(1, ruletag, k, caution, flag, score, 0, (days - 1), eid,
                                                     '', history_emp_pblist, history_emp_pbwt, history_emp_pbsn,
                                                     emp_matchpro, history_emp_shiftlen, history_emp_interval)

                if history_flag == 1:  # 如果已有违反硬规则的
                    return 1,score

                # 历史数据和现在的排班数据合并
                history_emp_pblist[eid].extend(emp_pblist[eid])
                history_emp_pbwt[eid].extend(emp_pbwt[eid])
                history_emp_pbsn[eid].extend(emp_pbsn[eid])
                beg_ind = 0  #
                end_ind = (pb_end - begin).days
                flag, score = check_ruleType(0, ruletag, k, caution, flag, score, beg_ind, end_ind, eid, date,
                                             history_emp_pblist, history_emp_pbwt, history_emp_pbsn, emp_matchpro, '',
                                             '')

            elif (begin < pb_start) and (end < pb_end) and (end > pb_start):
                # 再加上历史数据，先校验历史数据的部分合规性
                history_emp_pblist, history_emp_pbwt, history_emp_pbsn, history_emp_shiftlen, history_emp_interval, days = handle_HistoryData(
                    begin, pb_start, cid, eid)
                history_flag, score = check_ruleType(1, ruletag, k, caution, flag, score, 0, (days - 1),
                                                     eid, '', history_emp_pblist, history_emp_pbwt,
                                                     history_emp_pbsn, emp_matchpro, history_emp_shiftlen,
                                                     history_emp_interval)

                if history_flag == 1:  # 如果历史排班已违反硬规则
                    return 1,score

                # 历史数据和现在的排班数据合并
                history_emp_pblist[eid].extend(emp_pblist)
                history_emp_pbwt[eid].extend(emp_pbwt)
                history_emp_pbsn[eid].extend(emp_pbsn)
                beg_ind = 0  #
                end_ind = len(history_emp_pblist) - 1
                flag, score = check_ruleType(0, ruletag, k, caution, flag, score, beg_ind, end_ind, eid, date,
                                             emp_pblist, emp_pbwt, emp_pbsn, emp_matchpro, '', '')
            elif (begin > pb_start) and (begin < pb_end) and (end > pb_end):
                beg_ind = (begin - pb_start).days  # 规则开始日期在排班周期中的index
                end_ind = (pb_end - pb_start).days  # 排班结束的index
                flag, score = check_ruleType(0, ruletag, k, caution, flag, score, beg_ind, end_ind, eid, date,
                                             emp_pblist, emp_pbwt, emp_pbsn, emp_matchpro, '', '')

            return flag, score

        #返回合规性检查结果，flag=0 符合，1 不符合。
        def hg_fuhe(emp_rules,emp_matchpro,eid,caution,ruletag,score,pb_start,pb_end,emp_pblist,emp_pbsn, emp_pbwt,date,cid):
            date = datetime.strptime(date,'%Y-%m-%d').date()
            pb_start = datetime.strptime(pb_start, '%Y-%m-%d').date()
            pb_end = datetime.strptime(pb_end, '%Y-%m-%d').date()
            flag = 0 #默认没有规则，即符合规则
            #员工合规性检查
            #if caution in emp_rules[ruletag]:#如果规则中有这个类型的规则'forbid':[（开始*结束，比较类型,数值,shiftid,certname,cycle）,...]
            if len(emp_rules[ruletag][caution]) != 0:
                for k in emp_rules[ruletag][caution]:
                    rule_begin = datetime.strptime(k[0].split('*')[0], '%Y-%m-%d').date()#规则开始日期
                    rule_end = datetime.strptime(k[0].split('*')[1], '%Y-%m-%d').date()#规则结束日期
                    rule_date = []#[(2019-07-01,2019-07-07),()]
                    if rule_end < pb_start:#规则结束日期在排班开始之前，则要循环规则，找到排班开始所对应的区间
                        if k[5] == 'day' or k[5] == '':#k[5]表示周期，week，month，day,''
                            if rule_begin <= pb_start:
                                flag, score = cycleRule(date, date, pb_start, pb_end, ruletag, k, caution, flag, score,
                                                        eid, date,
                                                        emp_pblist, emp_pbwt, emp_pbsn, emp_matchpro)
                        elif k[5] == 'week':
                            while 1:#规则结束日期在排班开始之前，一直循环规则周期,直到规则和排班周期有重合
                                rule_begin = rule_end + relativedelta(days=+1)#规则的下一个开始日期=上一个结束的后一天
                                rule_end = rule_begin + relativedelta(weeks=+1)
                                rule_end -= relativedelta(days=+1)
                                if rule_begin<=pb_start and  rule_end >= pb_start:
                                    rule_date.append((rule_begin,rule_end))
                                elif rule_begin>=pb_start and rule_begin<=pb_end:
                                    rule_date.append((rule_begin, rule_end))
                                if rule_begin > pb_end:
                                    break

                            for start,end in rule_date:
                                flag, score = cycleRule(start,end, pb_start, pb_end, ruletag, k, caution, flag, score, eid, date,
                                      emp_pblist, emp_pbwt, emp_pbsn, emp_matchpro)
                                if flag == 1:  # 如果已有违反硬规则的
                                    break

                        elif k[5] == 'month':
                            pass
                        else:
                            pass

            return flag,score

        #检查指定类别的合规性
        def hgcheck_ruleType(emp_rules, emp_matchpro, eid, ruletag, score,pb_start,pb_end,emp_pblist,emp_pbsn, emp_pbwt,date,cid):
            # 检查员工总工时shiftTime
            #ruletag, emp_tag = 'shiftTime', 'all_wt'
            res_flag = 0 #默认没有违背硬性规则
            cautions = ['forbid', 'hint', 'warning']
            for caution in cautions:
                flag, score = hg_fuhe(emp_rules,emp_matchpro,eid,caution,ruletag,score,pb_start,pb_end,emp_pblist,emp_pbsn, emp_pbwt,date,cid)
                if flag == 1:#若违反了硬性规则
                    res_flag = 1
                    return res_flag, score
                # elif not flag:#无规则
                #     return False,score
            return res_flag, score

        #员工合规性检查，写成打分模型，初始都为满分100，违反软性规则 -1分/条，违反硬性规则，得分为0，直接返回
        #emp_pblist 员工是否排班的0，1矩阵
        def check_empcompliance(emp_rules,cid,eid,emp_matchpro,date,emp_pblist,pb_start,pb_end,emp_pbsn,emp_pbwt,now_score):
            #emp_matchpro 员工属性  start 排班开始日期  end 排班结束日期
            #emp_rules, flag = PBResultDB.select_emphgrule(cid,eid)#获取该员工的合规性规则
            score = now_score[eid]

            #1 检查员工总工时shiftTime
            ruletag = 'shiftTime'
            res_flag, score = hgcheck_ruleType(emp_rules, emp_matchpro, eid, ruletag, score,
                                               pb_start, pb_end, emp_pblist, emp_pbsn, emp_pbwt,date,cid)
            if not res_flag:
                res_flag = 2
                #return False, score  # 无规则
            elif res_flag == 1:  # 违反了硬性规则
                return res_flag, score
            #2 检查员工已排班次个数
            ruletag = 'schShiftNum'
            res_flag, score = hgcheck_ruleType(emp_rules, emp_matchpro, eid, ruletag, score,
                                               pb_start, pb_end, emp_pblist,emp_pbsn, emp_pbwt,date,cid)
            if not res_flag:
                res_flag = 2
                #return False, score  #
            elif res_flag == 1:  # 违反了硬性规则
                return res_flag, score

            #3 检查员工连续排班天数
            ruletag = 'schDayNumCon'
            res_flag, score = hgcheck_ruleType(emp_rules, emp_matchpro, eid, ruletag, score,pb_start,pb_end,emp_pblist,
                                               emp_pbsn, emp_pbwt,date,cid)
            if not res_flag:
                res_flag = 2
                #return False, score#
            elif res_flag == 1:  # 违反了硬性规则
                return res_flag, score
            #4 检查员工连续休息天数
            ruletag = 'restNumCon'
            res_flag, score = hgcheck_ruleType(emp_rules, emp_matchpro, eid, ruletag, score,pb_start, pb_end,
                                               emp_pblist, emp_pbsn, emp_pbwt,date,cid)
            if not res_flag:
                res_flag = 2
                #return False, score  # 规则有错或无规则
            elif res_flag == 1:  # 违反了硬性规则
                return res_flag, score
            #5 检查员工未排班天数
            ruletag = 'noSchNum'
            res_flag, score = hgcheck_ruleType(emp_rules, emp_matchpro, eid, ruletag, score,pb_start, pb_end,
                                               emp_pblist, emp_pbsn, emp_pbwt,date,cid)
            if not res_flag:
                res_flag = 2
                #return False, score  # 规则有错
            elif res_flag == 1:  # 违反了硬性规则
                return res_flag, score
            #6 检查员工休息天数
            ruletag = 'restNum'
            res_flag, score = hgcheck_ruleType(emp_rules, emp_matchpro, eid, ruletag, score,pb_start, pb_end,
                                               emp_pblist, emp_pbsn, emp_pbwt,date,cid)
            if not res_flag:
                res_flag = 2
                #return False, score  # 规则有错
            elif res_flag == 1:  # 违反了硬性规则
                return res_flag, score

            #7 检查员工排班次间隔
            ruletag = 'interval'
            res_flag, score = hgcheck_ruleType(emp_rules, emp_matchpro, eid, ruletag, score,
                                               pb_start, pb_end, emp_pblist, emp_pbsn, emp_pbwt,date,cid)
            if res_flag == 1:  # 违反了硬性规则
                return res_flag, score
            #8 检查员工班次长度
            ruletag = 'shiftLen'
            res_flag, score = hgcheck_ruleType(emp_rules, emp_matchpro, eid, ruletag, score,
                                               pb_start, pb_end, emp_pblist, emp_pbsn, emp_pbwt,date,cid)
            if res_flag == 1:  # 违反了硬性规则
                return res_flag, score

            #9 检查员工所需证书到期天数
            ruletag = 'certExpireDays'
            res_flag, score = hgcheck_ruleType(emp_rules, emp_matchpro, eid, ruletag, score,
                                               pb_start, pb_end, emp_pblist, emp_pbsn, emp_pbwt,date,cid)

            if res_flag == 1:  # 违反了硬性规则
                return res_flag, score

            return res_flag,score

        #部门合规性检查
        def check_orgcompliance(cid,did,date):
            pass

        #emp_pb:员工排班结果  {'23': [0, 0, 0, 0, 0, 0, 0, 0, 0]},...
        #返回员工当天的班次情况列表，一小时及以下的独立非固定任务舍弃
        def emp_dayshift(emp_pb,timeInterval):
            emps_dayshift = {}
            for eid in emps_eid:
                #emp_shift, emp_pb = emp_dayshift(emp_pb, eid, timeInterval)
                worklist = emp_pb[eid]#某员工某天的排班列表
                length = len(worklist)
                work_shift = []#每人每天的班次情况，[(开始，结束),(开始，结束),...]
                i = 0
                while i < length:
                    if worklist[i] != 0:
                        start_time = (i*timeInterval)/60
                        j = i+1
                        while j < length:
                            if worklist[j] != 0:
                                j += 1
                            else:
                                if (j-i == 1) and worklist[i].split('-')[1] != 'fixedwh':#半小时或1小时的且不是固定任务的，直接舍弃
                                    worklist[i] = 0
                                    i = j
                                    break
                                elif (j-i == 2) and worklist[i].split('-')[1] != 'fixedwh':
                                    worklist[i] = 0
                                    worklist[i+1] = 0
                                    i = j
                                    break
                                else:
                                    end_time = (j*timeInterval)/60
                                    end_time = numtostr(end_time)
                                    start_time = numtostr(start_time)
                                    work_shift.append([start_time,end_time])
                                    i = j
                                    break
                    else:
                        i += 1
                emps_dayshift[eid] = work_shift

            return emps_dayshift,emp_pb

        #虚拟员工排班优化
        def virtualEmpTaskDrop(virtual_emp):
            for eid in list(virtual_emp.keys()):
                worklist = virtual_emp[eid]#虚拟员工某天的排班列表
                length = len(worklist)
                #work_shift = []#每天的班次情况，[(开始，结束),(开始，结束),...]
                i = 0
                while i < length:
                    if worklist[i] != 0:
                        j = i+1
                        while j < length:
                            if worklist[j] != 0:
                                j += 1
                            else:
                                if (j-i == 1) and (worklist[i].split('-')[1] != 'fixedwh'):#半小时或1小时的且不是固定任务的，直接舍弃:#半小时或1小时的任务，直接舍弃
                                    worklist[i] = 0
                                    i = j
                                    break
                                elif (j-i == 2) and (worklist[i].split('-')[1] != 'fixedwh'):#半小时或1小时的且不是固定任务的，直接舍弃:
                                    worklist[i] = 0
                                    worklist[i+1] = 0
                                    i = j
                                    break
                                else:
                                    # end_time = (j*timeInterval)/60
                                    # end_time = numtostr(end_time)
                                    # start_time = numtostr(start_time)
                                    # work_shift.append((start_time,end_time))
                                    i = j
                                    break
                    else:
                        i += 1

                if worklist.count(0) == len(worklist):
                    del virtual_emp[eid] #如果删完后，该员工没有排班了，则将这个员工删除
            return virtual_emp

        # 实际员工排班优化
        def realEmpTaskDrop(emp_pb):
            for eid in list(emp_pb.keys()):
                worklist = emp_pb[eid]  # 虚拟员工某天的排班列表
                length = len(worklist)
                # work_shift = []#每天的班次情况，[(开始，结束),(开始，结束),...]
                i = 0
                while i < length:
                    if worklist[i] != 0:
                        j = i + 1
                        while j < length:
                            if worklist[j] != 0:
                                j += 1
                            else:
                                if (j - i == 1) and (worklist[i].split('-')[
                                                         1] != 'fixedwh'):  # 半小时或1小时的且不是固定任务的，直接舍弃:#半小时或1小时的任务，直接舍弃
                                    worklist[i] = 0
                                    i = j
                                    break
                                elif (j - i == 2) and (
                                        worklist[i].split('-')[1] != 'fixedwh'):  # 半小时或1小时的且不是固定任务的，直接舍弃:
                                    worklist[i] = 0
                                    worklist[i + 1] = 0
                                    i = j
                                    break
                                else:
                                    i = j
                                    break
                    else:
                        i += 1

            return emp_pb

        #实际员工：当前待排任务和已排任务是否可组合
        def combineOrNot(tasktype,eid,emp_matchpro,taskcombine_list,id_li):
            flag = 1 #默认不可排
            if tasktype == 'indirectwh':
                flag = 0
            elif (len(emp_matchpro[eid]['taskid_set']) == 1) and (taskID in emp_matchpro[eid]['taskid_set']):#相同任务
                flag = 0
            elif taskID not in id_li:#该任务是独立任务
                flag = 1
            elif len(taskcombine_list) != 0:#有可组合任务:
                li = emp_matchpro[eid]['taskid_set']
                #new = copy.deepcopy(li).append(taskID)
                for com in taskcombine_list:
                    if li.issubset(set(com)):  #添加待排任务后的任务列表在可组合任务集合中
                        flag = 0

            return flag

        #虚拟员工 当前待排任务和已排任务是否可组合
        def v_combineOrNot(tasktype,vemp_taskid, taskID, taskcombine_list, id_li):
            flag = 1  # 默认不可排
            if tasktype == 'indirectwh':
                flag = 0
            elif (len(vemp_taskid) == 1) and (taskID in vemp_taskid):
                flag = 0
            elif taskID not in id_li:  # 该任务是独立任务
                flag = 1
            elif len(taskcombine_list) != 0:#有可组合任务:
                #new = copy.deepcopy(vemp_taskid).add(taskID)
                new = copy.deepcopy(vemp_taskid)
                new.add(taskID)
                for com in taskcombine_list:
                    if new.issubset(set(com)):  # 添加待排任务后的任务列表在可组合任务集合中
                        flag = 0
            return flag

        #检查规则中指定班次的个数，emp_zdbcNum：返回规则中的指定班次及已有的次数(在规则周期内的次数)
        #{'id*s*e':[现有个数，规则比较类型，规则数值]，。。。}
        def get_zdbc(eid,emp_rules,date,cid,did,emps_shifts):
            bc_list = emps_shifts[date][eid]#某员工当天的班次列表
            date = datetime.strptime(date,'%Y-%m-%d').date()
            rule_li = emp_rules['apShiftNum']['forbid']
            emp_zdbcNum = {}
            if len(rule_li) != 0:#该员工有指定班次且是禁止的规则
                for rule in rule_li:
                    s,e = datetime.strptime(rule[0].split('*')[0],'%Y-%m-%d').date(),datetime.strptime(rule[0].split('*')[1],'%Y-%m-%d').date()
                    bjlx, num, shiftid = rule[1], int(rule[2]), rule[3]
                    # 获取出指定班次的（起，止时间，是否跨天）
                    res, flag = get_shiftMod(cid, did, shiftid)
                    #print('res, flag ',res, flag)
                    if res != None:#如果该班次存在
                        emp_zdbcNum[shiftid+'*'+str(res[0])+'*'+str(res[1])] = [0,bjlx,num]
                        if date >= s and date <= e:#
                            for bc in bc_list:
                                if (bc[0] == res[0]) and (bc[1] == res[1]):#该员工这一天中有这个指定班次
                                    emp_zdbcNum[shiftid+'*'+res[0]+'*'+res[1]][0] += 1
                                else:
                                    continue
            return emp_zdbcNum
        #检查指定班次个数
        def cheak_zdbc(emp_zdbcNum,emp_no_time,eid):
            #no_time = []#该员工不可用时间段列表
            flag = 0 #默认未违反规则
            for k,v in emp_zdbcNum.items():
                if v[1] == 'ge':#大于等于
                    if v[0] == (int(v[2])-1):#v[2] 被比较数值
                        flag = 1
                        emp_no_time[eid].append((k.split('*')[1],k.split('*')[2]))#该员工这个时间段设为不可用
                elif v[1] == 'gt':#大于
                    if v[0] == int(v[2]):  # v[2] 被比较数值
                        flag = 1
                        emp_no_time[eid].append((k.split('*')[1], k.split('*')[2]))  # 该员工这个时间段设为不可用
            return emp_no_time,flag

        #检查员工的这个任务在该时段是否可用
        def ckeck_time(emp_no_time,eid,task_starttime, task_endtime):
            if len(emp_no_time[eid]) != 0:#有不可用时段
                flag = 0 #默认可排
                for t in emp_no_time[eid]:
                    if not (task_starttime >= t[1] or task_endtime <= t[0]):#开始时间在不可用时段之后或结束时间在不可用时段之前
                        flag = 1 #不可排
                    else:
                        continue
                    if flag == 1:
                        break
            else:#无不可用时段
                flag = 0
            return flag

        #相同排班检查，从规则开始日期开始检查 emps_res：员工全部的排班情况，包括历史排班
        def check_samePB(eid,emps_res,date,emp_rules):
            date = datetime.strptime(date,'%Y-%m-%d').date()
            rule = emp_rules['schNumSame']['forbid']
            flag = 0 #默认没有违反相同排班天数硬规则
            if len(rule) != 0 :
                for r in rule:
                    s, e = datetime.strptime(r[0].split('*')[0], '%Y-%m-%d').date(), datetime.strptime(
                        r[0].split('*')[1], '%Y-%m-%d').date()
                    bjlx, num = [1], int(r[2])
                    d = s
                    work_dic = {} #{排班表元祖：数量}
                    while d <= date:#从规则开始日期直到当前日期
                        if str(d) in emps_res:#由于没有历史排班数据，所以员工排班字典中可能没有数据
                            if tuple(emps_res[str(d)][eid]) not in work_dic:
                                work_dic[tuple(emps_res[str(d)][eid])] = 1
                            else:
                                work_dic[tuple(emps_res[str(d)][eid])] += 1
                        d = d + timedelta(days=1)
                    if len(work_dic) != 0:
                        top_num = sorted(work_dic.items(),key=lambda x:x[1],reverse=True)[0][1]
                    if bjlx == 'ge':#大于等于'
                        if top_num == (num-1):
                            flag = 1
                    elif bjlx == 'gt':#大于
                        if top_num == num:
                            flag = 1
                    if flag == 1:
                        break
            return flag

        #结果格式化输出
        def jsonOut(emps_res,timeInterval,applyId):
            result = {}  # 最后的格式化输出
            data = {}
            data['applyId'] = applyId
            data['schemes'] = [{'worktime': ''}]
            data['cal'] = []
            for date, emp_value in emps_res.items():
                for eid, tasklist in emp_value.items():
                    emp_dic = {}
                    emp_dic['eid'] = eid
                    emp_dic['schDay'] = date
                    emp_dic['allWorkTime'] = 0
                    emp_dic['workUnit'] = []
                    i = 0
                    while i < len(tasklist):
                        if tasklist[i] == 0:
                            i += 1
                        else:
                            work = {}
                            work['type'] = 'task'
                            work['outId'] = tasklist[i]
                            work['shiftId'] = ''
                            work['startTime'] = date + ' ' + numtostr(float((i * timeInterval) / 60))
                            j = i + 1
                            while j < len(tasklist):
                                if tasklist[j] == tasklist[i]:
                                    j += 1
                                    if j == len(tasklist):
                                        work['endTime'] = date + ' ' + numtostr((j * timeInterval) / 60)
                                        work['workTime'] = int((j - i) * timeInterval)
                                        emp_dic['allWorkTime'] += int(work['workTime'])
                                        emp_dic['workUnit'].append(work)
                                        i = j
                                        break
                                else:
                                    work['endTime'] = date + ' ' + numtostr((j * timeInterval) / 60)
                                    work['workTime'] = int((j - i) * timeInterval)
                                    emp_dic['allWorkTime'] += int(work['workTime'])
                                    emp_dic['workUnit'].append(work)
                                    i = j
                                    break
                    emp_dic['allWorkTime'] = emp_dic['allWorkTime']
                    if emp_dic['allWorkTime'] != '0':
                        data['cal'].append(emp_dic)

            result['data'] = data
            return result

        # 间接任务-实际员工安插[('2019-07-12', '201903291241432550431007959f0213', 5580.0, 'indirectwh')]
        def indirectTask(eids_rule,indirect_task_list, cid, did, emp_pb, emp_pblist, emp_pbwt, emp_pbsn, j, emps_shifts, date,
                         timeInterval, emps_score,emp_matchpro,all_tnum):
            for task in indirect_task_list:
                taskid = task[1]
                intask_gs = int(task[2] / timeInterval)  # 间接任务工时数,可分为多少格
                skillID, sk_flag = get_skillID(taskid, cid, did)  # 得到该任务的技能ID
                certsname, cs_flag = get_certsname(taskid, cid, did)  # 得到该任务的证书名称list
                if (not sk_flag) and (not cs_flag):
                    save_result = {'code': 101, 'result': 'DB操作失败'}
                    return save_result
                elif len(skillID) == 0 and len(certsname) == 0:  # 任务不需要技能和证书
                    empid_li = emps_eid  # 从所有待排员工中选择
                elif len(skillID) == 0:  # 不需要技能
                    empid_li_c, em_flag_c = get_empID_c(certsname, cid)  # 获取拥有所需证书的员工id列表
                    if not em_flag_c:
                        save_result = {'code': 101, 'result': 'DB操作失败'}
                        return save_result
                    empid_li_c.extend(emps_eid)
                    # 从待排员工中筛选出具备证书的员工列表
                    empid_li = [k for k, v in dict(Counter(empid_li_c)).items() if v == 2]
                elif len(certsname) == 0:  # 不需要证书
                    empid_li_s, em_flag = get_empID(skillID, cid)  # 获取拥有该技能的员工id列表
                    if not em_flag:
                        save_result = {'code': 101, 'result': 'DB操作失败'}
                        return save_result
                    empid_li_s.extend(emps_eid)
                    # 从待排员工中筛选出具备技能的员工列表
                    empid_li = [k for k, v in dict(Counter(empid_li_s)).items() if v == 2]
                else:
                    # [(员工ID, 技能值), (eid, skillnum)]
                    empid_li_s, em_flag = get_empID(skillID, cid)  # 获取拥有该技能的员工id列表
                    empid_li_c, em_flag_c = get_empID_c(certsname, cid)  # 获取拥有要求证书的员工id列表
                    if (not em_flag) and (not em_flag_c):
                        save_result = {'code': 101, 'result': 'DB操作失败'}
                        return save_result
                    empid_li_s.extend(empid_li_c)
                    # 筛选出同时具备技能和证书的员工
                    empid_li = [k for k, v in dict(Counter(empid_li_s)).items() if v == 2]
                    empid_li.extend(emps_eid)
                    # 从待排员工中筛选出同时具备技能和证书的员工列表
                    empid_li = [k for k, v in dict(Counter(empid_li)).items() if v == 2]
                # empid_li:最后符合要求的员工ID列表,emp_pb:当天所有实际员工的排班字典
                eid_ = []  # 去除当天休息的员工后最后剩下的可用eid列表
                for eid in empid_li:
                    if emp_pblist[eid][j] != 2:  # 当天休息的不考虑，j表示是排班周期内的第几天
                        eid_.append(eid)

                emp_wt = dict(sorted(emp_pbwt.items(), key=lambda x: x[1][j]))
                for eid in list(emp_wt.keys()):
                    if eid in eid_:
                        # '12': [('05:30', '13:00'), ('14:30', '22:00')],
                        shiftNum = len(emps_shifts[date][eid])
                        if shiftNum >= 1:
                            for i in range(shiftNum):
                                while intask_gs > 0:
                                    start_time = strtonum(emps_shifts[date][eid][i][0])
                                    end_time = strtonum(emps_shifts[date][eid][i][1])
                                    worktime = (end_time - start_time) * 60  # 班次时长
                                    index = int((end_time * 60) / timeInterval)  # 结束时间后面一位索引，也就是填补可以从该位置填
                                    if shiftNum == 1:#只有一个班次直接往后填
                                        if index < all_tnum-2:
                                            temp_emp_pbwt = copy.deepcopy(emp_pbwt)
                                            temp_emp_matchpro = copy.deepcopy(emp_matchpro)
                                            temp_emps_score = copy.deepcopy(emps_score)
                                            emp_pbwt[eid][j] += timeInterval
                                            emp_matchpro[eid]['now_shiftlen'] = worktime + timeInterval
                                            if eid in eids_rule:
                                                hg_flag, score = check_empcompliance(emp_rules, cid, eid, emp_matchpro,
                                                                                     date,
                                                                                     emp_pblist, start, end, emp_pbsn,
                                                                                     emp_pbwt,
                                                                                     emps_score)
                                            else:
                                                hg_flag, score = 0, emps_score[eid]
                                            # 看该员工的special time 满不满足，0可排  1不可排
                                            t_flag = emp_special(eid, date, end_time, end_time + timeInterval / 60,
                                                                 emps_notime)
                                            if hg_flag == 1 or t_flag == 1:  # 违规了
                                                emp_matchpro = temp_emp_matchpro
                                                emp_pbwt = temp_emp_pbwt
                                                emps_score = temp_emps_score
                                                break
                                            else:
                                                emp_pb[eid][index] = taskid + '-' + 'indirectwh'
                                                intask_gs -= 1
                                                emps_shifts[date][eid][i][1] = numtostr(end_time + timeInterval / 60)
                                                emps_score[eid] = score
                                        else:
                                            break

                                    elif shiftNum == 2:
                                        if emp_pb[eid][index+1] == 0 and index < all_tnum-2:
                                            temp_emp_pbwt = copy.deepcopy(emp_pbwt)
                                            temp_emp_matchpro = copy.deepcopy(emp_matchpro)
                                            temp_emps_score = copy.deepcopy(emps_score)
                                            emp_pbwt[eid][j] += timeInterval
                                            emp_matchpro[eid]['now_shiftlen'] = worktime + timeInterval
                                            if i == 0:
                                                emp_matchpro[eid]['interval'] = (strtonum(emps_shifts[date][eid][i+1][0]) - end_time)*60-timeInterval
                                            if eid in eids_rule:
                                                hg_flag, score = check_empcompliance(emp_rules, cid, eid, emp_matchpro, date,
                                                                                     emp_pblist, start, end, emp_pbsn, emp_pbwt,
                                                                                     emps_score)
                                            else:
                                                hg_flag, score = 0,emps_score[eid]
                                            # 看该员工的special time 满不满足，0可排  1不可排
                                            t_flag = emp_special(eid, date, end_time, end_time + timeInterval / 60,
                                                                 emps_notime)
                                            if hg_flag == 1 or t_flag == 1:#违规了
                                                emp_matchpro = temp_emp_matchpro
                                                emp_pbwt = temp_emp_pbwt
                                                emps_score = temp_emps_score
                                                break
                                            else:
                                                emp_pb[eid][index] = taskid+'-'+'indirectwh'
                                                intask_gs -= 1
                                                emps_shifts[date][eid][i][1] = numtostr(end_time + timeInterval / 60)
                                                emps_score[eid] = score
                                        else:
                                            break
                                    elif shiftNum > 2:#填充间隙看能不能填为2个
                                        if emp_pb[eid][index+1] == 0 and index < all_tnum-2:
                                            temp_emp_pbwt = copy.deepcopy(emp_pbwt)
                                            temp_emp_matchpro = copy.deepcopy(emp_matchpro)
                                            temp_emps_score = copy.deepcopy(emps_score)
                                            emp_pbwt[eid][j] += timeInterval
                                            emp_matchpro[eid]['now_shiftlen'] = worktime + timeInterval
                                            if eid in eids_rule:
                                                hg_flag, score = check_empcompliance(emp_rules, cid, eid, emp_matchpro,
                                                                                     date,
                                                                                     emp_pblist, start, end, emp_pbsn,
                                                                                     emp_pbwt,
                                                                                     emps_score)
                                            else:
                                                hg_flag, score = 0, emps_score[eid]
                                            # 看该员工的special time 满不满足，0可排  1不可排
                                            t_flag = emp_special(eid, date, end_time, end_time + timeInterval / 60,
                                                                 emps_notime)
                                            if hg_flag == 1 or t_flag == 1:  # 违规了
                                                emp_matchpro = temp_emp_matchpro
                                                emp_pbwt = temp_emp_pbwt
                                                emps_score = temp_emps_score
                                                break
                                            else:
                                                emp_pb[eid][index] = taskid + '-' + 'indirectwh'
                                                intask_gs -= 1
                                                emps_shifts[date][eid][i][1] = numtostr(end_time + timeInterval / 60)
                                                emps_score[eid] = score
                                        elif emp_pb[eid][index+1] != 0:
                                            start_time_ = strtonum(emps_shifts[date][eid][i+1][0])
                                            end_time_ = strtonum(emps_shifts[date][eid][i+1][1])
                                            worktime_ = (end_time - start_time) * 60  # 班次时长
                                            emp_matchpro[eid]['now_shiftlen'] += worktime_

                                            temp_emp_pbwt = copy.deepcopy(emp_pbwt)
                                            temp_emp_matchpro = copy.deepcopy(emp_matchpro)
                                            temp_emps_score = copy.deepcopy(emps_score)
                                            emp_pbwt[eid][j] += timeInterval
                                            emp_matchpro[eid]['now_shiftlen'] += timeInterval
                                            if eid in eids_rule:
                                                hg_flag, score = check_empcompliance(emp_rules, cid, eid, emp_matchpro,
                                                                                     date,
                                                                                     emp_pblist, start, end, emp_pbsn,
                                                                                     emp_pbwt,
                                                                                     emps_score)
                                            else:
                                                hg_flag, score = 0, emps_score[eid]
                                            # 看该员工的special time 满不满足，0可排  1不可排
                                            t_flag = emp_special(eid, date, end_time, end_time + timeInterval / 60,
                                                                 emps_notime)
                                            if hg_flag == 1 or t_flag == 1:  # 违规了
                                                emp_matchpro = temp_emp_matchpro
                                                emp_pbwt = temp_emp_pbwt
                                                emps_score = temp_emps_score
                                                break
                                            else:
                                                emp_pb[eid][index] = taskid + '-' + 'indirectwh'
                                                intask_gs -= 1
                                                emps_shifts[date][eid][i][1] = emps_shifts[date][eid][i+1][1]
                                                #班次已合并，将第二个班次删掉
                                                emps_shifts[date][eid].pop(i+1)
                                                emps_score[eid] = score

                                        else:
                                            break


                        else:  # 一天只有一个班次的，不填充
                            continue


                task[2] = intask_gs*timeInterval #现在剩余间接任务情况

            return emp_pb,emp_pbwt,emps_shifts,indirect_task_list

        #间接任务-虚拟员工安插
        def indiretTask_virtualEmp(indirect_task_list,virtual_emp,all_tnum,timeInterval,splitRule):
            max_gs = float(splitRule['worktime'][1]) #虚拟员工每天的最大工时数
            #max_num = int(max_gs/timeInterval) #最大工时占多少格子
            for task in indirect_task_list:
                taskid = task[1]
                intask_gs = int(task[2] / timeInterval)  # 间接任务工时数,可分为多少格
                for k in sorted(virtual_emp):
                    #vemp_taskid = set(i.split('-')[0] for i in virtual_emp[k] if i != 0)  # 每个员工目前已有的任务ID列表（不重复）

                    i = 11
                    while (i <all_tnum) and (intask_gs > 0):
                        new_v = [i.split('-')[0] for i in virtual_emp[k] if i != 0]
                        v_worktime = (len(new_v) + 1) * timeInterval  # 已有工作时长+排上这个任务后的总时长
                        if virtual_emp[k][i] == 0 and (v_worktime <= max_gs):  # 这个员工这个时段未排任务，且加上这个任务后的总工时没有超过工时限制
                            virtual_emp[k][i] = taskid + '-' + 'indirectwh'
                            i += 1
                            intask_gs -= 1
                        else:
                            i += 1

                xuni_eid = -len(virtual_emp) - 1
                print('xuni_eid=',xuni_eid)
                if intask_gs > 0:#还有间接任务没排完,从最早上班时间开始，每天2个班次，每个班次4小时，中间间隔1.5小时
                    virtual_emp[str(xuni_eid)] = [0 for i in range(all_tnum)]
                    j = 11
                    while j < 29 and (intask_gs > 0):
                        if j < 19:
                            virtual_emp[str(xuni_eid)][j] = taskid + '-' + 'indirectwh'
                            j += 1
                            intask_gs -= 1
                        elif j == 19:
                            j += 3
                        else:
                            virtual_emp[str(xuni_eid)][j] = taskid + '-' + 'indirectwh'
                            j += 1
                            intask_gs -= 1
                    xuni_eid -= 1
                task[2] = intask_gs * timeInterval  # 现在剩余间接任务情况
            return virtual_emp


        #目前只有任务类型的排班
        if schType == '0':
            if scheme == 'worktime':#如果排班方案要求工时最少
                mode = 1
            else:
                mode = 0
            # {eid1: {开始-结束日期1：[开始时间，结束时间],
            #       开始-结束日期2：[开始时间，结束时间]}
            # }
            emps_notime,emps_eid = emp_notime(emps)  # 所有待排员工的不可用时段字典,所有待排员工ID列表
            eids_rule = PBResultDB.select_emphgrule(cid, emps_eid)  # 所有待排员工的规则字典
            against_softRule = 0#1 违反软约束最少  0 只要不违反硬约束就行
            emps_list = copy.deepcopy(emps_eid)
            print('emps_eid=',emps_eid)
            #emps_eid, emp_matchpro = emps_attr(emps,cid)#所有待排员工ID列表和员工属性字典
            for did in didArr:#遍历所有待排部门
                date_li = get_PBdate(start, end) #获取所有待排班日期列表
                all_pbdays = len(date_li) #排班总天数
                emp_pblist = {} #排班周期内，每天是否排班、休息情况{eid:[],eid:[],,,,}
                emp_pbwt = {} #排班周期内，每天的工时情况
                emp_pbsn = {}  # 排班周期内，每天的班次个数情况
                emp_no_time = {}  # 员工不可用时间段列表(指定班次和相同排班校验产生的)
                emps_score = {}  # 员工排班的分数，分数越高表示违反的软规则越少
                for eid in emps_eid:
                    emp_pblist[eid] = [0 for i in range(all_pbdays)]#初始化每个员工的排班周期内的排班列表，0 可用但未排班 2 当天休息不可用，1 当天排班，
                    emp_pbwt[eid] = [0 for i in range(all_pbdays)]#初始化每个员工每天的工时为0，后面排任务时，累加即可
                    emp_pbsn[eid] = [0 for i in range(all_pbdays)]#初始化每个员工每天的班次个数为0，后面排任务时，累加即可
                    emp_no_time[eid] = [] #初始化每个员工的不可用时段
                    #emps_score[eid] = 100  # 待选员工安排任务后的分数，分数越高表示违反的软规则越少.初始默认100
                    emps_score[eid] = {}  # 待选员工安排任务后的软约束违反情况,{ruletag:num,...}
                print('初始emps_score',emps_score)
                #emp_pblist为排班周期内，员工的不可用和可用状态已标好（0，2矩阵）
                for d in range(all_pbdays):
                    res = emp_type(cid, date_li[d])
                    for eid in emps_eid:
                        res_flag = 1  # 默认不可排
                        if eid in res:
                            if res[eid][0] == '1':
                                res_flag = 1  # 不可排
                            elif res[eid][0] == '0':
                                res_flag = 0  # 可排
                            else:
                                res_flag = 0  # 部分时间可排，也算可用

                        if res_flag == 1:#不可用
                            emp_pblist[eid][d] = 2 #该员工当天排班矩阵状态为休息（不可用）

                emps_res = {} #当前部门下所有日期的排班结果
                emps_shifts = {} #所有员工的每天的班次情况{date1:{eid1:[(),()],eid2:[(),()]}, date2:{},...}
                #i = 1 #第几天，用来算统计周期
                for j in range(all_pbdays):#遍历所有待排日期
                    s_t = datetime.now()
                    import pandas as pd
                    date = date_li[j]
                    print('date:',date)
                    result,flag = receive_matrix(cid,did,date,mode)
                    if flag:  # 获取任务排班矩阵的DB操作成功
                        matrix = result[0]
                        splitRule = json.loads(result[2]) #阶段三的拆分规则字典{interval: ['lt',120,True],worktime:[lt,240,True],shiftNum:[],shiftLen;[]...}
                        indirectTask_list = json.loads(result[3])  # 间接任务列表
                        taskcombine_list = json.loads(result[1]) #任务组合规则列表
                        print('taskcombine_list=',taskcombine_list)
                        id_li = set()
                        if len(taskcombine_list) != 0:
                            for com in taskcombine_list:
                                for id in com:
                                    id_li.add(id)
                            id_li = list(id_li)  # 去重后所有可以组合的任务ID列表
                        emp_matchpro = emps_attr(emps, cid)  # 所有待排员工ID列表和员工属性字典
                        virtual_emp_matchpro = {} #虚拟员工的属性字典{eid:{inter:0}}
                        if len(matrix) != 0:  # 没有任务排班时获取matrix为空元组
                            task_matrix = json.loads(matrix)  # 将json格式还原为列表格式
                            print('task_matrix=',task_matrix)
                            df = pd.DataFrame(data=task_matrix)
                            df.to_csv('./matrix_new{}.csv'.format(date), encoding='utf8')
                            emp_pb = {}#实际员工，每天排班结果，{eid:[,,,,],eid:[,,,,],...}
                            virtual_emp = {}  # 虚拟员工每天的排班结果

                            for eid in emps_eid:
                                emp_pb[eid] = [0 for i in range(all_tnum)]#初始化每个员工当天的任务列表为空，按时间粒度，分为很多格

                            for d_task in task_matrix:#一天的任务排班情况
                                i = 0
                                while i < len(d_task):
                                    if d_task[i] == 0:
                                        i += 1
                                        continue
                                    else:
                                        taskID = d_task[i].split('-')[0]#i表示第几格，获取该任务块的任务ID，若是基于师兄的数据，则要改这个
                                        taskType = d_task[i].split('-')[4] #该任务的任务类型
                                        #taskname = PBResultDB.select_skillName(taskID, cid, did)
                                        skillID,sk_flag = get_skillID(taskID, cid, did)#得到该任务的技能ID list
                                        certsname,cs_flag = get_certsname(taskID, cid, did)#得到该任务的证书名称list
                                        if (not sk_flag) and (not cs_flag):
                                            save_result = {'code': 101, 'result': 'DB操作失败'}
                                            return save_result
                                        elif len(skillID) == 0 and len(certsname) == 0:#任务不需要技能和证书
                                            empid_li = emps_eid #从所有待排员工中选择
                                        elif len(skillID) == 0:#不需要技能
                                            empid_li_c, em_flag_c = get_empID_c(certsname, cid)  # 获取拥有所需证书的员工id列表
                                            if not em_flag_c:
                                                save_result = {'code': 101, 'result': 'DB操作失败'}
                                                return save_result
                                            empid_li_c.extend(emps_eid)
                                            # 从待排员工中筛选出具备证书的员工列表
                                            empid_li = [k for k, v in dict(Counter(empid_li_c)).items() if v == 2]

                                        elif len(certsname) == 0:#不需要证书
                                            empid_li_s, em_flag = get_empID(skillID, cid)  # 获取拥有该技能的员工id列表
                                            if not em_flag:
                                                save_result = {'code': 101, 'result': 'DB操作失败'}
                                                return save_result
                                            empid_li_s.extend(emps_eid)
                                            # 从待排员工中筛选出具备技能的员工列表
                                            empid_li = [k for k, v in dict(Counter(empid_li_s)).items() if v == 2]
                                        else:
                                            #[(员工ID, 技能值), (eid, skillnum)]
                                            empid_li_s,em_flag = get_empID(skillID, cid)#获取拥有该技能的员工id列表
                                            empid_li_c, em_flag_c = get_empID_c(certsname, cid)  # 获取拥有要求证书的员工id列表
                                            if (not em_flag) and (not em_flag_c):
                                                save_result = {'code': 101, 'result': 'DB操作失败'}
                                                return save_result
                                            empid_li_s.extend(empid_li_c)
                                            # 筛选出同时具备技能和证书的员工
                                            empid_li = [k for k, v in dict(Counter(empid_li_s)).items() if v == 2]
                                            empid_li.extend(emps_eid)
                                            # 从待排员工中筛选出同时具备技能和证书的员工列表
                                            empid_li = [k for k, v in dict(Counter(empid_li)).items() if v == 2]

                                        task_starttime = (i * timeInterval)/60# 任务块开始时间 7.5
                                        task_endtime = task_starttime + (timeInterval/60)#任务块结束时间,数字8.0
                                        #从优先级为1的规则开始一个个的检查，返回每个员工的匹配结果字典
                                        #emps_match = emp_matchPro(cid,did,empid_li,emp_matchpro,skillID,certsname,task_starttime,j,emp_pbwt,emp_pbsn)
                                        #从字典中比较结果，返回排序后的字典，排出员工的比较优先级
                                        #emp_order = sorted(emps_match.items(), key=cmp_to_key(dict_compare))
                                        #emps_order = emp_priority(emp_order)#员工eid优先级列表
                                        emps_available = []#最终该任务块的可用员工列表
                                        for eid in empid_li:
                                        #for eid in emps_order:#筛选出该时间段可用的员工
                                            #看该员工的special time 满不满足，0可排  1不可排
                                            t_flag = emp_special(eid, date, task_starttime, task_endtime,emps_notime)
                                            #看员工本身的可用性是否满足，0可排  1不可排
                                            a_flag = emp_time(eid,cid,date,task_starttime,task_endtime)
                                            #合规性校验后的不可用时间，进行检查
                                            h_flag = ckeck_time(emp_no_time, eid, task_starttime, task_endtime)
                                            if (t_flag == 0) and (a_flag == 0) and (h_flag == 0):
                                            #if (t_flag == 0) and (a_flag == 0):
                                                emps_available.append(eid)

                                        e_flag = 1 #默认该任务没有找到合适的实际员工
                                        #有可用员工
                                        if len(emps_available) != 0:
                                            now_score = {}#待选员工目前的分数
                                            e_score = {}#从待选中选出能排任务的员工的分数
                                            emps_available.sort(key=lambda x:int(x))
                                            for eid in emps_available:
                                                #先检查合规性，排上该任务后检查合规性，如果不符合则不能排
                                                # 该员工当天该时间段可用且未排任务，则可以尝试给该员工安排任务，排上后检查是否合规，不合规就不能排
                                                if emp_pb[eid][i] == 0:
                                                    temp_emp_pblist = copy.deepcopy(emp_pblist)  # 未排之前的是否排班情况
                                                    temp_emp_matchpro = copy.deepcopy(emp_matchpro)  # 未排之前当天的属性
                                                    temp_emp_pbsn = copy.deepcopy(emp_pbsn) #未排之前班次个数
                                                    temp_emp_pbwt = copy.deepcopy(emp_pbwt)
                                                    #该员工的属性字典对应属性随之改变
                                                    emp_pbwt[eid][j] += timeInterval#当天的日工时+=任务块工时，即时间粒度
                                                    emp_pblist[eid][j] = 1  # 该员工当天排工作了
                                                    if emp_matchpro[eid]['lasttask_endtime'] == 0:#该员工当天的第一个任务
                                                        emp_matchpro[eid]['interval'] = 100
                                                        emp_matchpro[eid]['lasttask_endtime'] = task_endtime  # 最新任务结束时间
                                                        emp_matchpro[eid]['now_shiftlen'] = timeInterval
                                                        emp_matchpro[eid]['taskid_set'].add(taskID)
                                                        emp_pbsn[eid][j] = 1
                                                    #上个任务结束时间等于这个任务的开始时间，即它们算一个班次里的
                                                    elif emp_matchpro[eid]['lasttask_endtime'] == task_starttime:
                                                        emp_matchpro[eid]['now_shiftlen'] += timeInterval
                                                        emp_matchpro[eid]['lasttask_endtime'] = task_endtime #最新任务结束时间
                                                        emp_matchpro[eid]['taskid_set'].add(taskID)
                                                    else:#跟之前的任务不是一个班次，是下一个新班次了
                                                        emp_pbsn[eid][j] += 1 #每天班次个数加1
                                                        emp_matchpro[eid]['now_shiftlen'] = timeInterval
                                                        emp_matchpro[eid]['interval'] = (task_starttime - emp_matchpro[eid]['lasttask_endtime'])*60#转为分钟
                                                        emp_matchpro[eid]['lasttask_endtime'] = task_endtime
                                                        emp_matchpro[eid]['taskid_set'].add(taskID)

                                                    now_score[eid] = copy.deepcopy(emps_score[eid])

                                                    # 获取该员工的合规性规则
                                                    if eid in eids_rule:
                                                        emp_rules = eids_rule[eid]
                                                        # 员工部分合规性检查
                                                        hg_flag,score = check_empcompliance(emp_rules,cid,eid,emp_matchpro,date,emp_pblist,start,end,emp_pbsn,emp_pbwt,now_score)
                                                        # 员工相同排班合规性检查
                                                        s_flag = check_samePB(eid, emps_res, date, emp_rules)
                                                    else:#该员工没有合规性，则表示该员工合规
                                                        hg_flag, score = 0, now_score[eid]
                                                        s_flag = 0  # 默认符合相同排班规则

                                                    #待排任务和员工现有任务的可组合性检查
                                                    c_flag = combineOrNot(taskType, eid, emp_matchpro, taskcombine_list, id_li)

                                                    #部门合规性检查(未完成)
                                                    #if (hg_flag == 1) or (c_flag == 1):
                                                    if (hg_flag == 1) or (c_flag == 1) or (s_flag == 1):#加上相同排班合规检查
                                                        #print('违反硬性规则，不可排')
                                                        #各规则恢复之前的值
                                                        emp_pblist = temp_emp_pblist
                                                        emp_matchpro = temp_emp_matchpro
                                                        emp_pbwt = temp_emp_pbwt
                                                        emp_pbsn = temp_emp_pbsn
                                                    else:
                                                        e_flag = 0
                                                        if against_softRule == 0:
                                                            emp_pb[eid][i] = taskID+'-'+taskType
                                                            emps_score[eid] = score
                                                            break
                                                        elif against_softRule == 1:#违反软约束最少
                                                            e_score[eid] = copy.deepcopy(score)
                                                            emps_score[eid] = copy.deepcopy(score)#把现在的分数再回传给员工分数集合

                                                else:#否则，该员工不可排，检查下一个
                                                    continue

                                        if (against_softRule == 1) and (e_flag == 0):#找到了合适的员工
                                            #print('e_score=',e_score)
                                            #将员工按分数倒序排序,选择分数最高的员工ID
                                            # emp_eid = sorted(e_score.items(),key=lambda x:x[1],reverse=True)[0][0]
                                            # emp_pb[emp_eid][i] = taskID+'-'+taskType

                                            softrule_num = {}  # {eid:num,...} 各员工违反软约束个数情况
                                            # print('e_score=',e_score)
                                            for key, v in e_score.items():
                                                softrule_num[key] = sum(v.values())
                                            # 将员工按违反软约束个数正序排序,选择最少的员工ID
                                            emp_eid = sorted(softrule_num.items(), key=lambda x: x[1])[0][0]
                                            emp_pb[emp_eid][i] = taskID + '-' + taskType


                                        if e_flag == 1:#如果在可用员工列表中没找到人，则增加一个虚拟eid
                                            if len(virtual_emp) == 0:#虚拟员工字典为空即还没有虚拟员工时
                                                xuni_eid = -1  # 任务找不到合适的员工时，虚拟eid
                                                virtual_emp[str(xuni_eid)] = [0 for i in range(all_tnum)]
                                                virtual_emp[str(xuni_eid)][i] = taskID+'-'+taskType
                                                virtual_emp_matchpro[str(xuni_eid)] = {}
                                                virtual_emp_matchpro[str(xuni_eid)]['interval'] = 100
                                                xuni_eid -= 1
                                            else:
                                                v_flag = 1#默认没找到合适的虚拟员工
                                                for k in sorted(virtual_emp):
                                                    vemp_taskid = set(i.split('-')[0] for i in virtual_emp[k] if i != 0)#每个员工目前已有的任务ID列表（不重复）
                                                    new_v = [i.split('-')[0] for i in virtual_emp[k] if i != 0]
                                                    v_worktime = (len(new_v)+1) * timeInterval #已有工作时长+排上这个任务后的总时长
                                                    if virtual_emp[k][i] == 0 and (v_worktime <= float(splitRule['worktime'][1])):#这个员工这个时段未排任务，且加上这个任务后的总工时没有超过工时限制
                                                        if i>0:
                                                            vc_flag = v_combineOrNot(taskType, vemp_taskid, taskID,
                                                                           taskcombine_list, id_li)
                                                            if vc_flag == 0:
                                                                virtual_emp[k][i] = taskID+'-'+taskType
                                                                v_flag = 0
                                                                break
                                                            else:
                                                                continue
                                                        else:#第一个任务，可直接排
                                                            virtual_emp[k][i] = taskID + '-' + taskType
                                                            v_flag = 0
                                                            break
                                                            # if taskType != 'indirectwh': #第一个任务，且不是间接任务，可直接排
                                                            #     virtual_emp[k][i] = taskID+'-'+taskType
                                                            #     v_flag = 0
                                                            #     break
                                                            # else:
                                                            #     continue
                                                    else:#查找下一个
                                                        continue
                                                #if v_flag == 1 and taskType != 'indirectwh':#没找到合适的虚拟员工，再虚拟个新的
                                                if v_flag == 1:
                                                    virtual_emp_matchpro[str(xuni_eid)] = {}
                                                    virtual_emp_matchpro[str(xuni_eid)]['interval'] = 100
                                                    virtual_emp[str(xuni_eid)] = [0 for i in range(all_tnum)]
                                                    virtual_emp[str(xuni_eid)][i] = taskID+'-'+taskType
                                                    xuni_eid -= 1

                                            #print('virtual_emp',virtual_emp)

                                        i += 1

                            # 统计当天的班次情况，1小时及以下的单个非固定任务舍弃
                            emps_dayshift,emp_pb = emp_dayshift(emp_pb, timeInterval)
                            emps_shifts[date] = emps_dayshift
                            print('emps_shifts old=', emps_shifts)

                            # emp_pb,emp_pbwt,emps_shifts,indirectTask_list = indirectTask(eids_rule, indirectTask_list, cid, did, emp_pb, emp_pblist, emp_pbwt,
                            #              emp_pbsn, j, emps_shifts, date,timeInterval, emps_score,emp_matchpro,all_tnum)
                            # print('emps_shifts new=', emps_shifts)
                            # print('实际员工填完，剩余间接工时=',indirectTask_list)
                            # emp_pb = realEmpTaskDrop(emp_pb)
                            # virtual_emp = indiretTask_virtualEmp(indirectTask_list, virtual_emp, all_tnum, timeInterval, splitRule)
                            # print('虚拟员工填完，剩余间接工时=', indirectTask_list)
                            # print('virtual_emp=', virtual_emp)
                            # print('虚拟员工数量 ',len(virtual_emp))
                            # virtual_emp = virtualEmpTaskDrop(virtual_emp)


                            final_pb = {}
                            final_pb.update(emp_pb)
                            final_pb.update(virtual_emp)
                            emps_res[date] = final_pb
                            print('每天最后的emps_score', emps_score)
                            print('emps_list=', emps_list)
                            for eid in emps_list:
                                if eid in eids_rule:  # 该员工有合规性
                                    emp_rules = eids_rule[eid]
                                    emp_zdbcNum = get_zdbc(eid, emp_rules, date, cid, did, emps_shifts)
                                    # 获取该员工的指定班次规则，若有该规则
                                    if len(emp_zdbcNum) != 0:  # 该员工有指定班次且是禁止的规则
                                        emp_no_time, flag = cheak_zdbc(emp_zdbcNum, emp_no_time, eid)
                                        if flag == 1:  # 已经达到规则数值了，第二天这个员工应该不再进行这个规则校验了
                                            emps_list.remove(eid)
                                    else:
                                        continue
                                else:
                                    continue

                    else:#获取任务排班矩阵的DB操作不成功
                        save_result = {'code': 101, 'result': '数据库中没有{}的任务排班'.format(date)}
                        print(save_result)
                        return save_result

                    e_t = datetime.now()
                    print('{}运行时间:{}'.format(date,(e_t-s_t).seconds))

            print('result.............')
            print('emps_res=',emps_res)
            print('最后emps_score=', emps_score)
            print('最后emp_pbwt=', emp_pbwt)
            print('最后emp_pbsn=', emp_pbsn)
            print('最后emp_pblist=', emp_pblist)
            out = jsonOut(emps_res, timeInterval, applyId)
            print('最后格式化输出',out)
            with open('./jsonout.txt','w') as f:
                f.write(str(out))

        #return out
        return emps_res,date_li

if __name__ == "__main__":
    raw_data={"cid":"123456","applyId":"76542","didArr":[6],"start":"2019-07-12","end":"2019-07-12","timeInterval":"30",
              "schType":"0","scheme":"worktime",
              "emps":[{"eid":"10","specialTime":[]},
                      {"eid":"88","specialTime":[]},
                      {"eid":"141","specialTime":[]},
                      {"eid":"256","specialTime":[]},
                      {"eid":"369","specialTime":[]},
                      {"eid":"633","specialTime":[]},
                      {"eid":"677","specialTime":[]},
                      {"eid":"680","specialTime":[]},
                      {"eid":"730","specialTime":[]},
                      {"eid":"732","specialTime":[]},
                      {"eid":"791","specialTime":[]},
                      {"eid":"12","specialTime":[]},
                      {"eid":"13","specialTime":[]},
                      {"eid":"15","specialTime":[]},
                      {"eid":"32","specialTime":[]},
                      {"eid":"341","specialTime":[]},
                      {"eid":"342","specialTime":[]},
                      {"eid":"351","specialTime":[]},
                      {"eid":"55","specialTime":[]},
                      {"eid":"556","specialTime":[]},
                      {"eid":"557","specialTime":[]},
                      {"eid":"558","specialTime":[]},
                      {"eid":"626","specialTime":[]},
                      {"eid":"669","specialTime":[]},
                      {"eid":"7","specialTime":[]},
                      {"eid":"774419","specialTime":[]},
                      {"eid":"774431","specialTime":[]},
                      {"eid":"774433","specialTime":[]},
                      {"eid":"774435","specialTime":[]},
                      {"eid":"774436","specialTime":[]},
                      {"eid":"774438","specialTime":[]},
                      {"eid":"774440","specialTime":[]},
                      {"eid":"774445","specialTime":[]},
                      {"eid":"774448","specialTime":[]},
                      {"eid":"774449","specialTime":[]},
                      {"eid":"774451","specialTime":[]},
                      {"eid":"774452","specialTime":[]},
                      {"eid":"774454","specialTime":[]},
                      {"eid":"774455","specialTime":[]},
                      {"eid":"774456","specialTime":[]},
                      {"eid":"774480","specialTime":[]},
                      {"eid":"8","specialTime":[]},
                      {"eid":"9","specialTime":[]}]}
    now = datetime.now()
    emp_pb,date_li = PBResultService().PaiBanResult(raw_data)
    end = datetime.now()
    print('运行时间：',(end-now).seconds)
    for date in date_li:
        import pandas as pd
        data = list(emp_pb[date].values())
        key = list(emp_pb[date].keys())
        res = pd.DataFrame(data=data,index=key)
        res.to_csv(('./{}_same.csv').format(date),encoding='utf-8')
