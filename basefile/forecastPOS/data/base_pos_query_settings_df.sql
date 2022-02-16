-- MySQL dump 10.13  Distrib 8.0.11, for macos10.13 (x86_64)
--
-- Host: 127.0.0.1    Database: woqu
-- ------------------------------------------------------
-- Server version	8.0.11

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
 SET NAMES utf8mb4 ;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `base_pos_query_settings_df`
--

DROP TABLE IF EXISTS `base_pos_query_settings_df`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `base_pos_query_settings_df` (
  `cid` int(10) DEFAULT NULL COMMENT '是 string 客户公司id',
  `companyName` varchar(100) DEFAULT NULL COMMENT '否 string 客户公司名称',
  `periodicType` varchar(20) DEFAULT NULL COMMENT '是 String 按周预测或者自定义预测；WEEK表示按周，CUSTOM表示自定义预测',
  `weekIndex` int(1) DEFAULT NULL COMMENT '否 Integer 按周预测时，从周几开始，0表示周日，1表示周一等',
  `startDay` varchar(100) DEFAULT NULL COMMENT '否 String 开始日期，用于自定义预测',
  `dayCount` int(3) DEFAULT NULL COMMENT '否 Integer 周期天数，用于自定义预测',
  `note` varchar(100) DEFAULT NULL COMMENT '预测算法参数',
  `effectStartDate` varchar(20) DEFAULT NULL COMMENT '是 String 生效开始日期',
  `EffectEndDate` varchar(20) DEFAULT NULL COMMENT '否 String 生效结束日期，如果不设置，则为永久，不限制结束时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `base_pos_query_settings_df`
--

LOCK TABLES `base_pos_query_settings_df` WRITE;
/*!40000 ALTER TABLE `base_pos_query_settings_df` DISABLE KEYS */;
/*!40000 ALTER TABLE `base_pos_query_settings_df` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-08-02 14:38:19
