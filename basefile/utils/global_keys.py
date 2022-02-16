'''
100:更新成功
101:DB操作错误
102:DB更新错误
103:更新pos成功，但是更新view表失败
400:未知异常
405:非法请求
408: token校验失败，非法请求
'''

RES_100= {"code":100,"result":"更新成功"}
RES_101= {"code":101,"result":"DB操作错误"}
RES_102= {"code":102,"result":"DB更新错误"}
RES_103= {"code":103,"result":"更新pos成功，但是更新view表失败"}
RES_400= {"code":400,"result":"未知异常"}
RES_405= {"code":405,"result":"非法请求"}
RES_401= {"code":401,"result":"缺少传字段"}
RES_402= {"code":402,"result":"数据重复传"}
RES_408= {"code":408,"result":"token校验失败，非法请求"}
RES_409= {"code":409, "result":"传参数错误"}

POS_THREAD_NUM =5
TRY_times =3

