SELECT code AS rule, COUNT(*) AS issue_count, COUNT(DISTINCT batch_id) AS affected_batches
FROM issues GROUP BY code ORDER BY issue_count DESC, code;
