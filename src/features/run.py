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
        case EnumEndpoint.RIGHT_VENTRICLE as feature:
            timer.start()
            try:
                right_ventricle.endpoint(feature=feature, case=case)
            except Exception as err:
                log_error(err)
            timer.stop()

        case _ as feature if isinstance(feature, EnumEndpoint):
            raise ValueError(f'No endpoint established for `{feature.value}`.')

        case _ as value:
            raise ValueError(f'No endpoint established for `{value}`.')

    return
