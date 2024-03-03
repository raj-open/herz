#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Starting point for programme executed in CLI mode.
'''

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

import os
import sys

os.chdir(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.getcwd())

from .setup import config
from .models.app import *
from .models.user import *
from .queries.console.cli import *
from .features import *

# ----------------------------------------------------------------
# LOCAL CONSTANTS, SETTINGS
# ----------------------------------------------------------------

PID = os.getpid()

# ----------------------------------------------------------------
# EXECUTION
# ----------------------------------------------------------------

if __name__ == '__main__':
    info = config.INFO
    args = CliArguments(info=info).parse(*sys.argv[1:])

    # handle simple mode immediately
    if args.mode == EnumProgrammeMode.VERSION:
        print(config.VERSION)
        exit(0)

    # initialise app
    config.set_pid(PID)
    config.set_path_env(args.env)
    config.set_path_logging(args.log)
    config.set_path_session(args.session)
    config.initialise_application(name='app', pid=PID, log_pid='PIDs', debug=args.debug)

    # get configurations once
    cfg = config.load_internal_config()
    requests = config.load_user_requests(args.requests)

    # run process
    for case in requests:
        run.process(cfg=cfg, case=case)
