from airflow.triggers.base import BaseTrigger, TriggerEvent, TaskSuccessEvent, TaskFailedEvent
from google.cloud import dataflow_v1beta3
import asyncio


class DataflowTrigger(BaseTrigger):
    def __init__(self, project_id, region, body):
        super().__init__()
        self.project_id = project_id
        self.region = region
        self.body = body

    def serialize(self):
        """Serialize the trigger for Airflow's triggerer."""
        return ("dataflow_trigger.DataflowTrigger", {
            "project_id": self.project_id,
            "region": self.region,
            "body": self.body
        })

    async def run(self):
        """Trigger logic to start the Dataflow job."""
        try:
            client = dataflow_v1beta3.FlexTemplatesServiceAsyncClient()
            request = dataflow_v1beta3.LaunchFlexTemplateRequest(
                project_id=self.project_id,
                location=self.region,
                launch_parameter=self.body
            )
            response = await client.launch_flex_template(request=request)
            job_id = response.job.id
            job_client = dataflow_v1beta3.JobsV1Beta3AsyncClient()

            while True:
                job = await job_client.get_job(
                    request=dataflow_v1beta3.GetJobRequest(
                        project_id=self.project_id,
                        location=self.region,
                        job_id=job_id
                    )
                )
                if job.current_state == dataflow_v1beta3.JobState.JOB_STATE_DONE:
                    # TriggerEvent({"status": "success", "jobId": job_id})
                    yield TaskSuccessEvent()
                    break
                elif job.current_state in (
                    dataflow_v1beta3.JobState.JOB_STATE_FAILED,
                    dataflow_v1beta3.JobState.JOB_STATE_CANCELLED,
                    dataflow_v1beta3.JobState.JOB_STATE_UPDATED,
                ):
                    # TriggerEvent({"status": "error", "message": f"Job {job_id} failed with state {job.current_state}"})
                    yield TaskFailedEvent()
                    break
                await asyncio.sleep(60)
            # yield TriggerEvent({"status": "success", "jobId": response.job.id})
        except Exception as e:
            # TriggerEvent({"status": "error", "message": str(e)})
            yield TaskFailedEvent()
