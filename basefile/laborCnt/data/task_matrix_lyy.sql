create table `task_matrix_lyy`
(
	`auto_id` int auto_increment primary key comment '自增主键',
	`cid` varchar(32) not null comment '公司id',
	`did` varchar(32) not null comment '部门id',
	`data_type` varchar(32) not null comment '类型：min full max',
	`forecastType` varchar(32) not null comment '预测类型（任务劳动人数：0、岗位劳动人数：1、排班劳动人数：2）',
	`forecast_date` varchar(32) not null comment '预测日期',
	`task_matrix` MEDIUMTEXT not null comment '任务排班矩阵',
	`id_li` MEDIUMTEXT comment '可组合任务列表',
	`split_rule` MEDIUMTEXT comment '规则字典',
	`indirect_task` MEDIUMTEXT comment '间接任务',
    `create_time` datetime default '1997-01-01 00:00:00' not null comment '创建时间',
	`update_time` datetime default '1997-01-01 00:00:00' not null comment '更新时间',
	`status` int default 1 not null comment '状态1 可用 0 不可用'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;