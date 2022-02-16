create table labor_comb_rule
(
	auto_id int auto_increment primary key comment '自增主键',
	cid varchar(32) comment '公司id',
	bid varchar(32) comment '业务id',
	did varchar(32) comment '部门id',
	rule_data varchar(340) default '' comment '关联规则',
	create_time datetime default '1997-01-01 00:00:00' not null comment '创建时间',
	update_time datetime default '1997-01-01 00:00:00' not null comment '修改时间',
	status int default 1 not null comment '状态 1可用 0不可用'
)ENGINE=InnoDB DEFAULT CHARSET=utf8;