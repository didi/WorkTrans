create table `sch_available_time`(
    `auto_id` int auto_increment primary key comment '自增主键',
    `cid` varchar(32) default '' not null comment '公司id',
    `eid` varchar(32) default '' not null comment '用户id',
    `opt` varchar(32) default '' not null comment '操作类型（modify， delete）',
    `type` varchar(2) default '' not null comment '0: 全天可排， 1 ：全天不可排， 2 部分时间可排。部',
    `start` time default NULL comment '工作时间开始（HH:mm)',
    `end` time  default NULL comment '工作时间结束（HH:mm）',
    `day` date comment '日期yyyy-MM-dd',
    `create_time` datetime comment '创建时间',
	`update_time` datetime comment '修改时间',
	`status` int default 1 not null comment '状态0 无效 状态1 生效'
);