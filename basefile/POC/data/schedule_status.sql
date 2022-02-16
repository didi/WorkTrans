CREATE TABLE `woqu`.`schedule_status` (
  `auto_id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '自增id',
  `applyId` VARCHAR(32) NOT NULL COMMENT '获取结果生成id',
  `status` INT NOT NULL COMMENT '使用状态（0：不可用，1：可用）',
  `date` VARCHAR(32) NOT NULL COMMENT '日期',
  `create_time` DATETIME NOT NULL COMMENT '创建时间',
  `update_time` DATETIME NOT NULL COMMENT '更改时间',
  `scheme_type` varchar(32) DEFAULT NULL,
  `condition` VARCHAR(32) NOT NULL COMMENT '排班状态（success：排班成功，running：正在运行）'
)   ENGINE=InnoDB DEFAULT CHARSET=utf8 ;