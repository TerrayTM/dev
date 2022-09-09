import os
import shutil

from dev.constants import SETUP_FILE, ReturnCode
from dev.output import output
from dev.setup import parse_setup_file
from dev.subprocess import subprocess_run
from dev.tasks.task import Task


class UninstallTask(Task):
    def _perform(self) -> int:
        if not os.path.isfile(SETUP_FILE):
            output("Cannot find setup file.")
            return ReturnCode.FAILED

        setup_data = parse_setup_file(SETUP_FILE)

        if setup_data is None:
            output("Failed to parse setup file.")
            return ReturnCode.FAILED

        if setup_data.name is None:
            output("Failed to determine package name from setup file.")
            return ReturnCode.FAILED

        subprocess_run(["pip", "uninstall", "-y", setup_data.name], check_call=True)

        egg_folder = f"{setup_data.name.replace('-', '_')}.egg-info"
        if os.path.isdir(egg_folder):
            shutil.rmtree(egg_folder)

        return ReturnCode.OK
