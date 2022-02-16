create table `task_matrix_ss`
(
	`auto_id` int auto_increment primary key comment '自增主键',
	`cid` varchar(32) not null comment '公司id',
	`did` varchar(32) not null comment '部门id',
	`forecastType` varchar(32) not null comment '预测类型（任务劳动人数：0、岗位劳动人数：1、排班劳动人数：2',
	`type` varchar(32) not null comment '类型：min full max',
	`forecast_date` varchar(32) not null comment '预测日期',
	`start_time` varchar(32) default '00:00' comment '开始时间',
	`end_time` varchar(32) default '23:59' comment '结束时间',
	`task_matrix` MEDIUMTEXT not null comment '任务排班矩阵',
	`update_time` datetime default '1997-01-01 00:00:00' not null comment '更新时间',
	`status` int default 1 not null comment '状态1 可用 0 不可用'
)ENGINE=InnoDB DEFAULT CHARSET=utf8;