-- ==========================================================
-- E-commerce Price Tracker
-- Initial development seed data
-- ==========================================================


BEGIN;


INSERT INTO products (
	name,
	brand,
	model,
	description
)

VALUES (
	'Samsung Galaxy S23+ 256 GB',
	'Samsung',
	'SM-S916',
	'Canonical product used for initial development and testing.'
)
ON CONFLICT DO NOTHING;



INSERT INTO stores (
	name,
	domain,
	country_code
)

VALUES (
	'Mercado Libre Mexico',
	'mercadolibre.com.mx',
	'MX'
)
ON CONFLICT (domain) DO NOTHING;



INSERT INTO product_listings (
	product_id,
	store_id,
	external_listing_id,
	title,
	url,
	condition
)
SELECT
	products.id,
	stores.id,
	'DEMO-LISTING-001',
	'Samsung Galaxy S23 Plus 256GB',
	'https://example.com/demo-product',
	'new'
FROM products
CROSS JOIN stores
WHERE products.model = 'SM-S916'
   AND stores.domain = 'mercadolibre.com.mx'
ON CONFLICT (store_id, external_listing_id) DO NOTHING;



INSERT INTO pipeline_runs (
	started_at,
	finished_at,
	status,
	listings_processed,
	successful_records,
	failed_records,
	execution_source
)
VALUES (
	CURRENT_TIMESTAMP,
	CURRENT_TIMESTAMP,
	'success',
	1,
	1,
	0,
	'test'
);



INSERT INTO price_history (
	listing_id,
	pipeline_run_id,
	current_price,
	original_price,
	shipping_cost,
	currency,
	available,
	stock_status,
	raw_price_text,
	observed_at
)
SELECT
	product_listings.id,
	pipeline_runs.id,
	12599.00,
	13999.00,
	0.00,
	'MXN',
	TRUE,
	'available',
	'$12,599',
	CURRENT_TIMESTAMP
FROM product_listings
CROSS JOIN pipeline_runs
WHERE product_listings.external_listing_id = 'DEMO-LISTING-001'
ORDER BY pipeline_runs.id DESC
LIMIT 1;

COMMIT;
