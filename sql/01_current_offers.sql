SELECT o.offer_id, b.name AS brand, v.model, o.product,
       o.price_cents / 100.0 AS monthly_price_eur, o.term_months, o.annual_mileage, o.updated_at
FROM offers o JOIN vehicles v ON o.vehicle_id = v.id JOIN brands b ON v.brand_id = b.id
ORDER BY b.name, v.model, o.offer_id;
