create table `labor_shift_split_rule`
(
	`auto_id` int auto_increment primary key comment '自增主键',
	`bid` varchar(32) not null comment '业务id',
	`cid` varchar(32) not null comment '公司id',
	`did` varchar(32) not null comment '部门id',
    `opt` varchar(32) DEFAULT '' not null comment '操作类型（modify， delete)',
    `ruleCalType` varchar(256) DEFAULT '' comment '规则计算类型（目前有三种：interval，shiftNum, shiftLen，worktime)',
    `ruleCpType` varchar(256) DEFAULT '' not null comment '比较类型（lt, le, eq, ge, gt。小于，小于等于，等于， 大于等于，大于)',
    `ruleCpNum` varchar(256) DEFAULT '' not null comment '比较数值 分钟数',
    `dayFusion` boolean DEFAULT true not null comment 'true 跨天融合 班次可跨天， 班段跨天计算',
    `create_time` datetime default '1997-01-01 00:00:00' not null comment '创建时间',
	`update_time` datetime default '1997-01-01 00:00:00' not null comment '更新时间',
	`status` int default 1 not null comment '状态1 可用 0 不可用'
);