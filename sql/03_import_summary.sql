SELECT id AS batch_id, file_name, status, rows_total, rows_valid, inserted, updated, unchanged,
       started_at, completed_at
FROM batches ORDER BY id;
