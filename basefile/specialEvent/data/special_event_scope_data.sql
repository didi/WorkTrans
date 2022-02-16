create table special_event_scope_data
(
	auto_id int auto_increment primary key comment '自增主键',
	bid varchar(32) default '' not null comment '业务id',
	cid varchar(32) default '' not null comment '公司id',
	event_bid varchar(32) default '' not null comment '事件bid',
	did_arr longtext comment '部门数组',
	goods_arr longtext comment '商品数组',
	start_time datetime comment '开始时间',
	end_time datetime comment '结束时间',
	create_time datetime comment '创建时间',
	update_time datetime comment '修改时间'
)ENGINE=InnoDB DEFAULT CHARSET=utf8;