#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

import json
from typing import Generator

import behave_webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

import behave
import behave.model
from behave.model import Feature
from behave.model import Row
from behave.model import Scenario

# for modifications, not import
from behave.model import Table
from behave.runner import Context

# from behave import fixture
# from behave import use_fixture
from behave.tag_matcher import ActiveTagMatcher
from behave.tag_matcher import setup_active_tag_values
from behave.userdata import UserData

# ----------------------------------------------------------------
# MODIFICATIONS
# ----------------------------------------------------------------


def get_feature_tags(feature: Feature) -> list[behave.model.Tag]:
    return feature.effective_tags


def get_scenario_tags(scenario: Scenario) -> list[behave.model.Tag]:
    return scenario.effective_tags


def get_context_table(ctx: Context) -> Table:
    return ctx.table


def get_context_table_rows(ctx: Context) -> list[Row]:
    rows: list[Row] = get_context_table(ctx).rows
    return rows


def get_context_table_rows_unjson(ctx: Context) -> Generator[dict, None, None]:
    rows = get_context_table_rows(ctx)
    for row in rows:
        row = row.as_dict()
        for key, value in row.items():
            try:
                row[key] = json.loads(value)
            except Exception:
                pass
        yield row


# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "ActiveTagMatcher",
    "ChromeOptions",
    "Context",
    "Feature",
    "Scenario",
    "Table",
    "UserData",
    "behave",
    "behave_webdriver",
    "get_context_table",
    "get_context_table_rows",
    "get_context_table_rows_unjson",
    "get_feature_tags",
    "get_scenario_tags",
    "setup_active_tag_values",
]
