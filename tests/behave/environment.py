#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This file provides tearup / teardown for all features.
Cf. <https://behave.readthedocs.io/en/stable/api.html>.
"""

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from core.decorators import *
from thirdparty.behave import *

# ----------------------------------------------------------------
# HOOKS
# ----------------------------------------------------------------


@add_data_from_context
def before_all(
    ctx: Context,
    # DEV-NOTE: from decorato
    userdata: UserData,
    # end decorator args
):
    return


# ----------------
# NOTE:
# So that developer can inspect files manually,
# do not remove folders at end of tests.
# Use 'just clean' insetad to remove artefacts.
# ----------------
@add_data_from_context
def after_all(
    ctx: Context,
    # DEV-NOTE: from decorator
    userdata: UserData,
    # end decorator args
):
    return


@add_data_from_context
def before_feature(
    ctx: Context,
    # DEV-NOTE: from decorator
    userdata: UserData,
    # end decorator args
    feature: Feature,
):
    return


@add_data_from_context
def after_feature(
    ctx: Context,
    # DEV-NOTE: from decorator
    userdata: UserData,
    # end decorator args
    feature: Feature,
):
    return


@add_data_from_context
def before_scenario(
    ctx: Context,
    # DEV-NOTE: from decorator
    userdata: UserData,
    # end decorator args
    scenario: Scenario,
):
    # for tag in get_scenario_tags(scenario):
    #     match tag:
    #         case _:
    #             pass
    return


@add_data_from_context
def after_scenario(
    ctx: Context,
    # DEV-NOTE: from decorator
    userdata: UserData,
    # end decorator args
    scenario: Scenario,
):
    # for tag in get_scenario_tags(scenario):
    #     match tag:
    #         case _:
    #             pass
    return
