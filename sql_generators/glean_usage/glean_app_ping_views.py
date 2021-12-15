"""
Generate app (as opposed to channel) specific views for Glean ping tables.

At the moment we only do this for the release channel.
"""
import os

from mozilla_schema_generator.glean_ping import GleanPing

from sql_generators.glean_usage.common import GleanTable
from bigquery_etl.util.common import get_table_dir, write_sql

VIEW_QUERY_TEMPLATE = """\
-- Generated by Generated via bigquery_etl.glean_usage.GleanAppPingViews
CREATE OR REPLACE VIEW
  `{full_view_id}`
AS
SELECT
  *
FROM
  `{target}`
"""

VIEW_METADATA_TEMPLATE = """\
# Generated by bigquery_etl.glean_usage.GleanAppPingViews
---
friendly_name: App-specific view for Glean ping "{ping_name}"
description: |-
  This is a pointer to the main view to the stable ping table
  for the release channel of the Glean application "{app_name}"
  ({underlying_view_id}).

  It is used by Looker.
"""


class GleanAppPingViews(GleanTable):
    """Represents generated events_unnested table."""

    def __init__(self):
        """Initialize events_unnested table."""
        GleanTable.__init__(self)
        self.no_init = True
        self.per_app_id_enabled = False
        self.per_app_enabled = True

    def generate_per_app(self, project_id, app_info, output_dir=None):
        """
        Generate per-app ping views.

        For the release channel of a glean app *only*, generate a
        pointer view to the app-id specific view for that channel/app
        combination
        """
        release_app = app_info[0]
        target_dataset = release_app["app_name"]
        repo = next(
            (r for r in GleanPing.get_repos() if r["name"] == release_app["v1_name"])
        )

        # app name is the same as the bq_dataset_family for the release channel: do nothing
        if (
            repo["app_id"] == release_app["app_name"]
            or release_app["bq_dataset_family"] == release_app["app_name"]
        ):
            return

        p = GleanPing(repo)
        for ping_name in p.get_pings():
            view_name = ping_name.replace("-", "_")
            underlying_view_id = ".".join(
                ["moz-fx-data-shared-prod", repo["app_id"].replace("-", "_"), view_name]
            )
            full_view_id = f"moz-fx-data-shared-prod.{target_dataset}.{view_name}"
            if output_dir:
                write_sql(
                    output_dir,
                    full_view_id,
                    "view.sql",
                    VIEW_QUERY_TEMPLATE.format(
                        full_view_id=full_view_id,
                        target=underlying_view_id,
                    ),
                )
                write_sql(
                    output_dir,
                    full_view_id,
                    "metadata.yaml",
                    VIEW_METADATA_TEMPLATE.format(
                        ping_name=ping_name,
                        app_name=release_app["canonical_app_name"],
                        underlying_view_id=underlying_view_id,
                    ),
                )

                # we create a schema to the original view created for the
                # stable tables here (this assumes that they have been or
                # will be generated, which should be the case for a full
                # run of the sql generation logic)
                schema_dir = get_table_dir(output_dir, full_view_id)
                original_schema_file = os.path.relpath(
                    os.path.abspath(
                        get_table_dir(output_dir, underlying_view_id) / "schema.yaml"
                    ),
                    start=schema_dir,
                )
                schema_link = schema_dir / "schema.yaml"
                try:
                    os.unlink(schema_link)
                except FileNotFoundError:
                    pass
                os.symlink(original_schema_file, schema_link)
