CREATE ROLE erp_user WITH LOGIN PASSWORD 'ErpUser123.';
ALTER ROLE erp_user CREATEDB;  -- Optional: allow creating databases
GRANT ALL PRIVILEGES ON DATABASE db_video_analytics TO erp_user;