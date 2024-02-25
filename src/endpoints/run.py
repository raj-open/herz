#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This file contains the main process.
If called from e.g. cli.py or api.py, must initialise all paths.
'''

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ..thirdparty.misc import *

from ..core.log import *
from ..models.app import *
from ..models.user import *
from . import right_ventricle

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'process',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


@echo_function(tag='ENDPOINT {case.endpoint}', level=LOG_LEVELS.INFO)
def process(cfg: AppConfig, case: RequestConfig):
    '''
    The main process.

    **NOTE:** This process assumes that paths to

    - environment
    - session
    - logging
    - config

    have been set
    '''
    timer = Timer(
        name=f'Elapsed time for {case.endpoint}',
        text='{name}: {:.2f}s',
        logger=log_info,
    )

    match case.endpoint:
        case EnumEndpoint.RIGHT_VENTRICLE as ep:
            timer.start()
            right_ventricle.endpoint(case=case, cfg=cfg)
            timer.stop()

        case _ as ep if isinstance(ep, EnumEndpoint):
            raise ValueError(f'No endpoint established for `{ep.value}`.')

        case _ as value:
            raise ValueError(f'No endpoint established for `{value}`.')

    return
