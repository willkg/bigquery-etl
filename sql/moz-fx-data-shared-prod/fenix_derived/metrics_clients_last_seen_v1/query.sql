WITH _previous AS (
  SELECT
    * EXCEPT (submission_date)
  FROM
    `moz-fx-data-shared-prod.fenix_derived.metrics_clients_last_seen_v1`
  WHERE
    submission_date = DATE_SUB(@submission_date, INTERVAL 1 DAY)
    AND udf.shift_28_bits_one_day(days_sent_metrics_ping_bits) > 0
),
_current AS (
  SELECT
    *
  FROM
    `moz-fx-data-shared-prod.fenix.metrics_clients_daily` AS m
  WHERE
    submission_date = @submission_date
)
SELECT
  DATE(@submission_date) AS submission_date,
  client_id,
  sample_id,
  _current.normalized_channel,
  _current.n_metrics_ping,
  udf.combine_adjacent_days_28_bits(
    _previous.days_sent_metrics_ping_bits,
    _current.days_sent_metrics_ping_bits
  ) AS days_sent_metrics_ping_bits,
  COALESCE(_current.uri_count, _previous.uri_count) AS uri_count,
  COALESCE(_current.is_default_browser, _previous.is_default_browser) AS is_default_browser,
FROM
  _previous
FULL JOIN
  _current
USING
  (client_id, sample_id)