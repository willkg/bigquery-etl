-- Generated by ./bqetl generate events_daily
CREATE OR REPLACE VIEW
  `moz-fx-data-shared-prod.fenix.events_daily`
AS
SELECT
  *
FROM
  `moz-fx-data-shared-prod.fenix_derived.events_daily_v1`
