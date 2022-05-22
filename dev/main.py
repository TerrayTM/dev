import argparse

from dev.clean import CleanTask
from dev.constants import (RC_OK, TASK_CLEAN, TASK_INSTALL, TASK_LINT,
                           TASK_LIST, TASK_TEST, TASK_UNINSTALL)
from dev.install import InstallTask
from dev.lint import LintTask
from dev.test import TestTask
from dev.uninstall import UninstallTask


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="dev",
        description="Dev tools CLI for performing common development tasks.",
    )
    parser.add_argument("action", choices=TASK_LIST)
    args = parser.parse_args()
    rc = RC_OK

    if args.action == TASK_CLEAN:
        rc = CleanTask.execute()
    elif args.action == TASK_INSTALL:
        rc = InstallTask.execute()
    elif args.action == TASK_UNINSTALL:
        rc = UninstallTask.execute()
    elif args.action == TASK_TEST:
        rc = TestTask.execute()
    elif args.action == TASK_LINT:
        rc = LintTask.execute()

    return rc


if __name__ == "__main__":
    raise SystemExit(main())
