import os
import yaml
from typing import Generator

from nvwa.sky.task import ROOT, PatchTask, skyset_tools


def make_task(project: str, tag: str, **kwargs) -> PatchTask:
    return PatchTask(project, tag, skyset_tools.get_config(project, tag)["sanitizer"], **kwargs)


def get_all_task(project=None, tag=None, skip_linux=False, skip_extractfix=False, **kwargs) -> Generator[PatchTask, None, None]:
    for project_ in os.listdir(ROOT):
        if (
            os.path.isdir(project_path := os.path.join(ROOT, project_))
            and project_ not in ["skyset_tools", ".git", "skyset_kernel_image"]
            and not project_.startswith("external-")
            and (project is None or project == project_)
            and (not skip_extractfix or not project_.startswith("extractfix"))
            and (not skip_linux or not project_.startswith("linux"))
        ):
            for tag_ in os.listdir(project_path):
                if os.path.isdir(os.path.join(project_path, tag_)) and (tag is None or tag == tag_):
                    yield make_task(project_, tag_, **kwargs)
