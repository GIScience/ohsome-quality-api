SET SCHEMA 'development';

CREATE INDEX idx_isea3h_world_res_12_hex_geohash ON isea3h_world_res_12_hex USING btree (geohash_id);
CREATE INDEX idx_isea3h_world_res_12_hex_geom ON isea3h_world_res_12_hex USING gist (geom);
CREATE INDEX idx_isea3h_world_res_12_hex_geom4326 ON isea3h_world_res_12_hex USING gist (geom4326);
CREATE INDEX idx_isea3h_world_res_12_hex_id ON isea3h_world_res_12_hex USING btree (global_id);
CREATE INDEX idx_isea3h_world_res_12_hex_pt_geom ON isea3h_world_res_12_hex USING gist (pt_geom);

CREATE INDEX idx_isea3h_world_res_6_hex_geohash ON isea3h_world_res_6_hex USING btree (geohash_id);
CREATE INDEX idx_isea3h_world_res_6_hex_geom ON isea3h_world_res_6_hex USING gist (geom);
CREATE INDEX idx_isea3h_world_res_6_hex_geom4326 ON isea3h_world_res_6_hex USING gist (geom4326);
CREATE INDEX idx_isea3h_world_res_6_hex_id ON isea3h_world_res_6_hex USING btree (global_id);
CREATE INDEX idx_isea3h_world_res_6_hex_pt_geom ON isea3h_world_res_6_hex USING gist (pt_geom);

CREATE INDEX nuts_rg_01m_2021_id ON nuts_rg_01m_2021 USING btree (id);
CREATE INDEX nuts_rg_01m_2021_fid ON nuts_rg_01m_2021 USING btree (fid);
CREATE INDEX nuts_rg_01m_2021_geom ON nuts_rg_01m_2021 USING gist (geom);

CREATE INDEX nuts_rg_60m_2021_id ON nuts_rg_60m_2021 USING btree (id);
CREATE INDEX nuts_rg_60m_2021_fid ON nuts_rg_60m_2021 USING btree (fid);
CREATE INDEX nuts_rg_60m_2021_geom ON nuts_rg_60m_2021 USING gist (geom);

CREATE INDEX ghs_pop_st_convexhull_idx  ON ghs_pop USING gist (public.st_convexhull(rast));