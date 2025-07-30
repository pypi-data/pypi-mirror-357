from datetime import datetime, timedelta
from typing import Dict, Any, Literal, Optional, Union, Callable
import backoff
import json

from google.api_core.exceptions import NotFound
from google.cloud.tasks_v2 import CloudTasksClient, CreateTaskRequest, Task, HttpRequest, OAuthToken, OidcToken
from google.oauth2 import service_account
from google.protobuf import duration_pb2, timestamp_pb2

from arcane.core.exceptions import GOOGLE_EXCEPTIONS_TO_RETRY



TaskStatusLiteral = Literal['running', 'done', 'failed']


class Client(CloudTasksClient):
    def __init__(self, adscale_key: str, project: str):
        self.project = project
        self.credentials = service_account.Credentials.from_service_account_file(
            adscale_key)
        self.adscale_key = adscale_key
        super().__init__(credentials=self.credentials)

    @backoff.on_exception(backoff.expo, GOOGLE_EXCEPTIONS_TO_RETRY, max_tries=5)
    def publish_task(self,
                     queue: str,
                     method: str = "POST",
                     queue_region: str = "europe-west1",
                     url: Optional[str] = None,
                     # if rounded to the closest second. If not precised, use cloud task default value
                     max_response_time: Optional[timedelta] = None,
                     task_name: Optional[str] = None,
                     body: Optional[Union[Dict[str, Any], str, int]] = None,
                     raw_body: Optional[bytes] = None,
                     schedule_time: Optional[datetime] = None,
                     auth_method: Literal['oidc', 'oauth'] = 'oidc',
                     extra_headers: Optional[Dict[str, str]] = None,
                     ) -> Task:
        _task_queue = self.queue_path(
            project=self.project, location=queue_region, queue=queue)
        with open(self.adscale_key) as _credentials_file:
            _credentials = json.load(_credentials_file)
        _client_email = _credentials['client_email']
        headers = {'Content-Type': "application/json"}
        
        if extra_headers:
            headers.update(extra_headers)
            
        http_request = HttpRequest(
            http_method=method,
            url=url,
            headers=headers
        )

        if auth_method == 'oidc':
            http_request.oidc_token = OidcToken(
                service_account_email=_client_email)
        elif auth_method == 'oauth':
            http_request.oauth_token = OAuthToken(
                service_account_email=_client_email)

        if body is not None:
            if raw_body is not None:
                raise ValueError(
                    "either body or raw_body should be specified, not both at ")

            http_request.body = json.dumps(body).encode('utf-8')
        elif raw_body is not None:
            http_request.body = raw_body

        task = Task(http_request=http_request)
        if max_response_time is not None:
            task.dispatch_deadline = duration_pb2.Duration(
                seconds=max_response_time.seconds)
        if task_name:
            task.name = self.task_path(
                self.project, queue_region, queue, task_name)
        if schedule_time:
            timestamp = timestamp_pb2.Timestamp()
            timestamp.FromDatetime(schedule_time)

            task.schedule_time = timestamp
        created_task = self.create_task(
            request=CreateTaskRequest(parent=_task_queue, task=task)
        )
        return created_task


    def check_all_task_status(self, subtask_names: list[str], dispatch_count_limit: int = 5 , log: Callable = print) -> TaskStatusLiteral:
        """Given a list of task name, check if all tasks are done
        If one is failed, return failed
        If one is running, return running
        If all are done, return done

        Args:
            subtask_names (list[str]): Taks name to check
            dispatch_count_limit (int, optional): Limit to consider a task have failed. Defaults to 5.
            log (Callable, optional): logger function. Defaults to print.

        Returns:
            TaskStatusLiteral: Global status
        """
        tasks_status = 'done'
        for task_name in subtask_names:
            log(f'Checking task with name: {task_name}')
            try:
                task = self.get_task(
                    name=task_name
                )  # type: ignore
                task_last_attempt = task.last_attempt

                if task.dispatch_count >= dispatch_count_limit:  # type: ignore We consider task failed when 'dispatch_count_limit' attempts have failed
                    tasks_status = 'failed'
                    log(f'Task with name : {task_name} has failed')
                    break
                elif task_last_attempt.response_time is None or task_last_attempt.response_status.code != 0:  # type: ignore
                    tasks_status = 'running'
                    log(f'Task with name : {task_name} is running')
            except NotFound:
                pass  # The error catched means the task was completed
        return tasks_status
