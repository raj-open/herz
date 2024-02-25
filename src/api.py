#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Starting point for programme executed in API mode.
'''

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

import os
import sys

os.chdir(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.getcwd())

from .setup import config
from .thirdparty.fastapi import *
from .queries.console.api import *
from .ui import *

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

    config.set_pid(PID)
    config.set_path_env(args.env)
    config.set_path_logging(args.log)
    config.set_path_session(args.session)

    config.initialise_application(name='api', pid=PID, log_pid='PIDs', debug=args.debug)

    app = create_ui(debug=args.debug)

    uvicorn.run(
        app=app,
        host=config.get_http_ip(),
        port=config.get_http_port(),
    )
