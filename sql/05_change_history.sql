SELECT c.batch_id, c.offer_id, c.operation,
       json_extract(c.old_json, '$.price_cents') / 100.0 AS old_price_eur,
       json_extract(c.new_json, '$.price_cents') / 100.0 AS new_price_eur,
       c.changed_at
FROM changes c ORDER BY c.id;
