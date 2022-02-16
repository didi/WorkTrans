"""
create by liyabin
"""
import datetime
from typing import List


# 处理时间间隔 2019-07-1 - 2019-07-02
class DateTimeProcess:

    @staticmethod
    def datetimeToStr(dateTime:datetime.date) -> str:
        return datetime.datetime.strftime(dateTime,"%Y-%m-%d")

    @staticmethod
    def change_date_str(date_str: str, range: int):
        '''
        改变天数
        :param date_str:
        :param range:
        :return:
        '''
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        goal_date = date + datetime.timedelta(days=range)

        return goal_date.strftime("%Y-%m-%d")

    @staticmethod
    def date_interval(start_day: str, end_day: str) -> List[str]:
        '''
        计算日期间隔
        :param start_day:
        :param end_day:
        :return:
        '''

        date_list = []
        start_day = datetime.datetime.strptime(start_day, "%Y-%m-%d")
        end_day = datetime.datetime.strptime(end_day, "%Y-%m-%d")
        diff_days = (end_day - start_day).days + 1
        for i in range(diff_days):
            # 当前日期 + 1
            current_day = start_day + datetime.timedelta(days=i)
            current_day_str = current_day.strftime('%Y-%m-%d')
            date_list.append(current_day_str)

        return date_list

    @staticmethod
    def worktime_interval(start_time: str, end_time: str, timeSize: int) -> int:
        '''
        计算两个时间的 分钟数
        :param start_time:
        :param end_time:
        :return:
        '''
        start_time = datetime.datetime.strptime(start_time, '%H:%M')

        if end_time == '24:00' or end_time == '00:00':
            end_time = datetime.datetime.strptime("23:59:59", "%H:%M:%S")
            diff_time = int((end_time - start_time).total_seconds()) // 60 + 1
        else:
            end_time = datetime.datetime.strptime(end_time, '%H:%M')

            # 处理跨天
            if start_time >= end_time:
                end_time = end_time + datetime.timedelta(days=1)

            diff_time = int((end_time - start_time).total_seconds()) // 60


        return diff_time

    @staticmethod
    def compare_date(task_date: str, forecast_day: str) -> int:
        '''
        预测日期和工作日期作比较  大于 1 等于 0 小于 -1
        :param task_date:
        :param forecast_day:
        :return:
        '''
        task_date = datetime.date.fromisoformat(task_date)
        forecast_day = datetime.date.fromisoformat(forecast_day)

        if (forecast_day < task_date):
            return -1
        elif (forecast_day == task_date):
            return 0
        elif (forecast_day > task_date):
            return 1

    @staticmethod
    def timeStr_to_timeList(timeStrList: List, timeSize: int) -> List[int]:
        '''
        时间字符串转换为时间列表
        :param timeStr: 时间字符串 例如:12:00-23:00
        :param timeSize: 时间粒度  例如： 15min
        :return:
        '''

        timeList = [0] * (24 * 60 // timeSize)
        for timeStr in timeStrList:
            hour_list = timeStr.split("-")
            start = hour_list[0]
            end = hour_list[1]

            init_time = datetime.datetime.strptime("00:00", "%H:%M")

            start_time = None
            if start == '24:00':
                #start_time = datetime.datetime.strptime("23:59:59", "%H:%M:%S")
                start_time = datetime.datetime.strptime("00:00", "%H:%M")
            else:
                start_time = datetime.datetime.strptime(start, "%H:%M")

            end_time = None
            if end == '24:00':
                end_time = datetime.datetime.strptime("23:59:59", "%H:%M:%S")
            else:
                end_time = datetime.datetime.strptime(end, "%H:%M")

            start_index = int((start_time - init_time).total_seconds()) // 60 // timeSize
            gap = int((end_time - start_time).total_seconds()+1) // 60 // timeSize

            for i in range(start_index, start_index + gap):
                timeList[i] = 1
        return timeList

    @staticmethod
    def timeStr_to_timeList2(timeStr: str, timeSize: int) -> List:
        '''
        将时间字符串拆分为最小粒度列表
        例如：08:00-09:00
        :param timeStr:
        :param timeSize:
        :return:
        '''
        timeList = timeStr.split('-')
        start_time = timeList[0]
        end_time = timeList[1]

        new_time_list = []

        if start_time >= end_time:
            if end_time == '00:00':
                end_time = '23:59'

        startTime = datetime.datetime.strptime(start_time, "%H:%M")
        endTime = datetime.datetime.strptime(end_time, "%H:%M")

        gap = (endTime - startTime).total_seconds() + 60 // 60 // timeSize

        while startTime < endTime:
            temp_Time = startTime + datetime.timedelta(minutes=timeSize)

            start = startTime.strftime("%H:%M")
            end = temp_Time.strftime("%H:%M")

            new_time_list.append((start, end))

            startTime = temp_Time

        return new_time_list

    @staticmethod
    def cacl_time_str(startTime: str, timeSize: int, timeSizeNum: int):
        '''
        计算增加timeSizeNum以后的时间字符串
        :param startTime:
        :param timeSize:
        :param timeSizeNum:
        :return:
        '''
        startTime = datetime.datetime.strptime(startTime, "%H:%M")
        endTime = startTime + datetime.timedelta(minutes=(timeSize) * timeSizeNum)

        return datetime.datetime.strftime(endTime, "%H:%M")

    @staticmethod
    def print_timeList_of_day_and_timeSize(timeSize: int):
        '''
        返回一整天的时间字符串，按粒度打印
        :param timeSize:
        :return:
        '''
        timeNum = 24 * 60 // timeSize
        timeList = []
        for _ in range(timeNum):
            start_ = DateTimeProcess.cacl_time_str(startTime='00:00', timeSize=timeSize, timeSizeNum=_)
            end_ = DateTimeProcess.cacl_time_str(startTime=start_, timeSize=timeSize, timeSizeNum=1)
            timeList.append(start_ + "-" + end_)
        return timeList

    @staticmethod
    def timedelta_to_timeStr(forecast_day:str,obj):
        '''
        datetime.timedelta 转 timeStr
        :param obj:
        :return:
        '''
        #date = datetime.datetime.strptime(forecast_day, '%Y-%m-%d')
        date = forecast_day
        t = obj
        t = date + t
        timeStr = datetime.datetime.strftime(t, '%Y-%m-%d %H:%M')

        return timeStr


if __name__ == '__main__':
    # datestr1 = '2017-03-28'
    # datestr2 = '2017-04-05'
    #
    # date1 = datetime.datetime.strptime(datestr1,"%Y-%m-%d")
    # date2 = datetime.datetime.strptime(datestr2,"%Y-%m-%d")
    # #日期差值
    # diff_days = (date2 - date1).days
    #
    # date_list = DateTimeProcess.date_interval(datestr1,datestr2)
    # print("date_list:")
    # print(date_list)
    # for item in date_list:
    #     print(item)
    #
    # #print(date2 + datetime.timedelta(days=1))
    #
    # task_list1 = ['05:30-05:45', '06:00-06:15']
    # emp_list2 = ['05：00-08：00', '09:00-12:00']

    # emp_time = []
    # for item in emp_list2:
    #     str_list = item.split('-')
    #     emp_time.extend(str_list)
    # print(emp_time.sort())
    # task_time = []
    # for item in task_list1:
    #     str_list = item.split('-')
    #     task_time.extend(str_list)
    # print(task_time.sort())

    # timeList = DateTimeProcess.timeStr_to_timeList(["24:00-24:00"],30)
    # print(timeList)
    # print(len(timeList))
    #
    # start_time = "23:00"
    # end_time = "23:59"
    # diff_m = DateTimeProcess.worktime_interval(start_time,end_time,15)
    # print(diff_m)

    # def search_max_len_dateStr(date_str_list:List):
    #     '''
    #     寻找最大的连续天数字符串的个数
    #     :param date_str_list:
    #     :return:
    #     '''
    #     if not date_str_list: return 0
    #     if len(date_str_list) == 1: return 1
    #
    #     len_ = 1
    #     max_len = 1
    #     for i in range(1, len(date_str_list)):
    #         if (DateTimeProcess.change_date_str(date_str_list[i - 1], 1) == date_str_list[i]):
    #             len_ = len_ + 1
    #         elif (len_ > max_len):
    #             max_len = len_
    #             len_ = 1
    #
    #     return max_len if max_len > len_ else len_
    #
    #
    # lst = ['2019-07-01', '2019-07-02']  # 连续数字
    # print(search_max_len_dateStr(lst))

    # print(DateTimeProcess.print_timeList_of_day_and_timeSize(30))

    timeList = DateTimeProcess.timeStr_to_timeList2(timeStr='08:00-09:00', timeSize=15)
    print(timeList)
