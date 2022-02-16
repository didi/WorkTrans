'''
create by liyabin
'''

from POC.model.forecast_task_DB import ForecastTaskDB
import json
from utils.dateTimeProcess import DateTimeProcess
from typing import Dict,List

class CombTaskService:
    @staticmethod
    def task_to_shift(cid:str,did:str,start_date:str,end_date,task_all_info:Dict):
        '''
        将第三阶段结果矩阵，划分为班次，并按15分钟一个进行输出。
        :param cid:
        :param did:
        :param start_date:
        :param end_date:
        :param task_all_info:
        :return:
        '''
        result_tuple = ForecastTaskDB.read_matrix(cid=cid, did=did, start_date=start_date, end_date=end_date)

        manpower = []
        for item in result_tuple:

            # cid,did,forecast_date,start_time,end_time,task_matrix
            matrix_dict = {}
            matrix_dict["cid"] = item[0]
            matrix_dict["did"] = item[1]
            matrix_dict["forecast_date"] = item[2]

            matrix_dict["start_time"] = item[3]
            matrix_dict["end_time"] = item[4]
            matrix_dict["matrix"] = json.loads(item[5])

            print("------------------------" + matrix_dict["forecast_date"] + "--------------------------")

            #写入文件
            """
            file_name = "/Users/didi/PycharmProjects/woqu/basefile/POC/csv_file/matrix_" + matrix_dict["forecast_date"] + ".csv"
            with open(file_name, "w") as csvfile:
                import csv
                writer = csv.writer(csvfile)
                for line in matrix_dict["matrix"]:
                    writer.writerow(line)
            """
                # 写入一个矩阵 2019-07-12

            # 获取当天所有班次
            all_shift_list = []

            for emp_task_list in matrix_dict["matrix"]:
                i = 0

                while (i < len(emp_task_list)):
                    list_temp = []
                    if (emp_task_list[i] != ''):

                        taskCombination_dict = {}
                        task_set = set()
                        for j in range(i, len(emp_task_list)):
                            if emp_task_list[j] == '':
                                taskCombination = ",".join(list(task_set))
                                combinationVal = "1"
                                taskCombination_dict["taskCombination"] = taskCombination
                                taskCombination_dict["combinationVal"] = combinationVal
                                taskCombination_dict["detail"] = list_temp
                                all_shift_list.append(taskCombination_dict)
                                i = j
                                break

                            task_dict = {}
                            # task集合 用于taskCombination
                            task_set.add(emp_task_list[j])

                            task_dict["taskId"] = emp_task_list[j]
                            task_dict["start"] = DateTimeProcess.cacl_time_str(startTime=matrix_dict["start_time"],timeSize=15,timeSizeNum=j-0)
                            #print("start为 %s " % task_dict["start"])
                            task_dict["end"] = DateTimeProcess.cacl_time_str(startTime=task_dict["start"],timeSize=15,timeSizeNum=1)
                            #print("end为 %s " % task_dict["end"])
                            task_dict["taskType"] = task_all_info[task_dict["taskId"]]["taskType"]
                            list_temp.append(task_dict)


                            if (j + 1 == len(emp_task_list)):
                                taskCombination = ",".join(list(task_set))
                                combinationVal = "1"
                                taskCombination_dict["taskCombination"] = taskCombination
                                taskCombination_dict["combinationVal"] = combinationVal
                                taskCombination_dict["detail"] = list_temp
                                all_shift_list.append(taskCombination_dict)
                                i = j

                    i += 1

            date_data_dict = {
                matrix_dict["forecast_date"]:all_shift_list
            }
            manpower.append(date_data_dict)

        result_dict = {
            "cid":cid,
            "did":did,
            "ssData":{
                "manpowers": manpower
            }
        }
        return result_dict

    @staticmethod
    def task_to_shift2(cid: str, did: str, start_date: str, end_date, task_all_info: Dict,schType:str,scheme:str,timeSize:int):
        '''
        读取第三阶段结果矩阵，划分成班次，并合并时间
        :param cid:
        :param did:
        :param start_date:
        :param end_date:
        :param task_all_info:
        :param timeSize:
        :return:
        '''
        type_ = 'full'
        # if(scheme == 'worktime'):
        #     type_ = 'min'
        result_tuple = ForecastTaskDB.read_matrix(cid=cid, did=did, start_date=start_date, end_date=end_date,forecastType=schType,type=type_)
        manpower = []
        for item in result_tuple:

            # cid,did,forecast_date,start_time,end_time,task_matrix
            matrix_dict = {}
            matrix_dict["cid"] = item[0]
            matrix_dict["did"] = item[1]
            matrix_dict["forecast_date"] = item[2]

            matrix_dict["start_time"] = item[3]
            matrix_dict["end_time"] = item[4]
            matrix_dict["matrix"] = json.loads(item[5])

            # print("------------------------" + matrix_dict["forecast_date"] + "--------------------------")
            # file_name = "/Users/didi/PycharmProjects/woqu5/basefile/POC/matrix_" + matrix_dict[
            #     "forecast_date"] + ".csv"
            # with open(file_name, "w") as csvfile:
            #     import csv
            #     writer = csv.writer(csvfile)
            #     for line in matrix_dict["matrix"]:
            #         writer.writerow(line)

            # 获取当天所有班次
            all_shift_list = []

            for emp_task_list in matrix_dict["matrix"]:
                i = 0

                while (i < len(emp_task_list)):
                    list_temp = []
                    if (emp_task_list[i] != ''):

                        taskCombination_dict = {}
                        task_set = set()
                        for j in range(i, len(emp_task_list)):
                            if emp_task_list[j] == '':
                                # i 记录每个list的起始位置
                                all_shift_list.append((i,list_temp))
                                i = j
                                break

                            list_temp.append(emp_task_list[j])

                            if (j + 1 == len(emp_task_list)):

                                all_shift_list.append((i,list_temp))
                                i = j

                    i += 1

            #print("all_shift_list:")
            #print(all_shift_list)

            all_shift_group_list = []
            # i 为每个班次在矩阵中的起始索引
            for i,shift_list in all_shift_list:
                detail = []
                taskCombination = ",".join(set(shift_list))
                combinationVal = "1"
                startTime = DateTimeProcess.cacl_time_str(startTime=matrix_dict["start_time"],timeSize=timeSize,timeSizeNum=i)

                i = 0
                while(i < len(shift_list)):
                    taskId = shift_list[i]
                    start = DateTimeProcess.cacl_time_str(startTime=startTime, timeSize=timeSize,timeSizeNum=i)
                    distance = CombTaskService.cacl_distance_of_start_to_end(taskList=shift_list,start_index=i,taskId=taskId)
                    end = DateTimeProcess.cacl_time_str(startTime=start,timeSize=timeSize,timeSizeNum=distance)
                    taskType = task_all_info.get(taskId,{}).get('taskType','')

                    detail.append({
                        'taskId':taskId,
                        'start':start,
                        'end':end,
                        'taskType':taskType
                    })

                    i = i + distance


                all_shift_group_list.append({
                    'taskCombination':taskCombination,
                    'combinationVal':combinationVal,
                    'detail':detail
                })

            date_data_dict = {
                matrix_dict["forecast_date"]: all_shift_group_list
            }
            manpower.append(date_data_dict)


        result_dict = {
            "cid": cid,
            "did": did,
            "ssData": {
                "manpowers": manpower
            }
        }
        return result_dict
    @staticmethod
    def cacl_distance_of_start_to_end(taskList:List,start_index:int,taskId:str):
        '''
        计算某一工作的开始到结束的距离，用于计算时间跨度
        :param taskList:
        :param start_index:
        :param taskId:
        :return:
        '''
        for i in range(start_index, len(taskList)):
            if (taskList[i] != taskId):
                return i - start_index
        return len(taskList) - start_index


if __name__ == '__main__':
    from POC.bean.LaborTask import LaborTask
    #info_dict = CombTaskService.task_to_shift2(cid="123456",did="6",start_date="2019-07-12",end_date="2019-07-18",task_all_info=LaborTask.get_laborTask_all_info(cid="123456",did='6'),timeSize=30,scheme='emp',schType='0')

    info_dict = CombTaskService.task_to_shift2(cid="50000031",did='7692', start_date="2019-07-20", end_date="2019-07-20",task_all_info=LaborTask.get_laborTask_all_info(cid="50000031",did='7692'),timeSize=30,scheme='emp',schType='0')
    print(info_dict)


