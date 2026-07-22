SELECT 
    ph.id,
    pl.external_listing_id,
    pl.title,
    ph.current_price,
    ph.original_price,
    ph.shipping_cost,
    ph.currency,
    ph.available,
    ph.observed_at
FROM price_history AS ph
INNER JOIN  product_listing AS pl
    ON ph.listing_id = pl.id
WHERE pl.external_listing_id = 'DEMO-RTX5070TI-001'
ORDER BY ph.observed_at DESC;