import json
import threading
import hashlib
import datetime
import time

class Token():

    def getToken(self,timeStr):
        # 待加密信息
        appkey='c3d60ed77cd@ee94734@f9cf4180'
        appsecret='194c0006e2d#478d0f99705%216983ce06'
        str=("make token %s,%s,%s" %(appkey,appsecret,timeStr))

        # 创建md5对象
        m = hashlib.md5()

        # Tips
        # 此处必须encode
        # 若写法为m.update(str)  报错为： Unicode-objects must be encoded before hashing
        # 因为python3里默认的str是unicode
        # 或者 b = bytes(str, encoding='utf-8')，作用相同，都是encode为bytes
        b = str.encode(encoding='utf-8')
        m.update(b)
        str_md5 = m.hexdigest()

        return str_md5

# 获取token的时间戳
timestr_new = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
token_new =  Token().getToken(timestr_new)

with open("./interface_para.json",'r') as fr:
	data = fr.read()

data = json.loads(data)
uri = "http://ailabspre.didichuxing.com"

# 记录正确和失败的接口
interface_num = 0
error_num = 0
success_num = 0
error_interface = []
success_interface = []


for interface in data:
    interface_num += 1
    url = uri + interface
    # 修改参数里面的token的时间戳
    data[interface]['timestr'] = timestr_new 
    data[interface]['token'] = token_new
    res = requests.post(url, json=data[interface])

    # 如果返回的是json
    try:
        code_data = json.loads(res.text)
        if code_data['code'] == 100:
            success_num += 1
            success_interface.append(url)
        else:
            error_num += 1
            error_interface.append(url)
            print('接口：',interface, '请求失败的原因',res.text)
    
    except json.decoder.JSONDecodeError:
        error_num += 1
        error_interface.append(url)
        print('接口：',interface, '请求失败的原因',res.text)
        continue

print('测试接口的个数：', interface_num)
print('成功接口的个数：', success_num)
print('失败接口的个数：', error_num)
print('成功的接口', success_interface)
print('失败的接口', error_interface)

