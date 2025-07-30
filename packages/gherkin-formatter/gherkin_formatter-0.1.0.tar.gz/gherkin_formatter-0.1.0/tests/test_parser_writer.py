from typing import Any, Optional

from gherkin_formatter.parser_writer import GherkinFormatter


def create_docstring_step_ast(
    content: str, media_type: Optional[str] = None
) -> dict[str, Any]:
    """
    Helper function to create a minimal AST for testing docstring formatting.

    :param content: The content of the docstring.
    :type content: str
    :param media_type: The media type of the docstring, defaults to None.
    :type media_type: Optional[str]
    :return: A dictionary representing the minimal AST.
    :rtype: Dict[str, Any]
    """
    docstring_node: dict[str, Any] = {"content": content, "delimiter": '"""'}
    if media_type:
        docstring_node["mediaType"] = media_type

    step_node: dict[str, Any] = {
        "keyword": "Given ",
        "text": "a step with a docstring",
        "docString": docstring_node,
    }
    feature_ast: dict[str, Any] = {
        "feature": {
            "keyword": "Feature",
            "name": "Test Feature",
            "language": "en",
            "children": [
                {
                    "scenario": {
                        "keyword": "Scenario",
                        "name": "Test Scenario",
                        "steps": [step_node],
                        "tags": [],
                    }
                }
            ],
            "tags": [],
        },
        "comments": [],
    }
    return feature_ast


def test_format_json_docstring_without_mediatype_scenario_from_issue_4spaces() -> None:
    """
    Test JSON docstring formatting (no mediaType) with 4-space indent.
    Matches a scenario from an issue.
    """
    json_content: str = '{\n"hello": "world",\n"greeting": "Hello, World!"\n}'
    ast: dict[str, Any] = create_docstring_step_ast(json_content)
    formatter: GherkinFormatter = GherkinFormatter(ast, tab_width=4)

    expected_lines: list[str] = [
        "Feature: Test Feature",
        "",
        "    Scenario: Test Scenario",
        "        Given a step with a docstring",
        '            """',
        "            {",
        '                "hello": "world",',
        '                "greeting": "Hello, World!"',
        "            }",
        '            """',
    ]
    expected_output: str = "\n".join(expected_lines)
    actual_output: str = formatter.format().strip()
    assert actual_output == expected_output


def test_format_rule_with_scenario_outline() -> None:
    """
    Test formatting of a Feature with a Rule containing a Scenario Outline.
    """
    feature_ast: dict[str, Any] = {
        "feature": {
            "keyword": "Feature",
            "name": "Feature with Rule and Scenario Outline",
            "language": "en",
            "children": [
                {
                    "rule": {
                        "keyword": "Rule",
                        "name": "My Rule",
                        "children": [
                            {
                                "scenario": {
                                    "keyword": "Scenario Outline",
                                    "name": "My Scenario Outline",
                                    "steps": [
                                        {
                                            "keyword": "Given ",
                                            "text": "a step with <variable>",
                                        },
                                    ],
                                    "examples": [
                                        {
                                            "keyword": "Examples",
                                            "name": "",
                                            "tableHeader": {
                                                "cells": [{"value": "variable"}]
                                            },
                                            "tableBody": [
                                                {"cells": [{"value": "value1"}]},
                                                {"cells": [{"value": "value2"}]},
                                            ],
                                            "tags": [],
                                        }
                                    ],
                                    "tags": [],
                                }
                            }
                        ],
                    }
                }
            ],
            "tags": [],
        },
        "comments": [],
    }
    formatter: GherkinFormatter = GherkinFormatter(feature_ast, tab_width=2)
    expected_lines: list[str] = [
        "Feature: Feature with Rule and Scenario Outline",
        "",
        "  Rule: My Rule",
        "",
        "    Scenario Outline: My Scenario Outline",
        "      Given a step with <variable>",
        "",
        "      Examples:",
        "        | variable |",
        "        | value1   |",
        "        | value2   |",
    ]
    expected_output: str = "\n".join(expected_lines)
    actual_output: str = formatter.format().strip()
    assert actual_output == expected_output


def test_format_minimal_feature_file() -> None:
    """
    Test formatting of a minimal feature file (just Feature: Name).
    """
    feature_ast: dict[str, Any] = {
        "feature": {
            "keyword": "Feature",
            "name": "Minimal",
            "language": "en",
            "children": [],
            "tags": [],
        },
        "comments": [],
    }
    formatter: GherkinFormatter = GherkinFormatter(feature_ast, tab_width=2)
    expected_lines: list[str] = [
        "Feature: Minimal",
    ]
    expected_output: str = "\n".join(expected_lines)
    actual_output: str = formatter.format().strip()
    assert actual_output == expected_output


def test_format_empty_feature_file() -> None:
    """
    Test formatting of an empty feature file (represented as None feature node).
    """
    feature_ast: dict[str, Any] = {
        "feature": None,
        "comments": [],
    }
    formatter: GherkinFormatter = GherkinFormatter(feature_ast, tab_width=2)
    expected_output: str = (
        ""  # Formatter produces a single newline, strip makes it empty
    )
    actual_output: str = formatter.format().strip()
    assert actual_output == expected_output


def test_format_feature_with_comments() -> None:
    """
    Test formatting of a feature file with comments.
    Checks for preservation and placement of comments.
    """
    feature_ast: dict[str, Any] = {
        "feature": {
            "keyword": "Feature",
            "name": "Comments Test",
            "language": "en",
            "children": [
                {
                    "scenario": {
                        "keyword": "Scenario",
                        "name": "Scenario with comments",
                        "steps": [
                            {"keyword": "Given ", "text": "a step"},
                        ],
                        "tags": [],
                    }
                }
            ],
            "tags": [],
        },
        "comments": [
            {"text": "# Comment before feature"},
            {"text": "# Another comment before scenario, associated with feature"},
            {"text": "# Comment before step, associated with scenario"},
        ],
    }
    formatter: GherkinFormatter = GherkinFormatter(feature_ast, tab_width=2)
    expected_lines: list[str] = [
        "# Comment before feature",
        "# Another comment before scenario, associated with feature",
        "# Comment before step, associated with scenario",
        "Feature: Comments Test",
        "",
        "  Scenario: Scenario with comments",
        "    Given a step",
    ]
    expected_output: str = "\n".join(expected_lines)
    actual_output: str = formatter.format().strip()
    assert actual_output == expected_output


def test_format_background_section() -> None:
    """
    Test formatting of a Feature with a Background section.
    """
    feature_ast: dict[str, Any] = {
        "feature": {
            "keyword": "Feature",
            "name": "Background Test",
            "language": "en",
            "children": [
                {
                    "background": {
                        "keyword": "Background",
                        "name": "",
                        "steps": [
                            {"keyword": "Given ", "text": "a logged-in user"},
                            {"keyword": "And ", "text": "the user has a subscription"},
                        ],
                    }
                },
                {
                    "scenario": {
                        "keyword": "Scenario",
                        "name": "Scenario After Background",
                        "steps": [
                            {
                                "keyword": "When ",
                                "text": "the user accesses a premium feature",
                            },
                            {"keyword": "Then ", "text": "access is granted"},
                        ],
                        "tags": [],
                    }
                },
            ],
            "tags": [],
        },
        "comments": [],
    }
    formatter: GherkinFormatter = GherkinFormatter(feature_ast, tab_width=2)
    expected_lines: list[str] = [
        "Feature: Background Test",
        "",
        "  Background:",
        "    Given a logged-in user",
        "    And the user has a subscription",
        "",
        "  Scenario: Scenario After Background",
        "    When the user accesses a premium feature",
        "    Then access is granted",
    ]
    expected_output: str = "\n".join(expected_lines)
    actual_output: str = formatter.format().strip()
    assert actual_output == expected_output


def test_format_scenario_outline_with_examples() -> None:
    """
    Test formatting of a Scenario Outline with an Examples table.
    """
    feature_ast: dict[str, Any] = {
        "feature": {
            "keyword": "Feature",
            "name": "Scenario Outline Test",
            "language": "en",
            "children": [
                {
                    "scenario": {
                        "keyword": "Scenario Outline",
                        "name": "Outline Example",
                        "steps": [
                            {"keyword": "Given ", "text": "a user with <id>"},
                            {
                                "keyword": "When ",
                                "text": "the user requests <resource>",
                            },
                            {
                                "keyword": "Then ",
                                "text": "the response should be <status>",
                            },
                        ],
                        "tags": [],
                        "examples": [
                            {
                                "keyword": "Examples",
                                "name": "",
                                "tableHeader": {
                                    "cells": [
                                        {"value": "id"},
                                        {"value": "resource"},
                                        {"value": "status"},
                                    ]
                                },
                                "tableBody": [
                                    {
                                        "cells": [
                                            {"value": "100"},
                                            {"value": "profile"},
                                            {"value": "200"},
                                        ]
                                    },
                                    {
                                        "cells": [
                                            {"value": "101"},
                                            {"value": "settings"},
                                            {"value": "404"},
                                        ]
                                    },
                                ],
                                "tags": [],
                            }
                        ],
                    }
                }
            ],
            "tags": [],
        },
        "comments": [],
    }
    formatter: GherkinFormatter = GherkinFormatter(feature_ast, tab_width=2)
    expected_lines: list[str] = [
        "Feature: Scenario Outline Test",
        "",
        "  Scenario Outline: Outline Example",
        "    Given a user with <id>",
        "    When the user requests <resource>",
        "    Then the response should be <status>",
        "",
        "    Examples:",
        "      | id  | resource | status |",
        "      | 100 | profile  | 200    |",
        "      | 101 | settings | 404    |",
    ]
    expected_output: str = "\n".join(expected_lines)
    actual_output: str = formatter.format().strip()
    assert actual_output == expected_output


def test_format_scenario_with_tags() -> None:
    """
    Test formatting of a Scenario with tags.
    """
    feature_ast: dict[str, Any] = {
        "feature": {
            "keyword": "Feature",
            "name": "Tags Test",
            "language": "en",
            "children": [
                {
                    "scenario": {
                        "keyword": "Scenario",
                        "name": "Tagged Scenario",
                        "steps": [
                            {"keyword": "Given ", "text": "a step"},
                        ],
                        "tags": [{"name": "@tag1"}, {"name": "@tag2"}],
                    }
                }
            ],
            "tags": [],
        },
        "comments": [],
    }
    formatter: GherkinFormatter = GherkinFormatter(feature_ast, tab_width=2)
    expected_lines: list[str] = [
        "Feature: Tags Test",
        "",
        "  @tag1 @tag2",
        "  Scenario: Tagged Scenario",
        "    Given a step",
    ]
    expected_output: str = "\n".join(expected_lines)
    actual_output: str = formatter.format().strip()
    assert actual_output == expected_output


def test_format_scenario_with_multiple_steps_and_varying_indentation() -> None:
    """
    Test formatting of a Scenario with multiple steps and varying initial
    indentation and spacing in step text. The formatter should normalize these.
    """
    feature_ast: dict[str, Any] = {
        "feature": {
            "keyword": "Feature",
            "name": "Indentation Test",
            "language": "en",
            "children": [
                {
                    "scenario": {
                        "keyword": "Scenario",
                        "name": "Mixed Indentation Scenario",
                        "steps": [
                            {
                                "keyword": "Given ",
                                "text": "  a step with leading spaces",
                            },
                            {
                                "keyword": "When ",
                                "text": "another step with trailing spaces   ",
                            },
                            {"keyword": "Then ", "text": "  a third step with both  "},
                        ],
                        "tags": [],
                    }
                }
            ],
            "tags": [],
        },
        "comments": [],
    }
    formatter: GherkinFormatter = GherkinFormatter(feature_ast, tab_width=2)
    expected_lines: list[str] = [
        "Feature: Indentation Test",
        "",
        "  Scenario: Mixed Indentation Scenario",
        "    Given a step with leading spaces",
        "    When another step with trailing spaces",
        "    Then a third step with both",
    ]
    expected_output: str = "\n".join(expected_lines)
    actual_output: str = formatter.format().strip()
    assert actual_output == expected_output


def test_format_invalid_json_docstring_as_plain_text() -> None:
    """
    Test that invalid JSON content in a docstring is treated as plain text.
    """
    invalid_json_content: str = (
        '{\n"key": "value",\n"anotherkey": "anothervalue",trailingcomma\n}'
    )
    ast: dict[str, Any] = create_docstring_step_ast(invalid_json_content)
    formatter: GherkinFormatter = GherkinFormatter(ast, tab_width=2)

    expected_lines: list[str] = [
        "Feature: Test Feature",
        "",
        "  Scenario: Test Scenario",
        "    Given a step with a docstring",
        '      """',
        "      {",
        '      "key": "value",',
        '      "anotherkey": "anothervalue",trailingcomma',
        "      }",
        '      """',
    ]
    expected_output: str = "\n".join(expected_lines)
    actual_output: str = formatter.format().strip()
    assert actual_output == expected_output


def test_format_simple_string_not_mistaken_as_json() -> None:
    """
    Test that a simple plain string in a docstring is not mistaken for JSON
    and is formatted correctly as plain text.
    """
    plain_content: str = "This is just a simple string.\nWith two lines."
    ast: dict[str, Any] = create_docstring_step_ast(plain_content)
    formatter: GherkinFormatter = GherkinFormatter(ast, tab_width=2)

    expected_lines: list[str] = [
        "Feature: Test Feature",
        "",
        "  Scenario: Test Scenario",
        "    Given a step with a docstring",
        '      """',
        "      This is just a simple string.",
        "      With two lines.",
        '      """',
    ]
    expected_output: str = "\n".join(expected_lines)
    actual_output: str = formatter.format().strip()
    assert actual_output == expected_output


def test_format_json_docstring_already_formatted_different_indent() -> None:
    """
    Test that a JSON docstring, already formatted but with different indentation,
    is re-formatted according to the formatter's settings.
    """
    json_content_already_formatted: str = (
        '{\n    "key": "value",\n        "number": 123\n}'
    )
    ast: dict[str, Any] = create_docstring_step_ast(json_content_already_formatted)
    formatter: GherkinFormatter = GherkinFormatter(ast, tab_width=2)

    expected_lines: list[str] = [
        "Feature: Test Feature",
        "",
        "  Scenario: Test Scenario",
        "    Given a step with a docstring",
        '      """',
        "      {",
        '        "key": "value",',
        '        "number": 123',
        "      }",
        '      """',
    ]
    expected_output: str = "\n".join(expected_lines)
    actual_output: str = formatter.format().strip()
    assert actual_output == expected_output
