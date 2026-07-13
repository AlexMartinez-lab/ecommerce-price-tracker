-- ============================================================

-- E-commerce Price Tracker

-- Initial PostgreSQL Schema

-- ============================================================

BEGIN;

-- ============================================================
-- 1. PRODUCTS
-- Canonical products independent from stores and URLs.
-- ===========================================================


CREATE TABLE IF NOT EXISTS products (
	id BIGSERIAL PRIMARY KEY,

	name VARCHAR(255) NOT NULL,
	brand VARCHAR(100),
	model VARCHAR(150),
	sku VARCHAR(100),
	description TEXT,

	active BOOLEAN NOT NULL DEFAULT TRUE,

	created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

	CONSTRAINT products_name_not_blank
		CHECK (BTRIM(name) <> '')
);


COMMENT ON TABLE products IS
'canonical products tracked independently from any store or listing.';

COMMENT ON COLUMN products.name IS
'Normalized product name used internally by the application.';

COMMENT ON COLUMN products.active IS
'Indicates whether the product should continue being tracked.';



-- ===================================================================
-- 2. STORES
-- Supported e-commerce websites and marketplaces.
-- ===================================================================


CREATE TABLE IF NOT EXISTS stores (
	id BIGSERIAL PRIMARY KEY,

	name VARCHAR(120) NOT NULL,
	domain VARCHAR(255) NOT NULL,
	country_code CHAR(2) NOT NULL DEFAULT 'MX',

	active BOOLEAN NOT NULL DEFAULT TRUE,

	created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

	CONSTRAINT stores_name_not_blank
		CHECK (BTRIM(name) <> ''),

	CONSTRAINT stores_domain_not_blank
		CHECK (BTRIM (domain) <> ''),

	CONSTRAINT stores_domain_unique
		UNIQUE (domain),

	CONSTRAINT stores_country_code_format
		CHECK (country_code ~ '^[A-Z]{2}$')
);


COMMENT ON TABLE stores IS
'E-commerce websites or marketplaces supported by the system.';

COMMENT ON COLUMN stores.domain IS
'Main domain without protocol, for example mercadolibre.com.mx.';


-- ==============================================================
-- 3. PRODUCT LISTINGS
-- Store-specific publications associated with canonical products.
-- ==============================================================


CREATE TABLE IF NOT EXISTS product_listings (
	id BIGSERIAL PRIMARY KEY,

	product_id BIGINT NOT NULL,
	store_id BIGINT NOT NULL,

	external_listing_id VARCHAR(200),
	title TEXT NOT NULL,
	url TEXT NOT NULL,
	image_url TEXT,

	condition VARCHAR(30) NOT NULL DEFAULT 'unknown',
	active BOOLEAN NOT NULL DEFAULT TRUE,

	first_seen_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
	last_seen_at TIMESTAMPTZ,

	created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

	CONSTRAINT product_listings_product_fk
		FOREIGN KEY (product_id)
		REFERENCES products(id)
		ON UPDATE CASCADE
		ON DELETE RESTRICT,

	CONSTRAINT product_listings_store_fk
		FOREIGN KEY (store_id)
		REFERENCES stores(id)
		ON UPDATE CASCADE
		ON DELETE RESTRICT,

	CONSTRAINT product_listings_title_not_blank
		CHECK (BTRIM(title) <> ''),

	CONSTRAINT product_listings_url_not_blank
		CHECK (BTRIM(url) <> ''),

	CONSTRAINT product_listings_condition_valid
		CHECK (
			condition IN (
				'new',
				'used',
				'refurbished',
				'open_box',
				'unknown'
		        )
		 ),

	CONSTRAINT product_listings_store_external_id_unique
		UNIQUE (store_id, external_listing_id)
);

COMMENT ON TABLE product_listings IS
'Store-specific publications associated with canonical products.';

COMMENT ON COLUMN product_listings.external_listing_id IS
'Identifier assigned to the listing by the source  website.';

COMMENT ON COLUMN product_listings.title IS
'Original product title shown by the source website.';



-- ==========================================================
-- 4. PIPELINE RUNS
-- Operational metadata for every ETL execution.
-- ==========================================================

CREATE TABLE IF NOT EXISTS pipeline_runs (
	id BIGSERIAL PRIMARY KEY,

	started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
	finished_at TIMESTAMPTZ,

	status VARCHAR(20) NOT NULL DEFAULT 'running',

	listings_processed INTEGER NOT NULL DEFAULT 0,
	successful_records INTEGER NOT NULL DEFAULT 0,
	failed_records INTEGER NOT NULL DEFAULT 0,

	error_message TEXT,
	execution_source VARCHAR(30) NOT NULL DEFAULT 'manual',

	created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

	CONSTRAINT pipeline_runs_status_valid
		CHECK (
			status IN (
				'running',
				'success',
				'partial',
				'failed'
			)
		 ),

	CONSTRAINT pipeline_runs_execution_source_valid
		CHECK (
			execution_source IN (
				'manual',
				'cron',
				'api',
				'scheduler',
				'test'
			)
		 ),

	CONSTRAINT pipeline_runs_listings_processed_non_negative
		CHECK (listings_processed >= 0),

	CONSTRAINT pipeline_runs_successful_records_non_negative
		CHECK (successful_records >= 0),

	CONSTRAINT pipeline_runs_failed_records_non_negative
		CHECK (failed_records >= 0),

	CONSTRAINT pipeline_runs_finished_after_started
		CHECK (
			finished_at IS NULL
			OR finished_at >= started_at
		)
);

COMMENT ON TABLE pipeline_runs IS
'Execution summaries for ETL pipeline monitoring and debugging.';



-- ============================================================
-- 5. PRICE HISTORY
-- Immutable historical observations collected from listings.
-- ============================================================


CREATE TABLE IF NOT EXISTS price_history (
	id BIGSERIAL PRIMARY KEY,

	listing_id BIGINT NOT NULL,
	pipeline_run_id BIGINT,

	current_price NUMERIC(12, 2) NOT NULL,
	original_price NUMERIC(12, 2),
	shipping_cost NUMERIC(12, 2),

	currency CHAR(3) NOT NULL DEFAULT 'MXN',

	available BOOLEAN NOT NULL DEFAULT TRUE,
	stock_status VARCHAR(50),
	raw_price_text VARCHAR(100),

	observed_at TIMESTAMPTZ NOT NULL,
	created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

	CONSTRAINT price_history_listing_fk
		FOREIGN KEY (listing_id)
		REFERENCES product_listings(id)
		ON UPDATE CASCADE
		ON DELETE RESTRICT,

	CONSTRAINT price_history_pipeline_run_fk
		FOREIGN KEY (pipeline_run_id)
		REFERENCES pipeline_runs(id)
		ON UPDATE CASCADE
		ON DELETE SET NULL,

	CONSTRAINT price_history_current_price_non_negative
		CHECK (current_price >= 0),

	CONSTRAINT price_history_original_price_non_negative
		CHECK (
			original_price IS NULL
			OR original_price >= 0
		),

	CONSTRAINT price_history_shipping_cost_non_negative
		CHECK (
			shipping_cost IS NULL
			OR shipping_cost >= 0
		),

	CONSTRAINT price_history_currency_format
		CHECK (currency ~ '^[A-Z]{3}$')
);


COMMENT ON TABLE price_history IS
'Append-only historical price and availability observations.';

COMMENT ON COLUMN price_history.observed_at IS
'Timestamp when the information was collected from the source.';

COMMENT ON COLUMN price_history.created_at IS
'Timestamp when the observation was inserted into PostgreSQL.';



-- ===============================================================
-- INDEXES
-- ===============================================================


CREATE INDEX IF NOT EXISTS idx_products_name
	ON products(name);

CREATE INDEX IF NOT EXISTS idx_product_listings_product_id
	ON product_listings(product_id);

CREATE INDEX IF NOT EXISTS idx_product_listings_store_id
	ON product_listings(store_id);

CREATE INDEX IF NOT EXISTS idx_product_listings_active
	ON product_listings(active);

CREATE INDEX IF NOT EXISTS idx_price_history_listing_id
	ON price_history(listing_id);

CREATE INDEX IF NOT EXISTS idx_price_history_observed_at
	ON price_history(observed_at);

CREATE INDEX IF NOT EXISTS idx_price_history_listing_observed_at
	ON price_history(listing_id, observed_at DESC);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_started_at
	ON pipeline_runs(started_at DESC);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_status
	ON pipeline_runs(status);



COMMIT;






















































































































































































































