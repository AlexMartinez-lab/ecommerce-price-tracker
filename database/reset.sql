-- ================================================================
-- WARNING
-- This script removes all project tables and their data.
-- Use only in development enviorments.
-- ================================================================


BEGIN;


DROP TABLE IF EXISTS price_history CASCADE;
DROP TABLE IF EXISTS pipeline_runs CASCADE;
DROP TABLE IF EXISTS product_listings CASCADE;
DROP TABLE IF EXISTS stores CASCADE;
DROP TABLE IF EXISTS products CASCADE;

COMMIT;
