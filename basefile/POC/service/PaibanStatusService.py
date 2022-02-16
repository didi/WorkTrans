"""
阶段四接口6-获取长连接
2019-11-14
"""
from typing import Dict,List,Set,Tuple
from utils.dateTimeProcess import DateTimeProcess
from POC.bean.LaborTask import LaborTask
from POC.service.CombTaskService import CombTaskService
from POC.model.forecast_task_DB import ForecastTaskDB
from POC.bean.EmpComplianceRule import EmpComplianceRule
from POC.service.ComTaskEmpMappingService import ComTaskEmpMappingService
from POC.algorithm.CombTasksEmpMapping import Mapping
from POC.bean.CombTasks import CombTasks
import datetime

class PaibanStatusService:


    @staticmethod
    def paibanStatus(raw_data: Dict):
        """
        save_result={}

        flag=1 #不需要运行，可以直接返回
        calc=[]
        for 日期 in 日期范围：
            #根据raw_data测applyid和日期，【状态表】， 判断数据库是否有值
            if （applyid not in 【状态表】）
              or （日期 not in 【状态表】）
              or （status =success） :
              flag = 0
              calc.append(日期)

        if flag==1:
            save_result=#直接从数据库结果表读出数据，返回
        else:
            for 日期 in calc:
                insert 【状态表】 : applyid and 日期 and 【状态表]=running
                调用这一天的计算 （计算这一天）
                保存结果入【排班结果表】
                update 【状态表】: applyid and 日期 and 【状态表]=success
            save_result =  #{status：'running',cal:''}
        return save_result
        """