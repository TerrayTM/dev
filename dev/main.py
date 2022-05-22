import argparse

from dev.clean import CleanTask
from dev.constants import RC_OK
from dev.install import InstallTask
from dev.lint import LintTask
from dev.test import TestTask
from dev.uninstall import UninstallTask


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="dev",
        description="Dev tools CLI for performing common development tasks.",
    )
    parser.add_argument(
        "action", choices=["clean", "install", "uninstall", "test", "lint"]
    )
    args = parser.parse_args()
    rc = RC_OK

    if args.action == "clean":
        rc = CleanTask.execute()
    elif args.action == "install":
        rc = InstallTask.execute()
    elif args.action == "uninstall":
        rc = UninstallTask.execute()
    elif args.action == "test":
        rc = TestTask.execute()
    elif args.action == "lint":
        rc = LintTask.execute()

    return rc


if __name__ == "__main__":
    raise SystemExit(main())
