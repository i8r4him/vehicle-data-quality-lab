SELECT offer_id, batch_id,
       (json_extract(new_json, '$.price_cents') - json_extract(old_json, '$.price_cents')) / 100.0 AS price_delta_eur
FROM changes WHERE operation = 'update'
ORDER BY batch_id, offer_id;
