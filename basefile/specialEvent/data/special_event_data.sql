create table special_event_data
(
	auto_id int auto_increment primary key comment '自增主键',
	bid varchar(32) default '' not null comment '业务id',
	cid varchar(32) default '' not null comment '公司id',
	did varchar(32) default '' not null comment '部门id',
	-- event_id varchar(32) default '' not null comment '事件id',
	event_name varchar(64) default '' comment '事件名称',
	event_start datetime comment '开始时间',
	event_end datetime comment '结束时间',
	create_time datetime comment '创建时间',
	update_time datetime comment '修改时间',
	status int default 1 not null comment '状态 0：删除，1：正常'
)ENGINE=InnoDB DEFAULT CHARSET=utf8;