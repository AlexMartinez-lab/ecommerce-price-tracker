BEGIN;

SELECT
	p.name AS product,
	s.name AS store,
	pl.title AS listing,
	ph.current_price,
	ph.currency,
	ph.available,
	ph.observed_at
FROM price_history AS ph
JOIN product_listings AS pl
	ON ph.listing_id = pl.id
JOIN products AS p
	ON pl.product_id = p.id
JOIN stores AS s
	ON pl.store_id = s.id
ORDER BY ph.observed_at DESC;

COMMIT;
