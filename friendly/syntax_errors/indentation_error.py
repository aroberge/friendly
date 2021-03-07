from ..my_gettext import current_lang
from ..token_utils import remove_meaningless_tokens


def set_cause_indentation_error(value, statement):
    _ = current_lang.translate

    value = str(value)
    if "unexpected indent" in value:
        this_case = _("The line identified above is more indented than expected.\n")
    elif "expected an indented block" in value:
        this_case = _(
            "The line identified above\n"
            "was expected to begin a new indented block.\n"
        )
    else:
        this_case = _("The line identified above is less indented than expected.\n")

    if (
        len(statement.all_statements) > 1
        and len(statement.tokens) == 1
        and statement.tokens[0].is_string()
    ):
        prev_statement = statement.all_statements[-2]
        prev_tokens = remove_meaningless_tokens(prev_statement)
        if len(prev_tokens) == 1 and prev_tokens[0].is_string():
            additional = _(
                "However, line {number}, which is identified as having a problem,\n"
                "consists of a single string which is also the case\n"
                "for the preceding line.\n"
                "Perhaps you meant to include a continuation character, `\\`,\n"
                "at the end of line {preceding}.\n"
            ).format(number=statement.linenumber, preceding=statement.linenumber - 1)

            return this_case + "\n" + additional

    return this_case
