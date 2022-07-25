from dev.build import BuildTask
from dev.clean import CleanTask
from dev.count import CountTask
from dev.doc import DocTask
from dev.install import InstallTask
from dev.lint import LintTask
from dev.publish import PublishTask
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
    BuildTask,
    PublishTask,
    DocTask,
]
