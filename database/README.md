# Database

This document describes how the database is setup.


## 1. Create a dump of ohsome-hex

```bash
pg_dump \
    -h k2.geog.uni-heidelberg.de
    -p 5434
    -U username
    -t isea3h_world_res_10_hex \
    -t isea3h_world_res_11_hex \
    -t isea3h_world_res_12_hex \
    -t isea3h_world_res_3_hex \
    -t isea3h_world_res_4_hex \
    -t isea3h_world_res_5_hex \
    -t isea3h_world_res_6_hex \
    -t isea3h_world_res_7_hex \
    -t isea3h_world_res_8_hex \
    -t isea3h_world_res_9_hex \
ohsome-hex > ohsome-hex-isea.sql
```
