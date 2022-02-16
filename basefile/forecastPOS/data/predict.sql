


INSERT INTO view_pos_df
SELECT cid, did
	, concat(substr(gmt_bill, 1, 14), LPAD(floor(bill_minute / 15), 2, 0)) AS shike
	, SUM(IFNULL(data_value, 0)) AS trueGMV
	, 0 AS predictGMV, 0 AS adjustGMV
	, SUM(IFNULL(peoples, 0)) AS truePeoples
	, 0 AS predictPeoples, 0 AS adjustPeoples, 1 AS status, current_timestamp AS insertTime, current_timestamp AS updateTime
	, COUNT(DISTINCT order_no) AS trueOrders, 0 AS predictOrders, 0 AS adjustOrders
FROM base_pos_df
WHERE substr(gmt_bill, 1, 10) = '2019-09-01'
	AND aistatus = 1
GROUP BY cid, did, concat(substr(gmt_bill, 1, 14), LPAD(floor(bill_minute / 15), 2, 0));




desc ref_date_flag;
+------------+-------------+------+-----+---------+-------+
| Field      | Type        | Null | Key | Default | Extra |
+------------+-------------+------+-----+---------+-------+
| flagTday   | varchar(10) | YES  |     | NULL    |       |
| flagTstart | varchar(5)  | YES  |     | NULL    |       |
| flagTend   | varchar(5)  | YES  |     | NULL    |       |
+------------+-------------+------+-----+---------+-------+


SELECT count(1)
    from ref_date_flag
    where flagTday='2019-09-01'
+----------+
| count(1) |
+----------+
|       96 |
+----------+
MariaDB [woqu]> select cid,did ,1 as s
    ->     from base_pos_df 
    ->     WHERE did is not NULL
    ->     GROUP by cid,did;
+--------+------+---+
| cid    | did  | s |
+--------+------+---+
| 102672 | 14   | 1 |
| 102672 | 15   | 1 |
| 102672 | 16   | 1 |
| 102672 | 44   | 1 |
| 102672 | 47   | 1 |
| 102672 | 48   | 1 |
| 102672 | 49   | 1 |
| 102672 | 50   | 1 |
| 102672 | 51   | 1 |
| 102672 | 52   | 1 |
| 102672 | 53   | 1 |
| 102672 | 57   | 1 |
| 102672 | 58   | 1 |
| 102672 | 6    | 1 |
| 123456 | 106  | 1 |
| 123456 | 108  | 1 |
| 123456 | 109  | 1 |
| 123456 | 11   | 1 |
+--------+------+---+
18 rows in set (0.39 sec)




INSERT INTO view_pos_df
SELECT
  b.cid
  ,b.did
  ,a.shike
  ,IFNULL(c.trueGMV, 0)  as trueGMV
  , 0 AS predictGMV
  , 0 AS adjustGMV
  ,IFNULL(c.truePeoples, 0) AS truePeoples
  , 0 AS predictPeoples
  , 0 AS adjustPeoples
  , 1 AS status
  ,current_timestamp as insertTime
  ,current_timestamp as updateTime
  ,IFNULL(c.trueOrders, 0) AS trueOrders
  , 0 AS predictOrders
  , 0 AS adjustOrders
from(
    SELECT flagTday,flagTstart,1 as s,concat_ws(' ',flagTday,flagTstart) as shike
    from ref_date_flag
    where flagTday='2019-09-01'
) a left outer join 
(
    select cid,did,1 as s
    from base_pos_df 
    WHERE did is not NULL
    GROUP by cid,did
)b
on  a.s=b.s 
left outer join
(
    SELECT cid, did
        , concat(substr(gmt_bill, 1, 14), LPAD(floor(bill_minute / 15), 2, 0)) AS shike
        , SUM(IFNULL(data_value, 0)) AS trueGMV
        , SUM(IFNULL(peoples, 0)) AS truePeoples
        , COUNT(DISTINCT order_no) AS trueOrders
    FROM base_pos_df
    WHERE substr(gmt_bill, 1, 10) = '2019-09-01'
        AND aistatus = 1
    GROUP BY cid, did, concat(substr(gmt_bill, 1, 14), LPAD(floor(bill_minute / 15), 2, 0))
) c
on b.cid=c.cid and b.did=c.did and a.shike=c.shike;