#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from __future__ import annotations

from ...thirdparty.code import *
from ...thirdparty.types import *
from .basic import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "LogProgress",
]

# ----------------------------------------------------------------
# CLASSES
# ----------------------------------------------------------------


@dataclass
class LogProgress:
    name: Optional[str] = field()
    title: Optional[str] = field(default=None)
    steps: int = field(default=1)
    step: int = field(default=0, init=False)
    auto: bool = field(default=True)
    depth: int = field(default=0)
    tasks: int = field(default=0, init=False, repr=False)
    parent: Optional[LogProgress] = field(default=None, init=False, repr=False)
    children: list[LogProgress] = field(default_factory=list, init=False, repr=False)
    logger: Callable[..., None] | None = field(default_factory=None)

    def __post_init__(self):
        self.tasks = self.steps
        self.selfreport()
        return

    @property
    def state(self) -> str:
        dash = "-" * (3 + 2 * self.depth)
        k = self.step
        n = self.steps
        r = 1 if n == 0 else k / n
        if self.depth == 0:
            return f"Progress {dash} {self.title or self.name}: {k}/{n} ({r:.2%})"
        else:
            return f"{self.name or 'Progress'} {dash} {self.title}: {k}/{n} ({r:.2%})"

    @property
    def done(self) -> bool:
        return self.tasks <= 0

    def report(self):
        if self.logger is not None:
            self.logger(self.state)
        return

    def selfreport(self):
        if self.auto:
            self.report()
        return

    def subtask(self, title: str, steps: int = 1, step: int = 0, auto: Optional[bool] = None):
        self.tasks += 1
        auto = self.auto if auto is None else auto
        child = LogProgress(
            name=self.name,
            title=title,
            steps=steps,
            auto=auto,
            depth=self.depth + 1,
            logger=self.logger,
        )
        child.parent = self
        self.children.append(child)
        return child

    def next(self, is_step: bool = True):
        if self.done:
            self.selfreport()
            return
        self.tasks -= 1
        if is_step:
            self.step += 1
            self.selfreport()
        if self.done and self.parent is not None:
            self.parent.next(is_step=False)
        return
