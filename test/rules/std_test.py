"""Tests for the standard set of rules."""
import pytest

from sqlfluff.core.rules import get_ruleset
from sqlfluff.core.config import FluffConfig
from sqlfluff.utils.testing.rules import assert_rule_raises_violations_in_file


@pytest.mark.parametrize(
    "rule,path,violations",
    [
        ("L001", "indentation_errors.sql", [(4, 24)]),
        ("L002", "indentation_errors.sql", [(3, 1), (4, 1)]),
        (
            "L003",
            "indentation_errors.sql",
            [(2, 1), (3, 1), (4, 1), (5, 1)],
        ),
        (
            "L004",
            "indentation_errors.sql",
            [(3, 1), (4, 1), (5, 1)],
        ),
        # Check we get comma (with leading space/newline) whitespace errors
        # NB The newline before the comma, should report on the comma, not the newline
        # for clarity.
        ("L005", "whitespace_errors.sql", [(2, 9)]),
        # Check we get comma (with incorrect trailing space) whitespace errors,
        # but also no false positives on line 4 or 5.
        ("L008", "whitespace_errors.sql", [(3, 12)]),
        # Check we get operator whitespace errors and it works with brackets
        (
            "L006",
            "operator_errors.sql",
            [(7, 6), (7, 7), (7, 9), (7, 10), (7, 12), (7, 13)],
        ),
        (
            "L039",
            "operator_errors.sql",
            [(3, 8), (4, 10)],
        ),
        ("L007", "operator_errors.sql", [(5, 9)]),
        # Check we DO get a violation on line 2 but NOT on line 3 (between L006 & L039)
        (
            "L006",
            "operator_errors_negative.sql",
            [(5, 6), (5, 7)],
        ),
        (
            "L039",
            "operator_errors_negative.sql",
            [(2, 6), (2, 9)],
        ),
        # Hard indentation errors
        (
            "L003",
            "indentation_error_hard.sql",
            [
                (2, 1),
                (6, 1),
                (9, 1),
                (11, 15),
                (12, 1),
                (12, 33),
                (13, 15),
                (14, 1),
                (14, 36),
                (18, 1),
                (19, 1),
                (20, 1),
            ],
        ),
        # Check bracket handling with closing brackets and contained indents works.
        ("L003", "indentation_error_contained.sql", []),
        # Check we handle block comments as expect. Github #236
        (
            "L016",
            "block_comment_errors.sql",
            # Errors should flag on the first element of the line.
            [(1, 1), (2, 5), (4, 5)],
        ),
        ("L016", "block_comment_errors_2.sql", [(1, 1), (2, 1)]),
        # Column references
        ("L027", "column_references.sql", [(1, 8)]),
        ("L027", "column_references_bare_function.sql", []),
        ("L026", "column_references.sql", [(1, 11)]),
        ("L025", "column_references.sql", [(2, 11)]),
        # Distinct and Group by
        ("L021", "select_distinct_group_by.sql", [(1, 8)]),
        # Make sure that ignoring works as expected
        ("L006", "operator_errors_ignore.sql", [(10, 8), (10, 9)]),
        (
            "L031",
            "aliases_in_join_error.sql",
            [(6, 15), (7, 19), (8, 16)],
        ),
        (
            "L046",
            "heavy_templating.sql",
            [(12, 13), (12, 25)],
        ),
    ],
)
def test__rules__std_file(rule, path, violations):
    """Test the linter finds the given errors in (and only in) the right places."""
    assert_rule_raises_violations_in_file(
        rule=rule,
        fpath="test/fixtures/linter/" + path,
        violations=violations,
        fluff_config=FluffConfig(overrides=dict(rules=rule, dialect="ansi")),
    )


@pytest.mark.parametrize(
    "rule_config_dict",
    [
        {"allow_scalar": "blah"},
        {"single_table_references": "blah"},
        {"unquoted_identifiers_policy": "blah"},
        {"L010": {"capitalisation_policy": "blah"}},
        {"L011": {"aliasing": "blah"}},
        {"L012": {"aliasing": "blah"}},
        {"L014": {"extended_capitalisation_policy": "blah"}},
        {"L030": {"capitalisation_policy": "blah"}},
    ],
)
def test_improper_configs_are_rejected(rule_config_dict):
    """Ensure that unsupported configs raise a ValueError."""
    config = FluffConfig(
        configs={"rules": rule_config_dict}, overrides={"dialect": "ansi"}
    )
    with pytest.raises(ValueError):
        get_ruleset().get_rulepack(config)
