/* Following extension are required by ohsome hex admin schema */
CREATE EXTENSION IF NOT EXISTS citext;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

SET search_path TO public, development, postgis;
