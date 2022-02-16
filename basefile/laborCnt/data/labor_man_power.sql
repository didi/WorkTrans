create table `labor_man_power`
(
	`auto_id` int auto_increment primary key comment '自增主键',
	`cid` varchar(32) not null comment '公司id',
	`did` varchar(32) not null comment '部门id',
	`forecastType` varchar(32) not null comment '预测类型（任务劳动人数：0、岗位劳动人数：1、排班劳动人数：2）',
	`forecast_date` varchar(32) not null comment '预测日期',
    `combiRule` varchar(256) DEFAULT '' comment '组合规则key(bid，逗号隔开)',
    `combiRuleNewVal` varchar(256) DEFAULT '' not null comment '修改值',
    `combiRuleOldVal` varchar(256) DEFAULT '' not null comment '修改前的值',
    `combiRuleCalcVal` varchar(256) DEFAULT '' not null comment '预测出的计算值',
    `resultMethod` varchar(256) DEFAULT '' not null comment '结果所属对象，0 lyy, 1 ss',
    `create_time` datetime default '1997-01-01 00:00:00' not null comment '创建时间',
	`update_time` datetime default '1997-01-01 00:00:00' not null comment '更新时间',
	`status` int default 1 not null comment '状态1 可用 0 不可用'
);