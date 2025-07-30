import tempfile
import logging
from pathlib import Path
from dataclasses import dataclass, field
from functools import cached_property
from collections.abc import Mapping, Sequence

from .tasks import Task
from .config import (
    ConfigDict,
    load_config,
    load_default_config,
    load_options_config,
)
from .utils import resolve_path


@dataclass(init=False)
class ProjectSource(object):
    """Represents a source project on the filesystem."""

    root: Path

    name: str

    config: ConfigDict = field(init=False, default_factory=load_default_config)

    sources: list[Path] = field(default_factory=list)
    additional_files: dict[str, any] = field(default_factory=dict)
    tasks: dict[str, list[Task]] = field(default_factory=dict)

    def __init__(
        self,
        root: str | Path,
        name: str = None,
        config: ConfigDict | Mapping = None,
    ) -> None:
        self.root = resolve_path(root)

        if not name:
            self.name = root.name

        self.config = load_default_config()
        if config:
            self.config.merge(config)

    def load_config(self, project_root: Path = None, options: dict = dict()) -> None:
        ## read config from user home
        self.config = load_config(Path.home() / ".config", base=self.config)

        ## resolve root directory from options or project config
        project_config = load_config(self.root, resolve=True)
        if project_root:
            self.config.project_root = resolve_path(project_root)
        else:
            if "project_root" in project_config and project_config.project_root:
                self.config.project_root = resolve_path(project_config.project_root)
            else:
                self.config.project_root = self.root.parent

        ## load project root config
        config = load_config(self.project_root, base=self.config, resolve=True)
        ## load project specific config
        config.merge(project_config)
        ## add cli options to config
        config.merge(load_options_config(options))

    @property
    def project_root(self) -> Path:
        return self.config.project_root


class ProjectVersion(object):
    """Represents a generated Project version."""

    source: ProjectSource

    config: ConfigDict

    files: dict[str, any] = field(default_factory=dict)
    tasks: dict[str, list[Task]] = field(default_factory=dict)


class ProjectSolution(ProjectVersion):
    """Represents the special solution version of a base project."""

    ...
