create table emp_skill(
    auto_id int auto_increment primary key comment '自增主键',
    cid varchar(32) default '' not null comment '公司id',
    eid varchar(32) default '' not null comment '员工id',
    skill varchar(40) default '' not null comment '员工技能',
    skillNum varchar(32) default '' not null comment '员工技能值',
    opt varchar(32) default '' not null comment '操作类型（update， delete）',
    create_time datetime comment '创建时间',
	update_time datetime comment '修改时间',
	status int default 1 not null comment '状态（1：有效，0：无效）'
);