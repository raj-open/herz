#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Contains steps for hello-world behavioural tests.
'''

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from thirdparty.behave import *
from thirdparty.types import *

from core.decorators import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'given_browser_open',
    'then_browser_at_url',
    'then_see_title',
    'then_see_heading',
]

# ----------------------------------------------------------------
# GIVEN, WHEN, THEN
# ----------------------------------------------------------------


@behave.given('browser is opened to "{url}"')
@add_webdriver_from_context
def given_browser_open(
    ctx: Context,
    # DEV-NOTE: from decorator
    userdata: UserData,
    www: behave_webdriver.Chrome,
    # end decorator args
    url: str,
):
    www.open_url(url=url)
    return


@behave.then('should be at url "{url}"')
@add_webdriver_from_context
def then_browser_at_url(
    ctx: Context,
    # DEV-NOTE: from decorator
    userdata: UserData,
    www: behave_webdriver.Chrome,
    # end decorator args
    url: str,
):
    url_ = www.current_url
    assert url_.rstrip('/') == url.rstrip('/')
    return


@behave.then('should see title "{title}"')
@add_webdriver_from_context
def then_see_title(
    ctx: Context,
    # DEV-NOTE: from decorator
    userdata: UserData,
    www: behave_webdriver.Chrome,
    # end decorator args
    title: str,
):
    element = www.find_element_by_xpath(f'//title[contains(text(), "{title}")]')
    assert element is not None
    return


@behave.then('should see heading "{title}"')
@add_webdriver_from_context
def then_see_heading(
    ctx: Context,
    # DEV-NOTE: from decorator
    userdata: UserData,
    www: behave_webdriver.Chrome,
    # end decorator args
    title: str,
):
    element = www.find_element_by_xpath(f'//h1[contains(text(), "{title}")]')
    assert element is not None
    return
