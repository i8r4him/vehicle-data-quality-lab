-- Synthetic service requests: descriptive demonstration, not measured business impact.
SELECT category, COUNT(*) AS requests,
       ROUND(AVG((julianday(resolved_at) - julianday(created_at)) * 24), 2) AS average_hours,
       ROUND(MAX((julianday(resolved_at) - julianday(created_at)) * 24), 2) AS maximum_hours
FROM service_requests GROUP BY category ORDER BY average_hours DESC;
