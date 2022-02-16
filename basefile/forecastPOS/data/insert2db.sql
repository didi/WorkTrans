

10.86.60.67


10.86.53.56
10.86.53.57
10.86.53.58
10.86.53.59
10.86.53.60






create table base_pos_df
(
id bigint comment "Id主键",
bid VARCHAR(40) comment "业务id",
gmt_create VARCHAR(40) comment "创建时间",
gmt_modified VARCHAR(40) comment "最后修改时间",
status int(4) comment "记录状态",
cid  VARCHAR(40) comment "公司ID",
did  VARCHAR(40)  comment "部门ID",
gmt_bill  VARCHAR(40) comment "开单时间",
gmt_trunover VARCHAR(40)  comment "营业结算时间",
money  int(6) comment "营业额-实际数据",
data_value  int(6)  comment "营业额",
bill_year int(4) comment "开单时间-年",
bill_month int(2) comment "开单时间-月",
bill_day int(2) comment "开单时间-日",
bill_hour int(2) comment "开单时间-时",
bill_minute int(2) comment "开单时间-分",
operator_eid VARCHAR(10) comment "导入人",
peoples int(6) comment "人数",
use_type VARCHAR(10) comment "产品使用类型：堂吃|外卖",
order_no VARCHAR(50) comment "订单编号",
source_data VARCHAR(30) comment "数据来源",
tc_count VARCHAR(10) comment "tc统计"
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


alter  table base_pos_df add column (companyName VARCHAR(100) comment "公司名称");
alter  table base_pos_df add column (singleSales int(5) comment "单品销量");

alter  table base_pos_df add column (payment VARCHAR(30) comment "支付方式");
alter  table base_pos_df add column (deviceCode VARCHAR(30) comment "收银台ID");


companyName
singleSales
payment
deviceCode


{

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



import pymysql
#import datetime
#day = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')#参数值插入时间
db = pymysql.connect(host='服务器IP', user='账号', passwd='密码', port=端口号)
cur = db.cursor()
cur.execute('use 数据库')
#批量创建测试账号

usersvalues=[]
for i in range(1,5):
  usersvalues.append(('参数值1'+str(i),'参数值2'))

#批量插入数据
cur.executemany('insert into base_pos_df(cid,companyName,did,gmt_bill,gmt_trunover,money,data_value,peoples,singleSales,payment,deviceCode,orderNo) value(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', usersvalues)
#修改数据（查询和删除数据同）
cur.execute("update 表名 set 参数名='参数更新值' where 条件名='条件值'")



load data infile "/Users/didi/work/web/tob/woqu/forecastPOS/data/20190729b.csv" replace into table base_pos_df fields terminated by',' ;

10359810,,21/3/2019 05:00:04,21/3/2019 05:00:04,0,102672,44,20/3/2019 18:50:06,20/3/2019 19:33:49,204.0,20400,2019,3,20,18,50,,3,lobby,00284730696b95a001699ab8f1861c84,fire2d,
10359811,,21/3/2019 05:00:04,21/3/2019 05:00:04,0,102672,44,20/3/2019 17:16:46,20/3/2019 17:57:15,308.0,30800,2019,3,20,17,16,,2,lobby,00284730696b95a301699a637f5e67df,fire2d,



create table ref_date_flag(
flagTday VARCHAR(10) comment "日期",
flagTstart VARCHAR(5) comment "开始时刻  00:00",
flagTend VARCHAR(5) comment "结束时间 00:15"
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



/usr/local/bin/python3.6 /Users/didi/work/web/tob/woqu/utils/genkey.py > ref_date_flag.csv
:%s/23:45 00:00/23:45 23:60/g
load data infile "/Users/didi/work/web/tob/woqu/utils/ref_date_flag.csv" replace into table ref_date_flag fields terminated by',' ;


每天每个15分钟的




create table view_pos_df
(
cid VARCHAR(40) comment "公司ID",
did  VARCHAR(40) comment "部门ID",
shike  VARCHAR(16) comment "15min一个 2019-01-01 00:15",
trueGMV        bigint(30)  comment '真实流水',     
predictGMV     bigint(30)  comment '预测流水',
adjustGMV      bigint(30)  comment '调整流水',
truePeoples    int(3)  comment '真实人数',
predictPeoples int(3)  comment '预测人数',
adjustPeoples  int(3)  comment '调整人数'
)ENGINE=InnoDB DEFAULT CHARSET=utf8;




alter table view_pos_df change cid did VARCHAR(40) comment "公司ID";
alter table view_pos_df change bid cid VARCHAR(40) comment "部门ID";
alter table view_pos_df add column(status int(1) comment "有效状态");
update view_pos_df set status=0;



 alter table view_pos_df add  column(trueOrders int(1) comment "真实订单量");
 alter table view_pos_df add  column(predictOrders int(1) comment "预测的订单量");
 alter table view_pos_df add  column(adjustOrders int(1) comment "调整的订单量");




delete from view_pos_df where status>0;

explain
insert into  view_pos_df 
select
 b.cid
,b.did
,a.shike
,sum(IFNULL( if(b.ft>=a.flagTstart and b.ft<a.flagTend,b.data_value,0) ,0)) as trueGMV
,0 as predictGMV
,0 as adjustGMV
,sum(IFNULL( if(b.ft>=a.flagTstart and b.ft<a.flagTend,b.peoples,0) ,0)) as truePeoples
,0 as predictPeoples
,0 as adjustPeoples
,5 as status
,current_timestamp as insertTime
,current_timestamp as updateTime
,count(distinct if(b.ft>=a.flagTstart and b.ft<a.flagTend,b.order_no,null)) as trueOrders
,0 as predictOrders
,0 as adjustOrders
from (
   select 
       flagTday as fd,flagTstart,flagTend,CONCAT_WS(' ',flagTday,flagTstart) as shike
   from ref_date_flag 
   where flagTday>= '2018-06-21' and flagTday<='2019-07-29'

) a
 left outer join
 (select
 cid,did,data_value,peoples,order_no,
  CONCAT_WS('-',bill_year,LPAD(bill_month, 2, 0) ,LPAD(bill_day, 2, 0)  ) as fd,
  CONCAT_WS(':',LPAD(bill_hour, 2, 0) ,LPAD(bill_minute, 2, 0) ) as ft
 from base_pos_df where aistatus=1 and did is not null ) b
 on a.fd=b.fd
 group by
 b.cid
,b.did
,a.shike;





left outer join
(
   select    
   cid
   ,did
   ,shike
   ,trueGMV
   ,truePeoples
   ,substr(shike,1,10) as fd
   from view_pos_df 
   where status=0 and substr(shike,1,10)='2018-11-08' and did = 53
) b 
on a.shike=b.shike ;



+----------------+-------------+------+-----+---------+-------+
| Field          | Type        | Null | Key | Default | Extra |
+----------------+-------------+------+-----+---------+-------+
| cid            | varchar(40) | YES  |     | NULL    |       |
| did            | varchar(40) | YES  |     | NULL    |       |
| shike          | varchar(16) | YES  |     | NULL    |       |
| trueGMV        | bigint(30)  | YES  |     | NULL    |       |
| predictGMV     | bigint(30)  | YES  |     | NULL    |       |
| adjustGMV      | bigint(30)  | YES  |     | NULL    |       |
| truePeoples    | int(3)      | YES  |     | NULL    |       |
| predictPeoples | int(3)      | YES  |     | NULL    |       |
| adjustPeoples  | int(3)      | YES  |     | NULL    |       |
| status         | int(1)      | YES  |     | NULL    |       |
| insertTime     | varchar(20) | YES  |     | NULL    |       |
| updateTime     | varchar(20) | YES  |     | NULL    |       |
+----------------+-------------+------+-----+---------+-------+


insert into  view_pos_df
select
 c.cid
,c.did
,a.shike
,sum(c.data_value) as trueGMV
,0 as predictGMV
,0 as adjustGMV
,sum(c.peoples) as truePeoples
,0 as predictPeoples
,0 as adjustPeoples
,1 as status
,current_timestamp as insertTime
,'2019-05-06' as updateTime
from (
   select
       flagTday as fd,flagTstart,flagTend,CONCAT_WS(' ',flagTday,flagTstart) as shike
   from ref_date_flag
   where flagTday= '2019-05-06'

) a
 left outer join
 (select  cid,did from base_pos_df where substr(gmt_bill,1,10)='2019-05-06'  group by cid,did ) c
 on c.





#todo
#todo
#todo
#todo
#todo
#todo



update view_pos_df set  status=0 where updateTime='2019-05-06';
insert into  view_pos_df
select
cid,did,
CONCAT_WS(' ',a.fd,a.flagTstart) as shike,
sum(if(b.ft>=a.flagTstart and b.ft<a.flagTend,b.gmv,0)) as trueGMV,
0 as predictGMV,
0 as adjustGMV,
sum(if(b.ft>=a.flagTstart and b.ft<a.flagTend,b.peoples,0)) as truePeoples,
0 as predictPeoples,
0 as adjustPeoples
,1 as status
,current_timestamp as insertTime
,'2019-05-06' as updateTime
from(
   select
       flagTday as fd,flagTstart,flagTend
   from ref_date_flag
   where flagTday='2019-07-08'
) a left outer join
(
   select cid,did,CONCAT_WS('-',bill_year,LPAD(bill_month, 2, 0) ,LPAD(bill_day, 2, 0)  ) as fd,
   CONCAT_WS(':',LPAD(bill_hour, 2, 0) ,LPAD(bill_minute, 2, 0) ) as ft,
   data_value  as gmv ,
   peoples
   from base_pos_df
   where CONCAT_WS('-',bill_year,LPAD(bill_month, 2, 0) ,LPAD(bill_day, 2, 0)  )='2019-07-08'
) b
on a.fd=b.fd
group by cid,did,CONCAT_WS(' ',a.fd,a.flagTstart) ;








select
sum(data_value),sum(peoples)
from
base_pos_df
   where CONCAT_WS('-',bill_year,LPAD(bill_month, 2, 0) ,LPAD(bill_day, 2, 0)  )='2019-07-08';

select
     shike,trueGMV as value
from  view_pos_df
where did='%s' and shike>='%s' and shike<'%s'

mysql> desc view_pos_df;
+----------------+-------------+------+-----+---------+-------+
| Field          | Type        | Null | Key | Default | Extra |
+----------------+-------------+------+-----+---------+-------+
| cid            | varchar(40) | YES  |     | NULL    |       |
| did            | varchar(40) | YES  |     | NULL    |       |
| shike          | varchar(16) | YES  |     | NULL    |       |
| trueGMV        | bigint(30)  | YES  |     | NULL    |       |
| predictGMV     | bigint(30)  | YES  |     | NULL    |       |
| adjustGMV      | bigint(30)  | YES  |     | NULL    |       |
| truePeoples    | int(3)      | YES  |     | NULL    |       |
| predictPeoples | int(3)      | YES  |     | NULL    |       |
| adjustPeoples  | int(3)      | YES  |     | NULL    |       |
| status         | int(1)      | YES  |     | NULL    |       |
+----------------+-------------+------+-----+---------+-------+
10 rows in set (0.00 sec)


insert into  view_pos_df 
select 
c.cid,
c.did,
a.shike,
IFNULL(b.trueGMV,0)  as trueGMV,
0 as predictGMV,
0 as adjustGMV,
IFNULL(b.truePeoples,0)  as truePeoples,
0 as predictPeoples,
0 as adjustPeoples,
6 as  status
from (
   select 
       flagTday as fd,flagTstart,flagTend,CONCAT_WS(' ',flagTday,flagTstart) as shike,1 as m
   from ref_date_flag 
   where flagTday='2018-11-08'
) a
left outer join
(select  cid,did,1 as m from base_pos_df   group by cid,did ) c  on a.m=c.m 
left outer join
(
   select    
   cid
   ,did
   ,shike
   ,trueGMV
   ,truePeoples
   ,substr(shike,1,10) as fd
   from view_pos_df 
   where status=0 and substr(shike,1,10)='2018-11-08' and did = 53
) b 
on a.shike=b.shike and c.cid=b.cid and c.did=b.did ;



flagTday>='2018-01-01' and flagTday<='2019-07-27'





SELECT * FROM view_pos_df WHERE status=3;




检查每个时间点的量
select status,substr(shike,1,10),count(1) as cnt from view_pos_df where did='53'  group by status,substr(shike,1,10) having cnt!=96;



检查每个时间点的量
select status,substr(shike,1,10),count(1) as cnt from view_pos_df where did='53' and status=6  group by status,substr(shike,1,10);


TODO：
既然有些时间点是空的
那就是需要在读DB时候填充
那么塞入view_pos_df表的数据就不用中间表了？【再斟酌】





predictParam









--


select
   did,
   count(distinct substr(shike,1,10)),
   count(distinct substr(shike,1,10))*96,
   count(distinct shike)
from view_pos_df
where status=0
group by did;






insert into  view_pos_df 
select 
cid,did,CONCAT_WS(' ',a.fd,a.flagTstart) as shike,
sum(if(b.ft>=a.flagTstart and b.ft<a.flagTend,b.gmv,0)) as trueGMV,
0 as predictGMV,
0 as adjustGMV,
sum(if(b.ft>=a.flagTstart and b.ft<a.flagTend,b.peoples,0)) as truePeoples,
0 as predictPeoples,
0 as adjustPeoples
from(
   select 
       flagTday as fd,flagTstart,flagTend
   from ref_date_flag 
) a left outer join
(
   select cid,did,CONCAT_WS('-',bill_year,LPAD(bill_month, 2, 0) ,LPAD(bill_day, 2, 0)  ) as fd, 
   CONCAT_WS(':',LPAD(bill_hour, 2, 0) ,LPAD(bill_minute, 2, 0) ) as ft, 
   data_value  as gmv ,
   peoples     
   from base_pos_df 
) b 
on a.fd=b.fd 
group by cid,did,CONCAT_WS(' ',a.fd,a.flagTstart) ;


order by CONCAT_WS(' ',a.fd,a.flagTstart) asc




desc ref_date_flag;








Query OK, 183067 rows affected (4 hours 14 min 1.68 sec)
Records: 183067  Duplicates: 0  Warnings: 0


view_pos_df

select 
shike,sum(1) as a 
from view_pos_df
group by shike
having a>=2
order by shike asc;





18344385400----qja04253


tornado+pymysql



Django：重量级web框架，功能大而全，注重高效开发 
内置管理后台 
内置封装完善的ORM操作 
session功能 
后台管理 
缺陷：高耦合

Tornado：轻量级web框架，功能少而精，注重性能优越 
HTTP服务器 
出色的抗负载能力
异步编程,异步非阻塞IO处理方式
优异的处理性能，不依赖多进程/多线程，一定程度上解决C10K问题
WebSocket 
缺陷：入门门槛较高



第一周：离线训练  



其中：
加权平均、移动平滑 调用时计算
时空预测／AI模型 每周训练一次模型


（如果任何环节有拖延，则周末加班）





select 
CONCAT_WS('-',bill_year,LPAD(bill_month, 2, 0) ,LPAD(bill_day, 2, 0)  ) as fd, 
CONCAT_WS(':',LPAD(bill_hour, 2, 0) ,LPAD(bill_minute, 2, 0) ) as ft, 
   data_value
from  base_pos_df where did=6 and  bill_year=2019 and bill_month=07 and bill_day=04









 flagTend

CREATE TABLE IF NOT EXISTS `csj_tbl`(
   `csj_id` INT UNSIGNED AUTO_INCREMENT,
   `csj_title` VARCHAR(100) NOT NULL,
   `csj_author` VARCHAR(40) NOT NULL,
   `submission_date` DATE,
   PRIMARY KEY ( `csj_id` )
)






---- modify逻辑 ----
select
*
from base_pos_df
where
cid='123456'
and did=11
and concat(substr(gmt_bill,1,14),LPAD(floor(bill_minute/15),2,0))='2019-05-16 12:00'
and aistatus=1;

select * from view_pos_df where  cid='123456' and did=11 and shike='2019-05-16 12:00';




update view_pos_df set status=0,updateTime=current_timestamp  where cid=%s and did=%s and shike=%s


update view_pos_df set status=0,updateTime=current_timestamp  where cid='123456' and did=11 and shike='2019-05-16 12:00'


insert into  view_pos_df
select
cid,
did,
concat(substr(gmt_bill,1,14),LPAD(floor(bill_minute/15),2,0))  as shike,
sum(IFNULL(data_value,0)) as trueGMV,0 as predictGMV,0 as adjustGMV,
sum(IFNULL(peoples,0)) as truePeoples,0 as predictPeoples,0 as adjustPeoples,
1 as status,
current_timestamp as insertTime,
current_timestamp as updateTime,
count(distinct order_no) as trueOrders,
0 as predictOrders,
0 as adjustOrders
from base_pos_df
where
cid='123456'
and did=11
and concat(substr(gmt_bill,1,14),LPAD(floor(bill_minute/15),2,0))='2019-05-16 12:00'
and aistatus=1
group by cid,
did,
concat(substr(gmt_bill,1,14),LPAD(floor(bill_minute/15),2,0));




insert into  view_pos_df
select
cid,did,
CONCAT_WS(' ',a.fd,a.flagTstart) as shike,
sum(if(b.ft>=a.flagTstart and b.ft<a.flagTend,b.gmv,0)) as trueGMV,
0 as predictGMV,
0 as adjustGMV,
sum(if(b.ft>=a.flagTstart and b.ft<a.flagTend,b.peoples,0)) as truePeoples,
0 as predictPeoples,
0 as adjustPeoples
,1 as status
,current_timestamp as insertTime
,'2019-05-06' as updateTime
from(
   select
       flagTday as fd,flagTstart,flagTend
   from ref_date_flag
   where flagTday='2019-07-08'
) a left outer join
(
   select cid,did,CONCAT_WS('-',bill_year,LPAD(bill_month, 2, 0) ,LPAD(bill_day, 2, 0)  ) as fd,
   CONCAT_WS(':',LPAD(bill_hour, 2, 0) ,LPAD(bill_minute, 2, 0) ) as ft,
   data_value  as gmv ,
   peoples
   from base_pos_df
   where CONCAT_WS('-',bill_year,LPAD(bill_month, 2, 0) ,LPAD(bill_day, 2, 0)  )='2019-07-08'
) b
on a.fd=b.fd
group by cid,did,CONCAT_WS(' ',a.fd,a.flagTstart) ;







脚本插入
insert into  view_pos_df
select
cid,
did,
concat(substr(gmt_bill,1,14),LPAD(floor(bill_minute/15),2,0))  as shike,
sum(IFNULL(data_value,0)) as trueGMV,0 as predictGMV,0 as adjustGMV,
sum(IFNULL(peoples,0)) as truePeoples,0 as predictPeoples,0 as adjustPeoples,
1 as status,
current_timestamp as insertTime,
current_timestamp as updateTime,
count(distinct order_no) as trueOrders,
0 as predictOrders,
0 as adjustOrders
from base_pos_df
where
substr(gmt_bill,1,10)=''
and aistatus=1
group by cid,
did,
concat(substr(gmt_bill,1,14),LPAD(floor(bill_minute/15),2,0));

