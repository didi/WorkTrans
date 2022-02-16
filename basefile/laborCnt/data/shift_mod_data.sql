create table shift_mod_data
(
	auto_id int auto_increment primary key comment '自增主键',
	bid varchar(32) default '' not null comment '预测人数业务id',
	cid varchar(32) default '' not null comment '公司id',
	did varchar(32) default '' not null comment '部门id',
	shiftbid varchar(32) default '' not null comment '班次bid',
	shift_start time comment '班次开始时间(HH:mm)',
	shift_end time comment '班次结束时间(HH:mm)',
	is_cross_day bool default false not null comment '是否跨天',
	create_time datetime comment '创建时间',
	update_time datetime comment '修改时间',
	status int default 1 not null comment '状态'
);