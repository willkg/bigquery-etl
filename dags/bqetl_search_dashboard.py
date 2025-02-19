# Generated via https://github.com/mozilla/bigquery-etl/blob/main/bigquery_etl/query_scheduling/generate_airflow_dags.py

from airflow import DAG
from operators.task_sensor import ExternalTaskCompletedSensor
import datetime
from utils.gcp import bigquery_etl_query, gke_command

docs = """
### bqetl_search_dashboard

Built from bigquery-etl repo, [`dags/bqetl_search_dashboard.py`](https://github.com/mozilla/bigquery-etl/blob/main/dags/bqetl_search_dashboard.py)

#### Owner

akomar@mozilla.com
"""


default_args = {
    "owner": "akomar@mozilla.com",
    "start_date": datetime.datetime(2020, 12, 14, 0, 0),
    "end_date": None,
    "email": ["telemetry-alerts@mozilla.com", "akomar@mozilla.com"],
    "depends_on_past": False,
    "retry_delay": datetime.timedelta(seconds=1800),
    "email_on_failure": True,
    "email_on_retry": True,
    "retries": 2,
}

tags = ["impact/tier_2"]

with DAG(
    "bqetl_search_dashboard",
    default_args=default_args,
    schedule_interval="0 4 * * *",
    doc_md=docs,
    tags=tags,
) as dag:

    search_derived__desktop_search_aggregates_by_userstate__v1 = bigquery_etl_query(
        task_id="search_derived__desktop_search_aggregates_by_userstate__v1",
        destination_table="desktop_search_aggregates_by_userstate_v1",
        dataset_id="search_derived",
        project_id="moz-fx-data-shared-prod",
        owner="xluo@mozilla.com",
        email=[
            "akomar@mozilla.com",
            "telemetry-alerts@mozilla.com",
            "xluo@mozilla.com",
        ],
        date_partition_parameter="submission_date",
        depends_on_past=False,
        dag=dag,
    )

    search_derived__desktop_search_aggregates_for_searchreport__v1 = bigquery_etl_query(
        task_id="search_derived__desktop_search_aggregates_for_searchreport__v1",
        destination_table="desktop_search_aggregates_for_searchreport_v1",
        dataset_id="search_derived",
        project_id="moz-fx-data-shared-prod",
        owner="xluo@mozilla.com",
        email=[
            "akomar@mozilla.com",
            "telemetry-alerts@mozilla.com",
            "xluo@mozilla.com",
        ],
        date_partition_parameter="submission_date",
        depends_on_past=False,
        dag=dag,
    )

    search_derived__mobile_search_aggregates_for_searchreport__v1 = bigquery_etl_query(
        task_id="search_derived__mobile_search_aggregates_for_searchreport__v1",
        destination_table="mobile_search_aggregates_for_searchreport_v1",
        dataset_id="search_derived",
        project_id="moz-fx-data-shared-prod",
        owner="mmccorquodale@mozilla.com",
        email=[
            "akomar@mozilla.com",
            "mmccorquodale@mozilla.com",
            "telemetry-alerts@mozilla.com",
            "xluo@mozilla.com",
        ],
        date_partition_parameter="submission_date",
        depends_on_past=False,
        dag=dag,
    )

    wait_for_telemetry_derived__clients_last_seen__v1 = ExternalTaskCompletedSensor(
        task_id="wait_for_telemetry_derived__clients_last_seen__v1",
        external_dag_id="bqetl_main_summary",
        external_task_id="telemetry_derived__clients_last_seen__v1",
        execution_delta=datetime.timedelta(seconds=7200),
        check_existence=True,
        mode="reschedule",
        pool="DATA_ENG_EXTERNALTASKSENSOR",
    )

    search_derived__desktop_search_aggregates_by_userstate__v1.set_upstream(
        wait_for_telemetry_derived__clients_last_seen__v1
    )

    wait_for_search_derived__search_aggregates__v8 = ExternalTaskCompletedSensor(
        task_id="wait_for_search_derived__search_aggregates__v8",
        external_dag_id="bqetl_search",
        external_task_id="search_derived__search_aggregates__v8",
        execution_delta=datetime.timedelta(seconds=3600),
        check_existence=True,
        mode="reschedule",
        pool="DATA_ENG_EXTERNALTASKSENSOR",
    )

    search_derived__desktop_search_aggregates_for_searchreport__v1.set_upstream(
        wait_for_search_derived__search_aggregates__v8
    )

    wait_for_search_derived__mobile_search_clients_daily__v1 = (
        ExternalTaskCompletedSensor(
            task_id="wait_for_search_derived__mobile_search_clients_daily__v1",
            external_dag_id="bqetl_mobile_search",
            external_task_id="search_derived__mobile_search_clients_daily__v1",
            execution_delta=datetime.timedelta(seconds=7200),
            check_existence=True,
            mode="reschedule",
            pool="DATA_ENG_EXTERNALTASKSENSOR",
        )
    )

    search_derived__mobile_search_aggregates_for_searchreport__v1.set_upstream(
        wait_for_search_derived__mobile_search_clients_daily__v1
    )
