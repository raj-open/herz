# language: en

@skip
Feature: Hello world
    As a web surfer,
    I want to open a few urls,
    And see that the pages and their contents are loaded.

    Scenario: A scenario in which nothing happens
        Given nothing happened
        Then nothing should happen

    Scenario: Open google website
        Given browser is opened to "https://www.google.co.uk"
        Then should be at url "https://www.google.co.uk"
        Given 3 seconds have passed
        Then should see title "Google"

    Scenario: Open mock website
        Given browser is opened to "https://mockaroo.com/datasets"
        Then should be at url "https://mockaroo.com/datasets"
        Given 3 seconds have passed
        Then should see heading "My Datasets"
