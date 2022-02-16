create table emp_matchpro(
    auto_id int auto_increment primary key comment '自增主键',
    cid varchar(32) default '' not null comment '公司id',
    bid varchar(32) default '' not null comment '业务id',
    did varchar(32) default '' not null comment '部门id',
    opt varchar(32) default '' not null comment '操作类型（update， delete）',
    weight varchar(32) default '' not null comment '优先级',
    ruleGroup varchar(32) default '' not null comment '规则类型组',
    ruleDesc varchar(32) default '' comment '规则描述',
    ruleCpType varchar(32) default '' not null comment '比较类型',
    ruletag varchar(32) default '' not null comment '规则类型',
    ruleCpNum varchar(32) default '' not null comment '比较数值',
    create_time datetime comment '创建时间',
	update_time datetime comment '修改时间',
	status int default 1 not null comment '状态0 无效  1 有效'
)ENGINE=InnoDB DEFAULT CHARSET=utf8;