"""Implementation of Rule L007."""

from typing import List

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler

from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
    document_groups,
)
from sqlfluff.utils.reflow import ReflowSequence


@document_groups
@document_fix_compatible
@document_configuration
class Rule_L007(BaseRule):
    """Operators should follow a standard for being before/after newlines.

    **Anti-pattern**

    In this example, if ``operator_new_lines = after`` (or unspecified, as is the
    default), then the operator ``+`` should not be at the end of the second line.

    .. code-block:: sql

        SELECT
            a +
            b
        FROM foo


    **Best practice**

    If ``operator_new_lines = after`` (or unspecified, as this is the default),
    place the operator after the newline.

    .. code-block:: sql

        SELECT
            a
            + b
        FROM foo

    If ``operator_new_lines = before``, place the operator before the newline.

    .. code-block:: sql

        SELECT
            a +
            b
        FROM foo
    """

    name = "line-break.operators"
    aliases = ("LB03",)
    groups = ("all", "layout", "line-break")
    crawl_behaviour = SegmentSeekerCrawler({"binary_operator", "comparison_operator"})

    def _eval(self, context: RuleContext) -> List[LintResult]:
        """Operators should follow a standard for being before/after newlines.

        We use the memory to keep track of whitespace up to now, and
        whether the last code segment was an operator or not.
        Anchor is our signal as to whether there's a problem.

        We only trigger if we have an operator FOLLOWED BY a newline
        before the next meaningful code segment.
        """
        return (
            ReflowSequence.from_around_target(
                context.segment,
                root_segment=context.parent_stack[0],
                config=context.config,
            )
            .rebreak()
            .get_results()
        )
