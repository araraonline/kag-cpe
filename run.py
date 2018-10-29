import sys

import doit.cmd_base
import doit.doit_cmd

from doit.cmd_base import ModuleTaskLoader
from doit.doit_cmd import DoitMain

import dodo.main
import dodo.prepare


if __name__ == "__main__":
    cmd_args = sys.argv[1:]

    task1 = DoitMain(ModuleTaskLoader(dodo.prepare))
    task2 = DoitMain(ModuleTaskLoader(dodo.main))

    status1 = task1.run(cmd_args)
    if status1 not in (None, 0):
        sys.exit(status1)

    status2 = task2.run(cmd_args)
    if status2 not in (None, 0):
        sys.exit(status2)

    sys.exit(0)  # needed?
