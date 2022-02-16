CREATE TABLE `user_login_log`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `login_user` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_croatian_ci NULL DEFAULT NULL COMMENT '登陆用户名',
  `login_user_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_croatian_ci NOT NULL COMMENT '登陆ID',
  `insert_time` datetime(0) NOT NULL COMMENT '登陆时间， 创建时间',
  `ip` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_croatian_ci NULL DEFAULT NULL,
  `login_time` int(8) NOT NULL DEFAULT 1 COMMENT '登陆次数',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_user_login`(`login_user_id`, `insert_time`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_croatian_ci ROW_FORMAT = Dynamic;