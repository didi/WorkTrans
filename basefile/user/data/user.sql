CREATE TABLE `user`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `insert_time` datetime(0) NOT NULL,
  `update_time` datetime(0) NOT NULL ON UPDATE CURRENT_TIMESTAMP(0),
  `username` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_croatian_ci NOT NULL DEFAULT '',
  `password` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_croatian_ci NOT NULL,
  `name` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_croatian_ci NULL DEFAULT NULL,
  `user_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_croatian_ci NOT NULL,
  `is_admin` tinyint(1) NOT NULL,
  `gro_name` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_croatian_ci NULL DEFAULT NULL,
  `status` int(2) NULL DEFAULT NULL COMMENT '1 开通， 0 无效',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `userprofile_username`(`username`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_croatian_ci ROW_FORMAT = Dynamic;