from dev.clean import CleanTask
from dev.count import CountTask
from dev.install import InstallTask
from dev.lint import LintTask
from dev.run import RunTask
from dev.test import TestTask
from dev.uninstall import UninstallTask

TASKS = [
    CleanTask,
    InstallTask,
    UninstallTask,
    TestTask,
    LintTask,
    CountTask,
    RunTask,
]
