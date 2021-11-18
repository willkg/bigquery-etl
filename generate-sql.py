#!/usr/bin/env python

import os
import shutil
import yaml
from pathlib import Path

import jinja2

VIEW_TEMPLATE = """CREATE OR REPLACE VIEW
  `{{ view_name }}`
AS
SELECT
  *
FROM
  `{{ source_name }}`

"""


for project in os.listdir("./definitions"):
    for namespace in os.listdir(f"./definitions/{project}"):
        base_output_dir = Path(f"./sql/{project}/{namespace}")
        for dataset in os.listdir(f"./definitions/{project}/{namespace}"):
            dataset_path = Path(f"./definitions/{project}/{namespace}/{dataset}")
            print((project, namespace, dataset))
            dataset_metadata = yaml.safe_load(
                open(dataset_path / "metadata.yaml").read()
            )

            table_path = dataset_path / "tables"
            latest_table_name = None
            # FIXME: this sorting won't work for versions greater than 10
            for table_version in sorted(os.listdir(table_path)):
                table_id = dataset + "_" + table_version
                output_dir = base_output_dir / f"{namespace}_derived" / table_id
                # copy the query
                os.makedirs(output_dir, exist_ok=True)
                shutil.copyfile(
                    table_path / table_version / "query.sql", output_dir / "query.sql"
                )
                # merge table-specific metadata with dataset metadata
                table_metadata = yaml.safe_load(
                    open(table_path / table_version / "metadata.yaml").read()
                )
                merged_metadata = {**dataset_metadata, **table_metadata}
                del merged_metadata["entrypoint"]
                open(output_dir / "metadata.yaml", "w").write(
                    yaml.dump(merged_metadata)
                )
                latest_table_name = f"{project}.{namespace}_derived.{table_id}"

            # we support defining custom versioned views for datasets
            latest_view_name = None
            if os.path.isdir(dataset_path / "views"):
                view_versions = os.listdir(dataset_path / "views")
                # FIXME: this sorting won't work for versions greater than 10
                for view_version in sorted(view_versions):
                    # views are templatized and take two parameters:
                    #   - source_name (name of the table to be queried)
                    #   - view_name (name of the view)
                    # both of these are generated automatically, based on the version of the view
                    view_id = f"{dataset}_{view_version}"
                    table_name = (
                        f"{project}.{namespace}_derived.{dataset}_{view_version}"
                    )
                    view_name = f"{project}.{namespace}.{view_id}"
                    output_dir = base_output_dir / view_id
                    print(output_dir)
                    os.makedirs(output_dir, exist_ok=True)
                    template = jinja2.Template(
                        open(dataset_path / "views" / view_version / "view.sql").read()
                    )
                    open(output_dir / "view.sql", "w").write(
                        template.render(table_name=table_name, view_name=view_name)
                    )
                    latest_view_name = view_name
            # finally, create a view pointing at either the latest view (if it exists),
            # or the latest table
            source_name = latest_view_name if view_name else latest_table_name
            view_output_dir = base_output_dir / dataset
            print(view_output_dir)
            os.makedirs(view_output_dir, exist_ok=True)
            open(view_output_dir / "view.sql", "w").write(
                jinja2.Template(VIEW_TEMPLATE).render(
                    source_name=source_name,
                    view_name=f"{project}.{namespace}.{dataset}",
                )
            )
            # v
            # print(dataset_metadata)
