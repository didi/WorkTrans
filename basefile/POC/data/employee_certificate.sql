CREATE TABLE employee_certificate (
  `auto_id` INT auto_increment NOT NULL primary key COMMENT '自增主键',
  `cid` VARCHAR(32) NOT NULL DEFAULT '' COMMENT '公司id',
  `eid` VARCHAR(32) NOT NULL DEFAULT '' COMMENT '员工id',
  `opt` VARCHAR(32) NOT NULL DEFAULT '' COMMENT '操作类型（modify， delete）',
  `certname` VARCHAR(256) NOT NULL DEFAULT '' COMMENT '证书名字',
  `closingdate` DATE NOT NULL COMMENT '截止日期',
  `create_time` datetime comment '创建时间',
  `update_time` datetime comment '修改时间',
  `status` INT NOT NULL DEFAULT 1 COMMENT '状态（1：有效，0：无效）'
)ENGINE=InnoDB DEFAULT CHARSET=utf8 ;
