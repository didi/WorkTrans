create table labor_standard
(
	auto_id int auto_increment primary key comment '自增主键',
	bid varchar(32) comment '业务id',
	cid varchar(32) comment '公司id',
	mode varchar(32) comment '模式：单类型或者多类型（single、multi）',
	masterType varchar(256) comment '第一业务类型（交易笔数、营业额等）',
	slaveType varchar(256) comment '第二业务类型（交易笔数、营业额等）',
	detailRank int default 1 not null comment '标准详情的序号',
	masterTypeScale VARCHAR(256) comment '标准详情的第一业务类型刻度值（有可能是小数）',
	slaveTypeScale varchar(256) comment '标准详情的第二业务类型刻度值（有可能是小数）',
	worktimeMinute int default 0 not null comment '标准业务单位时间：分钟数',
	create_time datetime default current_timestamp() not null comment '创建时间',
	update_time datetime default current_timestamp() on update current_timestamp() not null comment '修改时间',
	status int default 1 not null comment '状态'
);



create table labor_cacl_value
(
	auto_id int auto_increment primary key comment '自增主键',
	cid varchar(32) default ''  comment '公司id',
	did varchar(32) default ''  comment '门店id',
    forecastType varchar(32) default ''   comment '预测类型 task、node',
    forecastStandard varchar(32) default ''  COMMENT '营业额：turnover、交易笔数：order_num',

    dayStr varchar(32) default ''  comment '2019-07-15',
	startTimeStr varchar(32) default ''  comment '开始时间 hh:[00-15-30-45]',
	endTimeStr varchar(32) default ''  comment '结束时间 hh:[00-15-30-45]',

    nodeBid varchar(32) default ''   COMMENT '节点bid',
    nodeStandardBid  varchar(32) default ''   COMMENT '节点的劳动力标准bid',
	taskBid  varchar(32) default '' comment '任务bid',
	laborStandardBid varchar(32) default '' comment '任务的劳动力标准的bid',

	caclValue double default 0 comment '计算的劳动力个数',
    forecastValue double default 0  comment '预测的劳动力个数',
    editValue double default 0 comment '手工修改的劳动力个数',

    inserttime datetime default current_timestamp() not null comment '创建时间',
    updatetime datetime default current_timestamp() on update current_timestamp() not null comment '修改时间',
	status int default 1 not null comment '状态 1 可用 0不可用'

)ENGINE=InnoDB DEFAULT CHARSET=utf8 ;





 alter table labor_cacl_value add min_caclValue double;
 alter table labor_cacl_value add max_caclValue double;


















