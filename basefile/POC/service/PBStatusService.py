"""
by shenzihan
阶段四接口6-获取排班状态
2019-11-14
"""
import random
from typing import Dict, List, Set, Tuple
from POC.service.PBResultService_l import PBResultService_L
from utils.dateTimeProcess import DateTimeProcess
from POC.model.status_db import StatusDB
from POC.model.forecast_task_DB import ForecastTaskDB
import time, datetime
from tornado import gen, web
import threading
from utils.md5Token import Token
import requests, json
from utils.myLogger import infoLog
#from laborCnt.service.manpower_forecast_service import ManPowerForecastService
from laborCnt.service.manpower_forecast_service2 import ManPowerForecastService
import requests
from urllib.request import Request
from urllib.request import urlopen
from POC.bean.LaborTask import LaborTask
from POC.service.CombTaskService import CombTaskService
from POC.bean.EmpComplianceRule import EmpComplianceRule
from POC.service.EmpRecordsService import EmpRecordsService
from utils.dateTimeProcess import DateTimeProcess
import math

class PBStatusService:
    cal = []
    status = 'running'

    @staticmethod
    @gen.coroutine
    def doRequest(raw_data: Dict):
        status = 'running'
        cal = []
        save_result = {'code': 0, 'result': '未处理', 'data': None}
        flag = 1  # 是否运行排班算法的标识:若为1则不需运行，可直接返回结果;若为0则需要运行，才能返回结果
        calDate = []  # 记录排班日期
        start = raw_data.get('start', '1990-01-01').strip()
        end = raw_data.get('end', '1990-01-01').strip()

        # 是否重复计算 True重复计算   False第一次计算
        recalculation = raw_data.get('recalculation', False)

        forecast_days = DateTimeProcess.date_interval(start_day=start, end_day=end)  # 获取排班日期
        print('forecast_days : ', forecast_days)
        applyId = raw_data['applyId']
        cid = raw_data['cid']

        scheme = raw_data.get('scheme', '')
        schType = raw_data.get('schType', '0')
        accessToken = raw_data.get('accessToken', '')
        callbackUrl = raw_data.get('callbackUrl', '')

        # 清除数据库记录
        emps = raw_data.get('emps')
        for item in emps:
            eid = item.get('eid')
            StatusDB.delete_by_cid_eid_day(applyId=applyId, scheme=scheme, forecast_date_s=start, forecast_date_e=end,cid=cid, eid=eid)
            for forecast_day in forecast_days:
                flag = ForecastTaskDB.prePcrocess_empAvailable(cid, eid, forecast_day) #插入可用性

        # 删除数据库记录，并重新计算
        if ( recalculation is True or recalculation == 1):
            print('recalculation 重新计算')
            flag = 0
        # 导致查不到结果
        elif recalculation is False:
            StatusDB.delete_by_recalculation_is_False(applyId=applyId)

        schedule_status: Tuple = StatusDB.read_schedule_status(applyId=applyId, start=start, end=end, scheme=scheme)
        print('schedule_status=',schedule_status)
        status_list = []
        if schedule_status is not None:
            for item in schedule_status:
                # [applyId,status,date]
                applyId = item[0]
                status = item[1]
                date = item[2]
                status_list.append("%s_%s_%s_%s" % (applyId, status, date, scheme))

        for day in forecast_days:
            check_day_s = "%s_%s_%s_%s" % (applyId, 'success', day, scheme)
            check_day_r = "%s_%s_%s_%s" % (applyId, 'running', day, scheme)
            if check_day_s not in status_list and check_day_r not in status_list:
                flag = 0
                calDate.append(day)  ######记录未排班的日期
        print('calDate ', calDate)

        dayfull = False
        if flag == 1 or (recalculation is False and len(schedule_status) >= 1):
            print('直接读取数据库')
            cal = PBStatusService.get_from_db(applyId, scheme)

            if len(schedule_status) % len(forecast_days) == 0:
                dayfull = True

        elif len(schedule_status) < 1:
            print('重新计算')
            f = PBStatusService()
            t = threading.Thread(target=PBStatusService.calc,
                                 args=(raw_data, calDate, applyId, scheme, cid, accessToken, schType, callbackUrl))
            t.start()
            dayfull = PBStatusService.isdayfull(applyId, start, end, scheme, forecast_days)

            if dayfull:
                cal = PBStatusService.get_from_db(applyId, scheme)
            else:
                cal = f.cal

        save_result['code'] = 100
        save_result['result'] = '成功'
        save_result["data"] = {
            "schemes": [
                {scheme: ""}
            ],
            "applyId": applyId,
            "status": 'success' if dayfull else 'running',
            "describe": '排班成功，返回结果' if dayfull else '运行中...',
            "cal": cal if dayfull else []
        }

        print(save_result)
        raise gen.Return(save_result)

    @classmethod
    def isdayfull(cls, applyId, start, end, scheme, forecast_days):
        flag = False
        """
        for a in cal:
            if a['schDay'] in forecast_days:
                forecast_days.remove(a['schDay'])
        if len(forecast_days)==0:
            flag=True
        """
        schedule_status: Tuple = StatusDB.read_schedule_status(applyId=applyId, start=start, end=end, scheme=scheme)
        if schedule_status is not None:
            for item in schedule_status:
                status = item[1]
                date = item[2]
                if status == 'success' and date in forecast_days:
                    forecast_days.remove(date)

        if len(forecast_days) == 0:
            flag = True
        return flag

    @classmethod
    def get_from_db(cls, applyId, scheme):
        """
        :param applyId， 根据applyId、scheme从数据库获取数据
        :param scheme
        :return:
        """
        cal = []
        paiban_data: Tuple = StatusDB.read_schedule_data(applyId, scheme)
        cal_ = {}
        for item in paiban_data:
            applyId = item[0]
            cid = item[1]
            eid = item[2]
            schDay = item[3]
            allWorkTime = item[4]
            type = item[5]
            outId = item[6]
            shiftId = item[7]
            startTime = DateTimeProcess.timedelta_to_timeStr(forecast_day=schDay,obj=item[8])
            endTime = DateTimeProcess.timedelta_to_timeStr(forecast_day=schDay,obj=item[9])
            workTime = item[10]

            cal_key = "%s_%s" % (eid, schDay)
            if cal_key not in cal_.keys():
                cal_[cal_key] = []
            eid_unit = {
                "type": type,
                "outId": outId,
                "shiftId": shiftId,
                "startTime": startTime,
                "endTime": endTime,
                "workTime": int(workTime)
            }
            cal_[cal_key].append(eid_unit)
        for c, v in cal_.items():
            eid, schDay = c.split('_')
            allWorkTime = 0
            for i in v:
                allWorkTime += i['workTime']
            cal.append(
                {
                    "eid": eid,
                    "schDay": schDay,
                    "allWorkTime": allWorkTime,
                    "workUnit": v
                }
            )
        return cal

    @classmethod
    def randomRest(cls,not_last_day_at_circle,empSize,d,shouldSize,pbDay_restnums):
        #返回排班周期内每一天应该随机休息的人数[3,n,n,n,n,0,0] 假设周期是7天
        '''
        if d in circles_index:#属于规则周期的第一天
            pbDay_restnums[d] = 1
        elif not not_last_day_at_circle:
            pbDay_restnums[d] = 1
        else:
            if (d-1) in circles_index: #规则周期的第二天到规则周期的最后一天
                N = pbDay_realnums[d-1] + 1
                rest_nums = int(N / (base-3))  # 除最后2天外每天随机休息的人数
                rest_nums_list = [rest_nums for i in range(base-3)] #[rn,rn,rn,rn]

                rest_nums2 = N % (base-3)  # 剩余未被随机休息的人数，他们也应该被随机休息，因此把他们随机插入待排日期中
                rest_inx = [i for i in range(base-3)]  #
                days_index = random.sample(rest_inx, rest_nums2)
                for i in days_index:
                    rest_nums_list[i] += 1

                pbDay_restnums[d:(d+base-3)] = rest_nums_list

                pbDay_restnums[(d+base-3):(d+base)] = [3,3,2] #周六周日

        print('pbDay_restnums',pbDay_restnums)
        '''
        rest=round(empSize/shouldSize)*(math.ceil(shouldSize/4))
        pbDay_restnums=[rest for i in range(len(pbDay_restnums))]
        if not not_last_day_at_circle:
            pbDay_restnums[d] = 1
        print('shouldSize,empSize,round(empSize/shouldSize),math.ceil(shouldSize/4),pbDay_restnums',shouldSize,empSize,round(empSize/shouldSize),math.ceil(shouldSize/4),pbDay_restnums)
        return pbDay_restnums

    @classmethod
    def get_rest_emps_init(cls,cid,emps):
        '''
        构造一个员工休息返回列表
        :return:
        '''

        # 随机人员休息逻辑，有连续排班规则才执行

        rule_bid_eid = {'-': []}  # 默认无规则的员工的规则bid为'-'

        for e in emps:
            if e['legalityBidArr'] == []:
                rule_bid_eid['-'].append(e.get('eid', ''))
            elif e['legalityBidArr'][0] not in rule_bid_eid.keys():
                rule_bid_eid[e['legalityBidArr'][0]] = [e.get('eid', '')]
            else:
                rule_bid_eid[e['legalityBidArr'][0]].append(e.get('eid', ''))

        base=99
        r_starttime='1990-01-01'
        lxpb_num, eids_list = {}, []  # eids_list:有连续排班规则的员工eid列表
        for bid in rule_bid_eid.keys():
            if bid != '-':
                nums,r_startDate = ForecastTaskDB.read_lxpb_rule(cid, bid)  #连续排班天数和规则开始有效时间
                r_startDate=r_startDate.strftime('%Y-%m-%d')
                if nums != -1:  # 有连续排班规则的员工加入列表
                    eids_list.extend(rule_bid_eid[bid])
                    lxpb_num[bid] = nums
                    base=min(int(nums),base)
                    r_starttime=max(r_starttime,r_startDate)
        eid_set = set(eids_list)
        return eid_set,base,r_starttime

    @classmethod
    def get_rest_emps_day(cls,day,r_starttime,eid_set,restEid_history,circles_index,pbDay_restnums,base,d,pbDay_realnums,empSize,shouldSize):
        now_restEid_list = []
        # 随机选择两个员工休息，已休息过的员工不能再休息
        eids = eid_set - restEid_history  # 还未随机休息过的eid集合
        not_last_day_at_circle=True
        if int((int(time.mktime(time.strptime(day, '%Y-%m-%d'))) - int(time.mktime(time.strptime(r_starttime, '%Y-%m-%d')))) / (24 * 60 * 60)+1)%7 ==0:
            not_last_day_at_circle=False

        print('day,r_starttime,not_last_day_at_circle',day,r_starttime,not_last_day_at_circle)
        if eid_set:  # 有连续排班天数规则
            if d in circles_index:
                eids = eid_set
                restEid_history = set()
            pbDay_restnums = PBStatusService.randomRest(not_last_day_at_circle,empSize,d,shouldSize,pbDay_restnums)
            # 如果是周期的第0天 取pbDay_restnums[0]
            if not_last_day_at_circle:
                if len(eids) >= pbDay_restnums[d]:  # 如果剩余人数大于理应随机休息的人数
                    for eid in random.sample(eids, pbDay_restnums[d]):
                        now_restEid_list.append(eid)
                        restEid_history.add(eid)
                elif len(eids) < pbDay_restnums[d] and len(eids) > 0:  # 则直接令其休息
                    now_restEid_list.extend(eids)
                    restEid_history = restEid_history | eids
        return eid_set,restEid_history,circles_index,pbDay_restnums,base,d,now_restEid_list,pbDay_realnums


    @classmethod
    def calc(cls, raw_data, calDate, applyId, scheme, cid, accessToken, schType, callbackUrl):


        # 算法依赖（wtForecast(劳动工时预测数据)，mpForecast（第三阶段人数预测数据来源依赖））
        calRelyon = raw_data.get('calRelyon', 'wtForecast')

        # 如果使用劳动工时预测，则为None,需要在算法中自行读取。
        third_rules = None

        if calRelyon == 'wtForecast':
            infoLog.info('-------------------calRelyon == wtForecast 开始 生成第三阶段结果矩阵-----------------------')
            # 请求第三阶段，生成排班结果矩阵
            third_rules = PBStatusService.sent_post_request(raw_data)
            infoLog.info('-------------------calRelyon == wtForecast 结束 生成第三阶段结果矩阵-----------------------')
        cr = []
        rr = {"scheduledNum":0,"notScheduledNum":0,"reasonList":[]}
        # 用于计算进度条的百分比
        all_forecast_days = calDate
        quotient_set = set()
        emps: List = raw_data['emps']
        d = 0
        eid_set,base,r_starttime=PBStatusService.get_rest_emps_init( cid, emps)
        circles_index  = [i for i in range(0,int(len(calDate)/(base+1))*(base+1),(base+1))]
        pbDay_restnums =  [0 for i in range(len(calDate))] #
        pbDay_realnums = [0 for i in range(len(calDate))]
        restEid_history= set()

        empSize=len(emps)
        shouldSize=18
        for day in calDate:
            eid_set, restEid_history, circles_index, pbDay_restnums, base, d,now_restEid_list,pbDay_realnums=PBStatusService.get_rest_emps_day(day,r_starttime,eid_set, restEid_history, circles_index, pbDay_restnums, base, d,pbDay_realnums,empSize,shouldSize)
            print(' 开始处理日期：%s' %(day))
            print('now_restEid_list',now_restEid_list,'pbDay_restnums',pbDay_restnums)

            StatusDB.del_schedule_applyId(applyId, day, scheme)  # 删除状态表
            StatusDB.insert_schedule_status(applyId, day, scheme)  # 逐天 插入状态表,状态置为running

            raw_data['start'] = day
            raw_data['end'] = day

            # 排班类型（任务排班：0、岗位排班：1、组织排班：2）
            schType = str(raw_data.get('schType', "0"))
            # 获取排班方案
            scheme = raw_data["scheme"]

            cid = str(raw_data.get('cid', "123456"))
            didArr: List = raw_data.get('didArr', [6])
            applyId = str(raw_data.get('applyId', '-1'))
            timeSize = int(raw_data.get('timeInterval', 15))
            start = raw_data.get('start', '1990-01-01')
            end = raw_data.get('end', '1990-01-01')
            # 合规性部门规则bids
            legalityBids = raw_data.get("legalityBids", [])

            # 匹配属性
            emp_matchpro: Tuple = ForecastTaskDB.read_emp_matchpro(cid=cid, did=str(didArr[0]))

            # 任务详情
            task_all_info = LaborTask.get_laborTask_all_info(cid=cid, did=str(didArr[0]))

            # 第三阶段 拆分规则
            shift_split_rule_info = ForecastTaskDB.read_labor_shift_split_rule(cid=cid, did=str(didArr[0]))

            # 第三阶段 组合规则
            comb_rule_info: Tuple = ForecastTaskDB.read_comb_rule(cid=cid, did=str(didArr[0]))

            # 第三阶段班次数据
            shiftData = CombTaskService.task_to_shift2(cid=cid, did=str(didArr[0]), start_date=start, end_date=end,
                                                       task_all_info=task_all_info, schType=schType, scheme=scheme,
                                                       timeSize=timeSize)

            # 合规性
            emp_rule_dict = EmpComplianceRule.create_rule_file_new(cid=cid)


            # 存储所有员工工作记录
            employee_records = EmpRecordsService.package_emp_record(cid=cid, emps=emps, forecastDate=start,
                                                                    emp_rule_dict=emp_rule_dict,
                                                                    applyId=applyId,scheme_type=scheme,
                                                                    legalityBids=legalityBids)
            #排班回调
            accessToken = raw_data.get('accessToken', '')
            callbackProgressUrl = raw_data.get('callbackProgressUrl', '')
            callbackData = {"accessToken": accessToken, "applyId": applyId, "cid": cid, "did": didArr[0],"callbackProgressUrl": callbackProgressUrl}


            # 获取该公司当天可用的全部员工
            emp_info_tuple = ForecastTaskDB.read_emp_info(cid, day)

            return_data,pbDay_realnums,return_reason = PBResultService_L.task_schType(raw_data, third_rules, all_forecast_days, quotient_set,
                                                         employee_records,task_all_info, comb_rule_info, shift_split_rule_info,
                                                         emp_info_tuple, callbackData, shiftData, legalityBids,
                                                         emp_matchpro, emps, emp_rule_dict,now_restEid_list,pbDay_realnums,d)  # 调用当前天day，计算出结果


            StatusDB.save_result(cid, return_data, scheme, scheme, day)  # 存入结果表
            StatusDB.update_schedule_status(applyId, day, scheme)  # 更新状态表，设置为success
            cr = cr + return_data['cal']

            rr["scheduledNum"] += return_reason["scheduledNum"]
            rr["notScheduledNum"] += return_reason["notScheduledNum"]
            rr["reasonList"] = rr["reasonList"] + return_reason["reasonList"]

            cls.cal = cls.cal + return_data['cal']
            d += 1
        cls.status = 'success'
        result = {"accessToken": accessToken, "applyId": applyId, "cid": cid, "schType": schType, "scheduledNum":rr['scheduledNum'],"notScheduledNum":rr['notScheduledNum'],"reasonList":rr["reasonList"],"empList": cr}
        print("result=",result)

        PBStatusService.view_result(result)

        # 排班进度条回调
        callbackProgressUrl = raw_data.get('callbackProgressUrl', '')
        didArr: List = raw_data.get('didArr', [6])

        if "http://" in callbackProgressUrl or "https://" in callbackProgressUrl:
            callbackProgressUrl = callbackProgressUrl
        else:
            callbackProgressUrl = "http://" + callbackProgressUrl

        callbackData = {"accessToken": accessToken, "applyId": applyId, "cid": cid, "did": didArr[0],
                        "callbackProgressUrl": callbackProgressUrl, "percentage": 100.00}

        infoLog.info('排班进度回调：%d' % 100.00)

        headers = {'content-type': 'application/json'}

        json.dumps(callbackData).encode('utf-8')
        response = requests.post(url=callbackProgressUrl, json=callbackData, headers=headers)
        html_code = response.status_code
        print('排班进度回调接口喔趣返回：{}'.format(html_code))
        infoLog.info('排班进度回调接口喔趣返回：{}'.format(html_code))
        print('排班进度回调接口喔趣返回数据：{}'.format(response.text))
        infoLog.info('排班进度回调接口喔趣返回数据：{}'.format(response.text))


        # 排班结果回调
        if "http://" in callbackUrl or "https://" in callbackUrl:
            callbackUrl = callbackUrl
        else:
            callbackUrl = "http://" + callbackUrl

        infoLog.info('回调接口喔趣返回：%s' % result)


        result = json.dumps(result)
        post_data = result.encode('utf-8')
        headers = {'content-type': 'application/json'}
        request_obj = Request(url=callbackUrl, data=post_data, headers=headers)
        response_obj = urlopen(request_obj)
        html_code = response_obj.read().decode('utf-8')
        print('回调接口喔趣返回：{}'.format(html_code))
        infoLog.info('回调接口喔趣返回：{}'.format(html_code))




    @staticmethod
    def sent_post_request(raw_data: Dict) -> Dict:
        '''
        发送请求并返回状态码
        100 成功
        :param raw_data:
        :return:
        '''
        a = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        b = Token().getToken(a)

        cid = raw_data.get('cid', '123456')
        didArr = raw_data.get('didArr', [6])
        forecastType = raw_data.get('schType', '0')
        forecastDateStart = raw_data.get('start', '1990-01-01').strip()
        forecastDateEnd = raw_data.get('end', '1990-01-01').strip()
        timeInterval = raw_data.get('timeInterval', 30)
        #fill_coef: float = raw_data.get('fill_coef', 0.8)
        #reserve_fixed_wh: bool = raw_data.get('reserve_fixed_wh', False)

        comb_rule_list: List = ForecastTaskDB.read_comb_rule_to_list(cid=cid, did=didArr[0])
        shift_split_rule_list: List = ForecastTaskDB.read_labor_shift_split_rule_to_list(cid=cid, did=didArr[0])
        shift_mod_list: List = ForecastTaskDB.read_shift_mod_to_list(cid=cid, did=didArr[0])

        data = {"token": b,
                "timestr": a,
                "cid": cid,
                "didArr": didArr,
                "forecastType": forecastType,
                "forecastDateStart": forecastDateStart,
                "forecastDateEnd": forecastDateEnd,
                "timeInterval": timeInterval,
                "shift_mod_list": shift_mod_list,
                "combirule": comb_rule_list,
                "shiftsplitrule": shift_split_rule_list,
                }

        print('第三阶段请求参数为：%s' % json.dumps(data))

        result = ManPowerForecastService.manpower_forecast(cid=cid, bid=forecastType,
                                                           time_interval=timeInterval,
                                                            did_arr=didArr, forecast_date_start=forecastDateStart,
                                                            forecast_date_end=forecastDateEnd,
                                                            shift_mod=shift_mod_list, combi_rule=comb_rule_list,
                                                            shiftsplitrule=shift_split_rule_list)
        #print('直接请求第四阶段，需要程序执行第三阶段，返回的结果为：%s' % result)
        infoLog.info('ch为：%s' % result)

        return {'comb_rule_list':comb_rule_list,'shift_split_rule_list':shift_split_rule_list,'shift_mod_list':shift_mod_list}


    @staticmethod
    def view_result(result: Dict):
        for r in result['reasonList']:
            #print(result['applyId'], r['day'], r['eid'], r['reason'])
            pass
        for k in result['empList']:
            isin = False
            for x in k['workUnit']:
                #if x['outId'] in ['2020063014184801814043b460000721', '2020063014184848614043b460000733','2020063014185381514043b460000805', '20200630141852091140439cc0000803']:
                isin = True
            if int(k['eid'])<0:
                isin = False
            if isin:
                pass
                #print(result['applyId'],k['schDay'], k['eid'], k['allWorkTime'])


if __name__ == '__main__':
    raw_data ={"scheme":"fillRate","emps":[{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"109160","hireType":"full","specialTime":[]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"109287","hireType":"full","specialTime":[]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"109530","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"109695","hireType":"full","specialTime":[]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"109858","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"110419","hireType":"full","specialTime":[]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"110534","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"110566","hireType":"full","specialTime":[]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"110670","hireType":"full","specialTime":[]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"110759","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"110796","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"110970","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"110995","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"111233","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"111284","hireType":"full","specialTime":[]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"111378","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"111413","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"112195","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"112924","hireType":"full","specialTime":[]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"113768","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"114146","hireType":"full","specialTime":[]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"114383","hireType":"full","specialTime":[]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"114437","hireType":"full","specialTime":[]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"114812","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"115140","hireType":"full","specialTime":[{"startTime":"2020-09-06 16:00","endTime":"2020-09-07 00:00"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"115316","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"116466","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"116562","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"116941","hireType":"full","specialTime":[{"startTime":"2020-09-06 00:00","endTime":"2020-09-07 00:00"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"116976","hireType":"full","specialTime":[]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"117133","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"117185","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"118169","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"119179","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"119180","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"253908","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"253980","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"254032","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"254372","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"254399","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"254455","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"254456","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"254721","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"254878","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"255012","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"255483","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"255534","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"255535","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"255579","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"255580","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"255837","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"256028","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"256199","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"256328","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"256332","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"257113","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"257122","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"257440","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"257495","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"257819","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"257904","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"258217","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"258256","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"258430","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"258733","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"258798","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"258810","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"259177","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"259178","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"259623","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"259624","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"260180","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"260240","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"260506","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"260978","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"261264","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"262242","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"262375","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"262393","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"262422","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"262437","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"262831","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"262879","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"263073","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"263250","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"263264","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"264017","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"264059","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"264120","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"264197","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"264449","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"265060","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"265061","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"265209","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"265237","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"265256","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"265748","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"265799","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"265972","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"266020","hireType":"full","specialTime":[{"startTime":"2020-09-06 00:00","endTime":"2020-09-07 00:00"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"266136","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"266224","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"266234","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"266236","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"266282","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"266387","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"266404","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"266538","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"266791","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"266863","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"266977","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"266978","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"267111","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"267114","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"267295","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"267321","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"267696","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"267990","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"267991","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"268089","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"268364","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"268495","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"269421","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"269442","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"269633","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"270067","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"270092","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"270098","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"270609","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"270678","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"270901","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"271106","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"271191","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"271192","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"271319","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"271334","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"271544","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"271686","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"272059","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"272255","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"272442","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"272630","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"272645","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"272646","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"272702","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"273140","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"273163","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"273178","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"300915","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":[],"eid":"307133","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"366648","hireType":"part","specialTime":[]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"463876","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"480112","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"624037","hireType":"part","specialTime":[]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"624038","hireType":"part","specialTime":[]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"640608","hireType":"full","specialTime":[]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"651890","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"651891","hireType":"part","specialTime":[]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"660505","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"660762","hireType":"full","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160726722141339a80000023"],"eid":"684477","hireType":"part","specialTime":[{"startTime":"2020-09-07 00:00","endTime":"2020-09-13 23:59"}]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"872284","hireType":"full","specialTime":[]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"872285","hireType":"full","specialTime":[]},{"legalityBidArr":["20200727160343631141339a80000010"],"eid":"904538","hireType":"full","specialTime":[]}],"legalityBids":[],"start":"2020-09-07","bizStartTime":"07:00","timestr":"2020-09-03 23:06:07.003","accessToken":"D95D6E02CA97B478F3D8D207ED326548","token":"45d401868f85bd46677ac83bf8740f84","recalculation":False,"schType":"0","applyId":"20200903230606913030139930000065","callbackProgressUrl":"https://hrec.woqu365.com/forward_webfront/api/schedule-didi/sch/monitor/progress/callback?cod=UkwmlS5zuQ31bPYzQTzpHQ","calRelyon":"wtForecast1","didArr":[6508],"timeInterval":"30","end":"2020-09-13","callbackUrl":"https://hrec.woqu365.com/forward_webfront/api/schedule-didi/sch/cal/callback?cod=UkwmlS5zuQ31bPYzQTzpHQ","cid":60000039,"bizEndTime":"00:00"}
    a = PBStatusService.doRequest(raw_data)




