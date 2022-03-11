import time
from pymysql import connect
import numpy as np
#  建立链接


if __name__ == '__main__':

    # conn = connect(host='localhost', port=3306, db='woqu', user='root', password='12345678', charset='utf8')
    # 获取游标
    cur = conn.cursor()
    start = time.time()
    sql = "insert into base_pos_df(" \
          "`cid`" \
          ",`did`,`gmt_bill`,`gmt_trunover`,`money`,`data_value`" \
          ",`bill_year`,`bill_month`,`bill_day`,`bill_hour`,`bill_minute`" \
          ",`peoples`,`order_no`" \
          ",`singleSales`,`payment`,`deviceCode`" \
          ",`insertTime`,`updateTime`, `aistatus`" \
          ",`transaction_num`,`commodity_code`) values "

    # 随机生成
    for i in range(1,20001):
        # sql语句
        sql = sql+"(\"{}\"" \
                  ",\"{}\",\"{}\",\"{}\",\"{}\",{}" \
                  ",{},{},{},{},\"{}\"" \
                  ",\"{}\",\"{}\"" \
                  ",{},\"{}\",\"{}\"" \
                  ",\"{}\",\"{}\",{}" \
                  ",{},\"{}\"),".format(
            "cid"
            ,"did","gmt_bill","gmt_trunover",np.random.randint(i)*1.1,np.random.randint(i)

            ,np.random.randint(i),np.random.randint(i),np.random.randint(i),np.random.randint(i),np.random.randint(i)

            ,np.random.randint(i)
            ,"order_no"+str(np.random.randint(i))

            ,np.random.randint(i)
            ,"payment"+str(np.random.randint(i))
            ,"deviceCode"+str(np.random.randint(i))

            ,"insertTime"+str(np.random.randint(i))
            ,"updateTime"+str(np.random.randint(i))
            ,1000+np.random.randint(i)

            ,np.random.randint(i)
            ,"commodity_code"+str(np.random.randint(i))
        )
    sql = sql[:-1]

    row_count = cur.execute(sql)

    # 显示操作结果
    # print("SQL语句影响的行数为%d" % row_count)
    end = time.time()
    print(end-start)

    # 统一提交
    conn.commit()
    # 关闭游标
    cur.close()
    # 关闭连接
    conn.close()