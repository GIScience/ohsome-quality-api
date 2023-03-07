CREATE INDEX admin_world_water_geom_idx ON admin_world_water USING gist(geom);
CREATE INDEX hexcells_geom_idx ON hexcells USING gist(geom);
CREATE INDEX regions_geom_idx ON regions USING gist(geom);
CREATE INDEX shdi_geom_idx ON shdi USING gist(geom);

CREATE INDEX admin_world_water_pkey ON admin_world_water USING btree(id);
CREATE INDEX hexcells_pkey ON hexcells USING btree(ogc_fid);
CREATE INDEX regions_pkey ON regions USING btree(ogc_fid);
CREATE INDEX shdi_pkey ON shdi USING gist(gid);
