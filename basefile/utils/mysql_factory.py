

class Pos_base_Mysql_Query():

    @classmethod
    def inert_pos_data(cls):
        sql = """
                   insert into base_pos_info_df 
                   (cid,did,gmt_bill,
                    gmt_trunover,money,
                    data_value,transaction_num,
                    peoples,singleSales,
                    commodity_code,payment,
                    deviceCode,order_no,insertTime,
                    updateTime,aistatus
                    ) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    on duplicate key update 
                    gmt_bill = values(gmt_bill),
                    gmt_trunover = values(gmt_trunover),
                    money = values(money),
                    data_value = values(data_value),
                    transaction_num = values(transaction_num),
                    peoples = values(peoples),
                    commodity_code = values(commodity_code),
                    deviceCode = values(deviceCode),
                    insertTime = values(insertTime),
                    updateTime = values(updateTime),
                    aistatus = values(aistatus)
                """
        return sql
    @classmethod
    def _get_info_data(cls):
        sql = """
              select 
                    cid,did,
                    gmt_bill,
                    money,
                    data_value,
                    peoples,
                    order_no
              from base_pos_info_df
              where gmt_bill>='%s' and gmt_bill<='%s' and cid='%s' and did='%s' and aistatus=1
              """
        return sql

class Pos_view_Mysql_Query():
    @classmethod
    def update_view_pos(cls):
        sql = """
                insert into view_pos_info_df 
                (cid,did,shike,trueGMV,predictGMV,
                adjustGMV,truePeoples,predictPeoples,adjustPeoples,
                status,insertTime,updateTime,trueOrders,
                predictOrders,adjustOrders)
                values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                on duplicate key update
                    trueGMV = values(trueGMV),
                    truePeoples = values(truePeoples),
                    trueOrders = values(trueOrders),
                    updateTime = values(updateTime)
              """
        return sql


class Pos_task_detail_Query():

    @classmethod
    def insert_sql1(cls,headers):
        sql ="""
             insert into push_task_detail 
             (batch_id,serialNumber,total_count,
             request_count,data_start_time,data_end_time,
             push_token,modify_time,cid,did)
             values ('{batch_id}',
                     '{serialNumber}',{total_count},
                    {request_count},'{data_start_time}',
                    '{data_end_time}','{push_token}',
                    '{modify_time}','{cid}','{did}')
             """.format(batch_id=headers["batch_id"],
                        serialNumber=headers["serialNumber"],
                        total_count =headers["totalCount"],
                        request_count = headers["requestCount"],
                        data_start_time = headers["startTime"],
                        data_end_time=headers["endTime"],
                        push_token=headers["pushToken"],
                        modify_time = headers["pushToken"],
                        cid = headers["cid"],
                        did = headers["did"],
                       )
        return sql
    @classmethod
    def insert_sql(cls):
        sql="""insert into push_task_detail 
             (batch_id,serialNumber,total_count,
             request_count,data_start_time,data_end_time,
             push_token,modify_time,cid,did)
             values ('%s','%s',%s,%s,'%s','%s','%s','%s','%s','%s')
             """
        return sql

class Push_task_status_Query():

    @classmethod
    def update_status_Query(self):
        sql = """
             insert into push_task_status 
             (batch_id,received_count,
             view_proc_state,total_count,
             modify_time,cid,did)
             values('%s',%s,%s,%s,'%s','%s','%s') 
             on duplicate key update received_count =received_count+ values(received_count),
             view_proc_state= values(view_proc_state),
             total_count = values(total_count),
             modify_time = values(modify_time)
             """
        return sql

    @classmethod
    def get_received_count(self):
        sql = """
              select received_count,view_proc_state 
                 from push_task_status 
                 where batch_id='%s'
              """
        return sql

    @classmethod
    def update_Push_task_status(self):
        sql = """
              update push_task_status 
                    set view_proc_state =1,modify_time='%s'
                    where batch_id='%s'
              """
        return sql
