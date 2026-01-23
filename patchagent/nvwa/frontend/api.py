from typing import Union
from nvwa.sky.task import PatchTask
from nvwa.policy.default import DefaultPolicy

from nvwa.logger import log


def patch(
    task: PatchTask,
    reset: bool = True,
    model: str = "gpt-4",
    log_path: Union[None, str] = None,
    max_iteration: int = -1,
) -> Union[None, str]:
    log.info(f"Start Patching {task} (reset={reset})")

    policy = DefaultPolicy(task, reset=reset, model=model, log_path=log_path)
    policy.apply(max_iteration=max_iteration)

    return task.patch
