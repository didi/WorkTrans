'''
create by liyabin
'''

from typing import Dict,List,Tuple
import json
from utils.dateTimeProcess import DateTimeProcess
from POC.model.forecast_task_DB import ForecastTaskDB
from utils.task import DirectTask, InDirectTask, FixedTask
import datetime
from laborCnt.service.manpower_forecast_service2 import ManPowerForecastService
from POC.service.CombTaskService import CombTaskService
from utils.myLogger import infoLog

class CombTasks:
    def __init__(self,shiftId,cid:str,did:str,work_date:str,taskCombination:str,
                 combinationVal:str,taskId:list,taskName_list:list,taskSkillBid_list:List,skillNum_list:List,cert_list:List,
                 taskType:list,start:list,end:list,
                 worktimeList:list,employees:list,worktime_minutes:int):
        self.shiftId = shiftId
        self.cid = cid
        self.did = did
        self.work_date = work_date
        self.taskCombination = taskCombination
        self.combinationVal = combinationVal
        self.taskId = taskId
        self.taskName_list = taskName_list
        self.taskSkillBid_list = taskSkillBid_list
        self.skillNum_list = skillNum_list
        self.cert_list = cert_list
        self.taskType = taskType
        self.start = start
        self.end = end
        self.worktimeList = worktimeList
        self.employees = employees
        self.worktime_minutes:int = worktime_minutes
        # 用于排班统计
        self.done = False

    def scheduling_completed(self):
        self.done = True

    def set_worktimeList(self,worktimeList:List):
        self.worktimeList = worktimeList

    @staticmethod
    def get_comb_tasks_info(data: Dict,forecast_day:str,task_all_info:Dict,timeSize:int) -> List:
        '''
        获取工作组合列表
        :param data: shiftData 班次数据
        :param forecast_day:
        :param timeSize: 时间粒度
        :return:
        '''


        # 返回结果
        comb_tasks_list = []

        cid = data.get("cid")
        did = str(data.get("did"))

        forecast = data.get('ssData', '').get("manpowers")
        for item in forecast:
            for key in item.keys():
                # 日期
                date = key

                if(date != forecast_day): continue
                # 任务集合：人数
                shift_info = item[date]

                num = 1
                for item2 in shift_info:
                    '''
                    {
                    "taskCombination":"2020063014185381514043b460000805,2020063014194935414043b460000838,2020063014195031414043b460000847,20200630141851096140439cc0000787",
                    "value":1,
                    "scope":[
                        0,
                        1
                    ],
                    "detail":[
                        {
                            "taskId":"2020063014194935414043b460000838",
                            "taskType":"directwh",
                            "start":"20:00",
                            "end":"20:30"
                        },
                        {
                            "taskId":"2020063014195031414043b460000847",
                            "taskType":"directwh",
                            "start":"20:30",
                            "end":"22:00"
                        },
                        {
                            "taskId":"2020063014185381514043b460000805",
                            "taskType":"directwh",
                            "start":"22:00",
                            "end":"22:30"
                        },
                        {
                            "taskId":"20200630141851096140439cc0000787",
                            "taskType":"fixedwh",
                            "start":"22:30",
                            "end":"23:00"
                        }
                    ]
                    }
                    '''

                    # 喜茶吃饭任务bid
                    eat_food_dict = {}
                    eat_time_list = []

                    # 任务集合
                    taskCombination = item2["taskCombination"]
                    # 人数
                    combinationVal = item2["combinationVal"]
                    detail = item2['detail']

                    taskId_list = []
                    # 存任务名称考虑时间粒度，重复存取同一个任务名称为了对应打印的输出
                    taskName_list = []
                    taskSkillBid_list = []
                    skillNum_list = []
                    cert_list = []
                    taskType_list = []
                    start_list = []
                    end_list = []
                    # 存储时间 [05:00-06:00]
                    worktime_list = []
                    for item3 in detail:
                        # 单个任务
                        taskId = item3.get('taskId','')
                        # taskBid:[taskName,taskSKillBid]
                        # taskBid:[taskName,taskSkillBids,skillNums,certs]
                        taskName = task_all_info.get(taskId,{}).get("taskName","")
                        taskSkillBids = task_all_info.get(taskId,{}).get("taskSkillBids",'').split(",")
                        skillNums = task_all_info.get(taskId,{}).get("skillNums",'0').split(",")
                        certs = task_all_info.get(taskId,{}).get("certs","").split(",")
                        # 类型
                        taskType = item3.get('taskType','')

                        # 开始结束时间
                        start = item3['start']
                        end = item3['end']

                        if taskId == 'break':
                            if taskName == "":
                                taskName = '吃饭'
                                taskSkillBids = ['break']
                            eat_time_list.append(start + "-" + end)

                        # if(start< "08:00" or end > "22:00"):
                        #     continue
                        taskId_list.append(taskId)
                        taskName_num = DateTimeProcess.worktime_interval(start_time=start,end_time=end,timeSize=timeSize) // timeSize
                        for _ in range(taskName_num):
                            taskName_list.append(taskName)

                        taskSkillBid_list.extend(taskSkillBids)
                        skillNum_list.extend(skillNums)
                        cert_list.extend(certs)
                        taskType_list.append(taskType)
                        start_list.append(start)
                        end_list.append(end)
                        worktime_list.append(start+"-"+end)

                        # 记录吃饭
                        # if taskName == '吃饭':
                        #     eat_time_list.append(start + "-" + end)

                    # 给员工添加间接任务的技能
                    if not taskId_list: continue

                    # 转换成离散时间列表
                    worktime_list = DateTimeProcess.timeStr_to_timeList(timeStrList=worktime_list,timeSize=timeSize)
                    comb_tasks = CombTasks(shiftId=str(num),cid=cid, did=did, work_date=date,
                                           taskCombination=taskCombination, combinationVal=combinationVal,
                                           taskId=taskId_list,taskName_list=taskName_list,taskSkillBid_list=taskSkillBid_list,
                                           skillNum_list=skillNum_list,cert_list=cert_list,taskType=taskType_list,
                                           start=start_list, end=end_list,worktimeList=[],employees=["缺人"],worktime_minutes=0)

                    comb_tasks.set_worktimeList(worktime_list) #

                    # 计算工时
                    if cid != '60000039':#除喜茶外其余的吃饭任务不算工时
                        comb_tasks.calc_worktime_for_eatFood(timeSize=timeSize, eat_time_list=eat_time_list)
                    else: #喜茶的吃饭任务也算工时
                        comb_tasks.calc_worktime(timeSize=timeSize)


                    #comb_tasks.calc_worktime_for_eatFood(timeSize=timeSize, eat_time_list=eat_time_list)

                    # 键： cid-did-任务组合 ： comb_tasks对象
                    comb_tasks_list.append(comb_tasks)
                    #print('comb_tasks_list=',comb_tasks_list)
                    num += 1

        return comb_tasks_list

    def calc_worktime(self,timeSize:int):
        minutes = 0
        for i in range(len(self.start)):
            temp = DateTimeProcess.worktime_interval(start_time=self.start[i],end_time=self.end[i],timeSize=timeSize)
            minutes += temp
        self.worktime_minutes = minutes

    def calc_worktime_for_eatFood(self,timeSize:int,eat_time_list:List):
        minutes = 0
        for i in range(len(self.start)):
            temp = DateTimeProcess.worktime_interval(start_time=self.start[i],end_time=self.end[i],timeSize=timeSize)
            minutes += temp
        eattime = 0
        for eat_time in eat_time_list:
            s = eat_time.split('-')[0]
            e = eat_time.split('-')[1]
            start_time = datetime.datetime.strptime(s, "%H:%M")

            if e == '24:00' or e == '00:00':
                end_time = datetime.datetime.strptime("23:59:59", "%H:%M:%S")
                temp_ = int((end_time - start_time).total_seconds()) // 60 + 1
            else:
                end_time = datetime.datetime.strptime(e, "%H:%M")
                temp_ = int((end_time - start_time).total_seconds()) // 60

            eattime += temp_

        self.worktime_minutes = minutes - eattime

    @staticmethod
    def get_task_name_and_skill(cid:str):
        task_tuple = ForecastTaskDB.read_taskName_of_labor_task(cid)
        taskName_dict = {}
        #bid,taskName
        for item in task_tuple:
            taskBid = item[0]
            task_name_skill = []
            taskName = item[1]
            taskSkillBid = item[2]
            task_name_skill.append(taskName)
            task_name_skill.append(taskSkillBid)
            taskName_dict[taskBid] = task_name_skill

        return taskName_dict

    @staticmethod
    def get_all_index(lst=None, item=''):
        '''
        返回所有给定元素的索引
        :param lst:
        :param item:
        :return:
        '''
        return [index for (index, value) in enumerate(lst) if value == item]


    @staticmethod
    def get_worktime_of_no_emp_task(comb_task_list: List) -> List:
        '''
        获取未排班班次的列表
        :param comb_task_list:
        :param work_date:
        :return:
        '''

        comb_task_list_of_no_emp = []

        for comb_task in comb_task_list:
            if ("缺人" in comb_task.employees):
                comb_task_list_of_no_emp.append(comb_task)

        return comb_task_list_of_no_emp



    @staticmethod
    def get_task_info_by_peroid(cid: str, did: str, comb_task_list: List,third_rules:Dict,task_info_for_temp_emp:Dict,forecast_day,forecastType:str, timeSize:int):
        '''
        转换剩余任务时间格式，用于第三阶段回溯
        :return:
        '''
        # {'2020-01-09': [('20200317195535182140439750000078', '12:00', '12:30', '90')]}

        fix_task_dict: Dict[str, List[FixedTask]] = {}
        direct_task_dict: Dict[str, List[DirectTask]] = {}
        indirect_task_dict: Dict[str, List[InDirectTask]] = {}


        comb_task_list_of_no_emp = CombTasks.get_worktime_of_no_emp_task(comb_task_list)

        for comb_task in comb_task_list_of_no_emp:
            cid = comb_task.cid
            did = comb_task.did
            work_date = comb_task.work_date
            taskId :List = comb_task.taskId
            start:List = comb_task.start
            end:List= comb_task.end

            # 判断类型
            taskType:List = comb_task.taskType

            for index,task_type in enumerate(taskType):

                if not task_type or task_type == '':
                    # 没有taskType
                    continue

                taskBid = taskId[index]
                startTime = start[index]
                endTime = end[index]
                workTime = int(timeSize)

                timeList = DateTimeProcess.timeStr_to_timeList2(timeStr=(startTime + "-" + endTime),
                                                                timeSize=int(timeSize))

                if task_type == 'directwh':

                    # 直接
                    direct_task = direct_task_dict.get(work_date,[])
                    for time_tuple in timeList:
                        start_time = time_tuple[0]
                        end_time = time_tuple[1]

                        # fillCoeficient,discard,taskMinWorkTime,taskMaxWorkTime
                        key = cid + did + taskBid
                        data_list = task_info_for_temp_emp[key]
                        fillCoeficient = float(data_list[0])
                        discard = data_list[1]
                        taskMinWorkTime = int(data_list[2]) if data_list[2] != '' else 0
                        taskMaxWorkTime = int(data_list[3]) if data_list[3] != '' else 480
                        # TODO 实例化

                        direct_task.append(DirectTask(bid=taskBid,start_time=start_time,end_time=end_time,work_time=workTime,
                                                      fill_coef=fillCoeficient,discard=discard,task_min_time=taskMinWorkTime,
                                                      task_max_time=taskMaxWorkTime))
                    direct_task_dict[work_date] = direct_task

                elif task_type == 'indirectwh':
                    # 间接
                    indirect_task = indirect_task_dict.get(work_date, [])
                    for time_tuple in timeList:
                        start_time = time_tuple[0]
                        end_time = time_tuple[1]

                        key = cid + did + taskBid
                        data_list = task_info_for_temp_emp[key]
                        fillCoeficient = float(data_list[0])
                        discard = data_list[1]
                        taskMinWorkTime = int(data_list[2]) if data_list[2] != '' else 0
                        taskMaxWorkTime = int(data_list[3]) if data_list[3] != '' else 480

                        indirect_task.append(InDirectTask(bid=taskBid,work_time=workTime))
                    indirect_task_dict[work_date] = indirect_task

                elif task_type == 'fixedwh':
                    # 固定
                    fix_task = fix_task_dict.get(work_date, [])


                    for time_tuple in timeList:
                        start_time = time_tuple[0]
                        end_time = time_tuple[1]

                        key = cid + did + taskBid
                        data_list = task_info_for_temp_emp[key]
                        fillCoeficient = float(data_list[0])
                        discard = data_list[1]
                        taskMinWorkTime = int(data_list[2]) if data_list[2] != '' else 0
                        taskMaxWorkTime = int(data_list[3]) if data_list[3] != '' else 480

                        fix_task.append(FixedTask(bid=taskBid,start_time=start_time,end_time=end_time,work_time=workTime,
                                                  fill_coef=fillCoeficient,discard=discard,task_min_time=taskMinWorkTime,
                                                  task_max_time=taskMaxWorkTime))
                    fix_task_dict[work_date] = fix_task

        #print(fix_task_dict, direct_task_dict, indirect_task_dict)


        # 调用函数。
        # TODO 调用入口
        # {'comb_rule_list':comb_rule_list,'shift_split_rule_list':shift_split_rule_list,'shift_mod_list':shift_mod_list}
        shift_mod = third_rules.get('shift_mod_list',[])
        combi_rule = third_rules.get('comb_rule_list',[])
        shiftsplitrule = third_rules.get('shift_split_rule_list',[])

        result = ManPowerForecastService.manpower_forecast_recal(cid=cid,bid=forecastType,time_interval=timeSize,did_arr=[did],
                                                        forecast_date_start=forecast_day,forecast_date_end=forecast_day,
                                                        shift_mod=shift_mod,combi_rule=combi_rule,shiftsplitrule=shiftsplitrule,
                                                        direct_task_dict_in=direct_task_dict,fixed_task_dict_in=fix_task_dict,
                                                        indirect_task_dict_in=indirect_task_dict,recal=True,debug=False)
        # 是否成功
        flag = result[0]

        if flag:
            # 矩阵dict：[日期 -> (矩阵，start_time, end_time)]
            matrix_dict = result[2]
            matrix_tuple = matrix_dict.get(forecast_day,[])

            matrix = matrix_tuple[0]
            start_time = matrix_tuple[1]
            end_time = matrix_tuple[2]

            return (cid,did,forecast_day,start_time,end_time,matrix)

        else:
            # 失败原因
            reason = result[1]
            raise Exception(reason)


    @staticmethod
    def get_temp_emp_list(result:Tuple,cid:str,did:str,work_date:str,task_all_info:Dict,timeSize:int):
        '''

        :param result: 重新调用第三阶段排班逻辑返回值 (cid,did,forecast_date,start_time,end_time,task_matrix,type,forecastType)
        :param comb_task_list:
        :param work_date:
        :param task_all_info:
        :param timeSize:
        :return:
        '''

        result_cid = result[0]
        result_did = result[1]
        result_forecast_date = result[2]
        result_start_time = result[3]
        result_end_time = result[4]
        # result_matrix = json.loads(result[5])

        result_matrix = json.loads(result[5]) if result[5] is str else result[5]

        # 获取当天所有班次列表
        temp_comb_task_list = []

        for line in result_matrix:
            i = 0
            day_work_list = []

            while (i < len(line)):
                list_temp = []
                if (line[i] != ''):

                    taskCombination_dict = {}
                    task_set = set()
                    for j in range(i, len(line)):
                        if line[j] == '':
                            # i 记录每个list的起始位置
                            day_work_list.append((i, list_temp))
                            i = j
                            break

                        list_temp.append(line[j])

                        if (j + 1 == len(line)):
                            day_work_list.append((i, list_temp))
                            i = j

                i += 1
            #==========
            #print(day_work_list)

            # day_work_list
            # [(1, ['1','2']), (3, ['1', '3'])]

            taskId_list = []
            taskType_list = []
            taskName_list = []
            start_list = []
            end_list = []
            worktime_list = []
            taskCombination_list = []

            for i,continuous_work_list in day_work_list:

                taskCombination_list.extend(continuous_work_list)
                startTime = DateTimeProcess.cacl_time_str(startTime=result_start_time, timeSize=timeSize,
                                                          timeSizeNum=i)

                i = 0
                while (i < len(continuous_work_list)):
                    taskId = continuous_work_list[i]
                    start = DateTimeProcess.cacl_time_str(startTime=startTime, timeSize=timeSize, timeSizeNum=i)
                    distance = CombTaskService.cacl_distance_of_start_to_end(taskList=continuous_work_list, start_index=i,
                                                                             taskId=taskId)
                    end = DateTimeProcess.cacl_time_str(startTime=start, timeSize=timeSize, timeSizeNum=distance)
                    taskType = task_all_info.get(taskId, {}).get('taskType', '')
                    #taskName = task_all_info.get(taskId, {}).get('taskName', '')

                    taskId_list.append(taskId)
                    taskType_list.append(taskType)
                    #taskName_list.append(taskName)
                    start_list.append(start)
                    end_list.append(end)
                    worktime_list.append(start + '-' + end)

                    i = i + distance

            taskCombination = ",".join(set(taskCombination_list))

            task = CombTasks(cid=str(result_cid), did=str(result_did), work_date=result_forecast_date,
                             taskCombination=taskCombination, combinationVal='1', taskId=taskId_list,shiftId='',
                             taskName_list=[], taskSkillBid_list=[], skillNum_list=[], cert_list=[], taskType=taskType_list,
                             start=start_list, end=end_list, worktimeList=[], employees=["缺人"], worktime_minutes=0)

            # 转换成离散时间列表
            worktime_list = DateTimeProcess.timeStr_to_timeList(timeStrList=worktime_list, timeSize=timeSize)
            task.set_worktimeList(worktime_list)
            # 计算工时
            task.calc_worktime(timeSize=timeSize)

            temp_comb_task_list.append(task)

        return temp_comb_task_list




if __name__ == '__main__':
    # 第三阶段结果
    from POC.service.CombTaskService import CombTaskService
    from POC.bean.LaborTask import LaborTask
    from POC.algorithm.CombTasksEmpMapping import Mapping

    task_all_info = LaborTask.get_laborTask_all_info(cid="60000039",did='54')
    shiftData = CombTaskService.task_to_shift2(cid="60000039",did="54",start_date="2020-04-01",end_date="2020-04-01",task_all_info=task_all_info,timeSize=30,scheme='worktime',schType='0')
    comb_tasks_list = CombTasks.get_comb_tasks_info(shiftData,'2020-04-01',task_all_info,30)

    for obj in comb_tasks_list:
        print('\n'.join(['%s:%s' % item for item in obj.__dict__.items()]))

        print('-----------------------任务组合--------------------------')
    print(len(comb_tasks_list))




