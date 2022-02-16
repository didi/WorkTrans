# coding: utf-8
# author: hmk

import pymysql.cursors

# 连接数据库
conn = pymysql.connect(host='10.86.60.67',
                       user='root',
                       password='Ybaobao1',
                       db='woqu',
                       charset='utf8')


# 创建一个游标
cursor = conn.cursor()

# 查询数据
sql = "select * from base_pos_df limit 10"
cursor.execute(sql)  # 执行sql

# 查询所有数据，返回结果默认以元组形式，所以可以进行迭代处理
for i in cursor.fetchall():
    print(i)
print('共查询到：', cursor.rowcount, '条数据。')

# 获取第一行数据
result_1 = cursor.fetchone()
print(result_1)

# 获取前n行数据
result_3 = cursor.fetchmany(3)
print(result_3)

cursor.close()  # 关闭游标
conn.close()  # 关闭连接
