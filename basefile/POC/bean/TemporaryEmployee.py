'''
create by liyabin
'''

from typing import Dict,List,Tuple
import datetime
from utils.dateTimeProcess import DateTimeProcess
from POC.model.forecast_task_DB import ForecastTaskDB
import numpy as np

class TemporaryEmployee:

    def __init__(self,cid:str,eid:str,work_date:str,dayWorkTime:int,available_timeList:List,tasks:List,dayShiftNum:int):
        '''
        员工基础属性
        :param cid: 公司id
        :param eid: 员工id
        :param work_date: 工作日期
        :param dayWorkTime: 工作时长
        :param available_timeList: 可用时间列表
        :param tasks: 工作任务清单
        :param dayShiftNum: 班次个数
        '''
        self.cid = cid
        self.did = ""
        self.eid = eid
        self.work_date = work_date
        self.dayWorkTime = dayWorkTime
        self.available_timeList = available_timeList
        # 被分配的任务列表
        self.tasks = tasks
        # 被排班次个数
        self.dayShiftNum = dayShiftNum
        # 匹配属性
        self.weight = 1
        # 合规性
        self.caution = ""
        # 违反软约束的个数
        self.break_rule_num = 0


    def set_did(self,did:str):
        self.did = did

    def set_shift_num(self):
        '''
        设置班次个数
        :return:
        '''
        self.dayShiftNum += 1

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

    def set_worktime(self,workTime:int):
        '''
        设置劳动工时
        :param dayWorkTime:
        :return:
        '''
        self.dayWorkTime += workTime

    def set_caution(self,caution:str):
        self.caution = caution


if __name__ == '__main__':

    obj = TemporaryEmployee(cid='123456',eid='88',work_date='2017-09-12',dayWorkTime=0,
                             available_timeList=[1]*(24*60//30),tasks=[],dayShiftNum=0)

    print('\n'.join(['%s:%s' % item for item in obj.__dict__.items()]))






