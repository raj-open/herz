#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Starting point for programme executed in API mode.
"""

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

import os
import sys

os.chdir(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.getcwd())

from .queries.console.api import *
from .setup import config
from .thirdparty.fastapi import *
from .ui import *

# ----------------------------------------------------------------
# LOCAL CONSTANTS, SETTINGS
# ----------------------------------------------------------------

PID = os.getpid()

# ----------------------------------------------------------------
# EXECUTION
# ----------------------------------------------------------------

if __name__ == "__main__":
    info = config.INFO
    args = CliArguments(info=info).parse(*sys.argv[1:])

    config.pid.set(PID)
    config.path_env.set(args.env)
    config.path_logging.set(args.log)
    config.path_session.set(args.session)

    config.initialise_application(name="api", log_pid="PIDs", debug=args.debug)

    app = create_ui(debug=args.debug)

    uvicorn.run(
        app=app,
        host=config.http_ip(),
        port=config.http_port(),
    )
