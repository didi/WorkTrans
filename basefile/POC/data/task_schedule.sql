CREATE TABLE `task_schedule` (
  `autoid` int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  `cid` varchar(32)  NOT NULL COMMENT '公司id',
  `did` varchar(32) NOT NULL COMMENT '部门id',
  `applyId` varchar(32)  COMMENT '获取结果生成ID',
  `eid` varchar(32)  NOT NULL COMMENT '用户ID',
  `schDay` varchar(32) NOT NULL COMMENT '排班天yyyy-MM-dd',
  `allWorkTime` varchar(32)  DEFAULT NULL COMMENT '当天排班工时  分钟数',
  `type` varchar(32)  NOT NULL COMMENT '类型 task：任务',
  `outId` varchar(32)  NOT NULL COMMENT '工作单元对应ID （类型为task，此ID为任务ID）',
  `shiftId` varchar(32) not null comment '班次id',
  `startTime` varchar(32) NOT NULL COMMENT '开始时间yyyy-MM-dd hh:mm',
  `endTime` varchar(32) NOT NULL COMMENT '结束时间yyyy-MM-dd hh:mm',
  `workTime` varchar(32) DEFAULT NULL COMMENT '工作单元（分钟数）',
  `agthtype` VARCHAR(32) NULL COMMENT '使用的算法' ,
  `shiftType` VARCHAR(32) NULL COMMENT '班次类别（worktime(工时最少), emp（人员最少）, effect（时效最优）, violation（违反规则较少）， fillRate(满足率)）',
  `create_time` varchar(32) DEFAULT NULL COMMENT '创建时间',
  `update_time` varchar(32) DEFAULT NULL COMMENT '修改时间',
  `status` int(11) NOT NULL DEFAULT 1 COMMENT '状态（1：有效，0：无效',
  `scheme_type` varchar(32) DEFAULT NULL
)ENGINE=InnoDB DEFAULT CHARSET=utf8 ;




alter table task_schedule add `did` varchar(32) NOT NULL DEFAULT '' COMMENT '部门id';


