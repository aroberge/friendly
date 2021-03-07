from friendly import token_utils

# Note: most of the tests involving untokenize have
# been adapted from https://github.com/myint/untokenize


def check(source):
    tokens = token_utils.tokenize(source)
    new_source = token_utils.untokenize(tokens)
    assert source == new_source


def check_lines(source):
    lines = token_utils.get_lines(source)
    tokens = []
    for line in lines:
        tokens.extend(line)
    assert source == token_utils.untokenize(tokens)


def test_untokenize():
    check(
        '''

def zap():

    """Hello zap.

  """; 1


    x \t= \t\t  \t 1


'''
    )


def test_untokenize_with_tab_indentation():
    check(
        """
if True:
\tdef zap():
\t\tx \t= \t\t  \t 1
"""
    )


def test_untokenize_with_backslash_in_comment():
    check(
        r'''
def foo():
    """Hello foo."""
    def zap(): bar(1) # \
'''
    )


def test_untokenize_with_escaped_newline():
    check(
        r'''def foo():
    """Hello foo."""
    x = \
            1
'''
    )


def test_cpython_bug_35107():
    # Checking https://bugs.python.org/issue35107#msg328884
    check("#")
    check("#\n")


def test_last_line_empty():
    """If the last line contains only space characters with no newline
    Python's tokenizer drops this content. To ensure that the
    tokenize-untokenize returns the original value, we have introduced
    a fix in our utility functions"""

    source = "a\n  "
    source2 = "a\n\t"
    check(source)
    check(source2)

    check_lines(source)
    check_lines(source2)


source1 = "a = b"
source2 = "a = b # comment\n"
source3 = """
if True:
    a = b # comment
"""
tokens1 = token_utils.tokenize(source1)
tokens2 = token_utils.tokenize(source2)
lines3 = token_utils.get_lines(source3)


def test_dedent():
    new_tokens = token_utils.dedent(lines3[2], 4)
    assert new_tokens == tokens2


def test_indent():
    new_tokens = token_utils.indent(tokens2, 4)
    new_line_a = token_utils.untokenize(new_tokens)
    new_line_b = token_utils.untokenize(lines3[2])
    assert new_line_a == new_line_b


def test_self():
    with open(__file__, "r") as f:
        source = f.read()
    check(source)
