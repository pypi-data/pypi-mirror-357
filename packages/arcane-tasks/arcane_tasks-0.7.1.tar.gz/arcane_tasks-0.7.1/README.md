# Arcane CloudTask

This package is base on [google-cloud-cloudtasks](https://pypi.org/project/google-cloud-tasks/).

## Get Started

```sh
pip install arcane-tasks

## Example Usage

```python
from arcane import tasks

# Import your configs
from configure import Config

tasks_client = tasks.Client(adscale_key=Config.KEY, project=Config.GCP_PROJECT)
body = {
    'attribute' : value
}
task_name = "My task"
tasks_client.publish_task(
    queue=<your-queue>,
    url=<url-to-triger>,
    body=body,
    task_name=task_name
)
```
