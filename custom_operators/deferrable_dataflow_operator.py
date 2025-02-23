from typing import Any

from airflow.models.baseoperator import BaseOperator
from airflow.utils.context import Context
from airflow.triggers.base import StartTriggerArgs
# from dataflow_trigger import DataflowTrigger


class DeferrableDataflowOperator(BaseOperator):

    start_trigger_args = StartTriggerArgs(
        trigger_cls="dataflow_trigger.DataflowTrigger",
        trigger_kwargs={},
        next_method="execute_complete",
        next_kwargs=None,
        timeout=None,
    )

    def __init__(
        self,
        *args: list[Any],
        trigger_kwargs: dict[str, Any] | None,
        start_from_trigger: bool,
        end_from_trigger: bool,
        **kwargs: dict[str, Any],
    ) -> None:
        # This whole method will be skipped during dynamic task mapping.

        super().__init__(*args, **kwargs)
        self.start_trigger_args.trigger_kwargs = trigger_kwargs
        self.start_from_trigger = start_from_trigger
        self.end_from_trigger = end_from_trigger

    # def __init__(self, project_id, region, body, **kwargs):
    #     super().__init__(**kwargs)
    #     self.project_id = project_id
    #     self.region = region
    #     self.body = body

    # def execute(self, context: Context):
    #     """Defers execution to the triggerer."""
    #     self.body = self.render_template(self.body, context)
    #     self.defer(
    #         trigger=DataflowTrigger(
    #             project_id=self.project_id,
    #             region=self.region,
    #             body=self.body,
    #         ),
    #         method_name="execute_complete",
    #     )

    def execute_complete(self, context: Context, event: dict):
        """Callback method executed once trigger completes."""
        if event["status"] == "success":
            self.log.info(
                f"Dataflow job started successfully! Job ID: {event['jobId']}")
        else:
            raise RuntimeError(f"Dataflow job failed: {event['message']}")
