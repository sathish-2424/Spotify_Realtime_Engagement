USE spotify_analytics_dw;

-- Track length vs skip rate. This summarizes simulated engagement events.
SELECT
    CASE WHEN t.duration_mins > 4.0 THEN 'Long (> 4 min)' ELSE 'Standard (<= 4 min)' END AS length_bucket,
    COUNT(*) AS total_plays,
    SUM(e.event_type = 'stream_skip') AS skip_count,
    ROUND(100.0 * SUM(e.event_type = 'stream_skip') / NULLIF(COUNT(*), 0), 2) AS skip_rate_pct
FROM engagement_events e
JOIN tracks t ON e.track_id = t.track_id
WHERE e.event_type IN ('stream_complete', 'stream_skip')
GROUP BY length_bucket;

-- Notification open rate by delivery mode.
SELECT
    notification_delivery_mode,
    COUNT(*) AS total_notifications,
    SUM(event_type = 'push_notif_open') AS opened_count,
    ROUND(100.0 * SUM(event_type = 'push_notif_open') / NULLIF(COUNT(*), 0), 2) AS open_rate_pct
FROM engagement_events
WHERE event_type IN ('push_notif_open', 'push_notif_dismiss')
GROUP BY notification_delivery_mode;
