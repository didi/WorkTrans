import requests, json
from urllib import parse



ip='127.0.0.1'

url = 'http://'+ip+':8867/pos/setting'
data={
	"cid": "123456",
	"companyName": "北京奇点餐饮有限公司",
	"periodicType": "WEEK",
	"weekIndex": "3",
	"startDay": "",
	"dayCount": "",
	"note": "待定",
	"effectStartDate": "2019-05-16",
	"EffectEndDate": "2019-08-16"
}






url = 'http://'+ip+':8867/pos/push' #push
data={
	"cid": "123456",
	"companyName": "北京奇点餐饮有限公司",
	"data": [{
		"did": "11",
		"gmtBill": "2019-05-16 12:03:22",
		"gmtTurnover": "2019-05-16 12:03:33",
		"money": "280.00",
		"peoples": "3",
		"singleSales": "80",
		"payment": "现金",
		"deviceCode": "A1",
		"orderNo": "002847306ac359f6016ac3cdd4c10368"
	}, {
		"did": "11",
		"gmtBill": "2019-05-17 11:03:36",
		"gmtTurnover": "2019-05-17 11:03:36",
		"money": "170.50",
		"peoples": "2",
		"singleSales": "50",
		"payment": "现金",
		"deviceCode": "A1",
		"orderNo": "002847306ac359f6016ac3beb3d602dc"
	}]
}

head = {"Content-Type": "application/json; charset=UTF-8", 'Connection': 'close'}



#curl -H "Content-Type:application/json" -X POST --data '{"cid":"123456","companyName":"北京奇点餐饮有限公司","data":[{"did":"11","gmtBill":"2019-05-1612:03:22","gmtTurnover":"2019-05-1612:03:33","money":"280.00","peoples":"3","singleSales":"80","payment":"现金","deviceCode":"A1","orderNo":"002847306ac359f6016ac3cdd4c10368"},{"did":"11","gmtBill":"2019-05-1711:03:36","gmtTurnover":"2019-05-1711:03:36","money":"170.50","peoples":"2","singleSales":"50","payment":"现金","deviceCode":"A1","orderNo":"002847306ac359f6016ac3beb3d602dc"}]}' http://127.0.0.1:8867/pos/push



url  = 'http://'+ip+':8867/pos/result'
data = {
    "predictType":1,
    "cycleLenth":7,
    "did":6,
    "startPreDay":"2019-07-23",
    "preType":"trueGMV",
    "cycles":2,
    "cyclesCoef":"0.2,0.5",
    "smoothCoef":0.5
}




#r = requests.post(url, bytes(parse.urlencode(data),encoding = 'utf8'),headers=head)
r = requests.post(url, data=data,headers=head)
print(r.text)
