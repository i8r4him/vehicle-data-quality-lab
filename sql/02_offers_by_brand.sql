SELECT b.name AS brand, COUNT(*) AS offers,
       ROUND(AVG(o.price_cents) / 100.0, 2) AS average_monthly_price_eur
FROM offers o JOIN vehicles v ON v.id = o.vehicle_id JOIN brands b ON b.id = v.brand_id
GROUP BY b.id, b.name ORDER BY b.name;
