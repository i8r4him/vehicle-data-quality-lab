-- These phases are deliberately constructed synthetic examples, not a causal experiment.
SELECT phase, category, COUNT(*) AS requests,
       ROUND(AVG((julianday(resolved_at) - julianday(created_at)) * 24), 2) AS average_hours
FROM service_requests GROUP BY phase, category
ORDER BY category, CASE phase WHEN 'manuell' THEN 0 ELSE 1 END;
