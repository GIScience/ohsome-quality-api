DELETE FROM guf04_4 WHERE NOT rid IN (SELECT rid FROM guf04_4 GROUP BY rid HAVING ST_ValueCount(rast, 1, true, 255) > 0);
