# -*- coding:utf-8 -*-
# -*- created by: mo -*-


import argparse
import sys
from forecastPOS.logic.predictCls import PredictHandler
from forecastPOS.logic.modifyCls import ModifyHandler
from forecastPOS.logic.forecastModifyCls import ForecastModifyHandler
from labor.logic.pushCIs import PushHandler
from labor.logic.forecastCls import ForecastMHandler
from labor.logic.forecastCls_v2 import ForecastMHandler_v2
from labor.logic.lforecastModifyCls import LForecastModifyHandler
from laborCnt.logic.ShiftSplitRuleModifyCls import ShiftSplitRuleModifyHandler
from laborCnt.logic.modifyCls import ShiftModModifyHandler
from laborCnt.logic.ManPowerCls import ManPowerModifyHandler
from laborCnt.logic.LaborTaskModifyCls import LaborTsakModifyHandler
from laborCnt.logic.CombRuleModifyCls import CombRuleModifyHandler
from laborCnt.logic.manpower_forecastCls import ManPowerForecastHandler
from POC.logic.EmpSkillModify import EmpSkillModifyHandler
from POC.logic.AvailableTimeModify import AvailableTimeHandler
from POC.logic.empCertModify import EmpCertModifyHandler
from POC.logic.EmpMatchproModify import EmpMatchproModifyHandler
from POC.logic.calModify import CalModifyHandler
from POC.logic.ComplianceModify import ComplianceHandler
from POC.logic.PBResult import PBResultHandler
from utils.myLogger import infoLog
from utils.tools import get_host_ip
# 喔趣后端
from laborCaclValue.logic.labor_cacl_value_handler import LaborCaclValueHandler
from laborCombRule.logic.combrule_handler import CombruleHandler
from laborShiftSplitRule.logic.shift_split_rule_handler import ShiftSplitRuleHandler
from laborStandard.logic.labor_standard_handler import LaborStandardHandler
from laborTask.logic.labor_task_handler import LaborTaskHandler
from posData.logic.pos_data_handler import PosDataHandler
from base.logic.base_handler import BaseHandler
from empMatchpro.logic.emp_matchpro_handler import EmpMatchproHandler
from empSkill.logic.emp_skill_handler import EmpSkillHandler
from employeeCertificate.logic.employee_certificate_handler import EmployeeCertificateHandler
from schAvailableTime.logic.sch_available_time_handler import SchAvailableTimeHandler
from schCompliance.logic.sch_compliance_handler import SchComplianceHandler
from specialEvent.logic.special_event_handler import SpecialEventHandler
from specialEvent.logic.special_event_scope_handler import SpecialEventScopeHandler
from user.logic.user_handler import UserHandler
from viewGoodsDf.logic.goods_statistics_handle import GoodsStatisticsHandle
from laborTaskView.logic.task_view_handler import TaskViewHandler
from shiftWorkInspection.logic.shift_work_inspection import ShiftWorkInspectionHandler
from scheduleView.logic.schedule_view_handler import ScheduleViewHandler
from forecastPOS.logic.posPush import PosPushHandler
from forecastPOS.logic.getPosNum import GetPosNum
from multiprocessing import cpu_count
from posView.logic.pos_view_logic import PosViewHandler

sys.path.append('/xx/woqu20200421/woqu/basefile')

apiTuples = [
    (r"/pos/result", PredictHandler),  # pos预测接口
    (r"/pos/modify", ModifyHandler),  # pos base数据修改接口
    (r"/pos/push", PosPushHandler),  # pos base数据修改接口（第三版）
    (r"/pos/num", GetPosNum),  # 获取POS数据
    (r"/pos/forecastModify", ForecastModifyHandler),  # pos结果数据修改接口

    (r"/labor/standard/push", PushHandler),  # 劳动力标准
    (r"/labor/worktime/forecast", ForecastMHandler),  # 劳动力工时预测
    (r"/v2/labor/worktime/forecast", ForecastMHandler_v2),  # 劳动力工时预测(第二版)
    (r"/labor/worktime/forecastModify", LForecastModifyHandler),  # 劳动力工时手动修改值

    (r"/labor/shiftmod/modify", ShiftModModifyHandler),  # 班次
    (r"/labor/combirule/modify", CombRuleModifyHandler),  # 组合规则
    (r"/labor/shiftsplitrule/modify", ShiftSplitRuleModifyHandler),  # 拆分规则

    (r"/labor/task/modify", LaborTsakModifyHandler),  # 任务详情

    (r"/labor/manpower/modify", ManPowerModifyHandler),  # 预测人数手工修改
    (r"/labor/manpower/forecast", ManPowerForecastHandler),  # 劳动力人数预测接口

    (r"/sch/availabletime/modify", AvailableTimeHandler),  # 员工可用性-修改接口
    (r"/sch/empskill/modify", EmpSkillModifyHandler),  # 第四阶段-接口2-员工技能修改
    (r"/sch/empcert/modify", EmpCertModifyHandler),  # 员工证书-修改接口
    (r"/sch/compliance/modify", ComplianceHandler),  # 第四阶段-接口4：排班合规性-修改接口
    (r"/sch/matchpro/modify", EmpMatchproModifyHandler),  # 第四阶段-接口5-员工匹配属性
    (r"/sch/cal/modify", CalModifyHandler),  # 排班结果修改
    (r"/sch/cal", PBResultHandler),  # 排班结果获取

    # 喔趣后端接口
    (r"/base/(\w+)", BaseHandler),
    # (r"/labor/shiftmod/modify", ShiftModModifyHandler),
    (r"/pos/event/modify", SpecialEventHandler),  # 新增特殊事件（测试）
    (r"/posData/push", PosDataHandler),  # pos数据导入/更新接口
    (r"/pos/event/scope", SpecialEventScopeHandler),  # 事件范围（分配特殊事件）增删改接口
    (r"/viewPos/(\w+)", GoodsStatisticsHandle),
    (r"/user/(\w+)", UserHandler),
    (r"/shiftsplit/(\w+)", ShiftSplitRuleHandler),
    (r"/combrule/(\w+)", CombruleHandler),
    (r"/task/(\w+)", LaborTaskHandler),
    (r"/standard/(\w+)", LaborStandardHandler),
    (r"/laborCacl/(\w+)", LaborCaclValueHandler),
    (r"/schCompliance/(\w+)", SchComplianceHandler),
    (r"/empMatchpro/(\w+)", EmpMatchproHandler),
    (r"/empSkill/(\w+)", EmpSkillHandler),
    (r"/empCertificate/(\w+)", EmployeeCertificateHandler),
    (r"/schAvTime/(\w+)", SchAvailableTimeHandler),
    (r"/taskView/(\w+)", TaskViewHandler),
    (r"/shiftWorktime/(\w+)", ShiftWorkInspectionHandler),
    (r"/schView/(\w+)", ScheduleViewHandler),

    # 喔趣 API 调用
    (r"/labor/standard/(\w+)", LaborStandardHandler),
    (r"/labor/shiftsplitrule/(\w+)", ShiftSplitRuleHandler),
    (r"/labor/combirule/(\w+)", CombruleHandler),
    (r"/labor/empskill/(\w+)", EmpSkillHandler),
    (r"/labor/availabletime/(\w+)", SchAvailableTimeHandler),
    (r"/pos/(\w+)", PosDataHandler),
    (r"/labor/task/(\w+)", LaborTaskHandler),
    (r"/labor/compliance/(\w+)", SchComplianceHandler),
    (r"/labor/worktime/(\w+)", LaborCaclValueHandler),
    (r"/labor/posPredict/(\w+)", PosViewHandler),
    (r"/labor/manpower/(\w+)", TaskViewHandler),
]
application = tornado.web.Application(apiTuples)

if __name__ == "__main__":
    '''
    :入口
    :param none
    '''
    parser = argparse.ArgumentParser(description="Server of woqu service")
    parser.add_argument("--port", type=int, default=8867, help="server port")
    args = parser.parse_args()
    application.listen(args.port)
    cpu_num = cpu_count()
    # http_server = tornado.httpserver.HTTPServer(application)
    # http_server.bind(args.port)
    # http_server.start(max(cpu_num//2,1))#当前不全部打满CPU，防止出现问题
    # http_server.start(1)
    infoLog.info("Begin to serve at http://{}:{} and server_num:{}".format(get_host_ip(), args.port, cpu_num // 2))
    tornado.ioloop.IOLoop.instance().start()
