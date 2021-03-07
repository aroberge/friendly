"""Theme inspired from the Twilight coding scheme.

Currently, pygments does not include a "twilight" theme but this
could happen at any time. To avoid a potential conflict, I chose a different name.

Twilight can be translated in French as either crépuscule or as brunante,
with the former being the most often-used term. However, I chose the second
since the word 'brunante' starts with 'brun' which is French for 'brown',
and many colours in Twilight are essentially different shades of brown, yellow,
and orange. With these dominant colours, it might be more reminescent of
autumn ... but there is already a pygments theme named autumn.
"""

from pygments.style import Style
from pygments.token import (
    Keyword,
    Name,
    Comment,
    String,
    Error,
    Text,
    Number,
    Operator,
    Generic,
    Whitespace,
    Punctuation,
    Other,
    Literal,
)


colours = {
    "yellow": "#F0E68C",
    "orange": "#FF8243",
    "red": "#D92121",
    "white": "#F4F0EC",
    "beige": "#DEB887",
    "blue": "#87CEEB",
    "gray": "#999999",
    "green": "#87A96B",
    "mauve": "#9370DB",
}

my_style = {
    "builtins": colours["yellow"],
    "code": colours["beige"],
    "comments": colours["gray"],
    "keywords": colours["yellow"],
    "numbers": colours["white"],
    "operators": colours["blue"],
    "string": colours["green"],
    "text": colours["white"],
    "TrueFalseNone": colours["orange"],
    "Exception": colours["red"],
    "diagnostics": "#FF00FF",  # Magenta; when trying to figure out a category
}


# Since we use Rich's pretty(), we try to ensure that the colours
# are consistent.  pretty() highlight objects based on their repr name
# with the following choices:

rich_style = {
    "markdown.code": my_style["code"],
    "repr.tag_name": my_style["code"],  # for consistency with Python
    "markdown.h1": my_style["diagnostics"],
    # Exception message; location header H2
    "markdown.h2": f"{colours['red']}",
    "markdown.h3": colours["mauve"],  # likely cause
    "markdown.h4": colours["orange"],  # warning header
    "markdown.link": f"underline {my_style['keywords']}",
    "repr.url": my_style["keywords"],
    "repr.number": my_style["numbers"],
    # The next three are identical for pygments, so we keep them identical
    "repr.bool_false": my_style["TrueFalseNone"],
    "repr.bool_true": my_style["TrueFalseNone"],
    "repr.none": my_style["TrueFalseNone"],
    #
    "repr.str": my_style["string"],
    "repr.error": my_style["Exception"],
    "repr.indent": my_style["comments"],
}

my_style.update(**rich_style)


class BrunanteStyle(Style):
    """
    This style was originally inspired by the Twilight scheme
    """

    background_color = "#101010"
    default_style = "#363636"

    styles = {
        Text: my_style["text"],  # class:  ''
        Whitespace: "",  # class: 'w'
        Error: my_style["Exception"],  # class: 'err'
        Other: my_style["string"],  # class 'x'
        #
        Comment: my_style["comments"],  # class: 'c'
        Comment.Multiline: my_style["comments"],  # class: 'cm'
        Comment.Preproc: my_style["comments"],  # class: 'cp'
        Comment.Single: my_style["comments"],  # class: 'c1'
        Comment.Special: my_style["comments"],  # class: 'cs'
        #
        Generic: my_style["text"],  # class: 'g'
        Generic.Deleted: my_style["Exception"],  # class: 'gd'
        Generic.Emph: my_style["text"],  # class: 'ge'
        Generic.Error: my_style["Exception"],  # class: 'gr'
        Generic.Heading: my_style["text"],  # class: 'gh'
        Generic.Inserted: my_style["text"],  # class: 'gi'
        Generic.Output: my_style["text"],  # class: 'go'
        Generic.Prompt: my_style["keywords"],  # class: 'gp'
        Generic.Strong: my_style["text"],  # class: 'gs'
        Generic.Subheading: my_style["text"],  # class: 'gu'
        Generic.Traceback: my_style["Exception"],  # class: 'gt'
        #
        Keyword: my_style["keywords"],  # class: 'k'
        Keyword.Constant: my_style["TrueFalseNone"],  # class: 'kc'
        Keyword.Declaration: my_style["keywords"],  # class: 'kd'
        Keyword.Namespace: my_style["keywords"],  # class: 'kn'
        Keyword.Pseudo: my_style["keywords"],  # class: 'kp'
        Keyword.Reserved: my_style["keywords"],  # class: 'kr'
        Keyword.Type: my_style["keywords"],  # class: 'kt'
        #
        Literal: my_style["text"],  # class: 'l'
        Literal.Date: my_style["text"],  # class: 'ld'
        #
        Name: my_style["code"],  # class: 'n'
        Name.Attribute: my_style["code"],  # class: 'na'
        # The following is for file path in tracebacks and Python builtins.
        Name.Builtin: my_style["builtins"],  # class: 'nb'
        Name.Builtin.Pseudo: my_style["builtins"],  # class: 'bp'
        Name.Class: my_style["code"],  # class: 'nc'
        Name.Constant: my_style["code"],  # class: 'no'
        Name.Decorator: my_style["code"],  # class: 'nd'
        Name.Entity: my_style["code"],  # class: 'ni'
        Name.Exception: my_style["Exception"],  # class: 'ne'
        Name.Function: my_style["code"],  # class: 'nf'
        Name.Property: my_style["code"],  # class: 'py'
        Name.Label: my_style["code"],  # class: 'nl'
        Name.Namespace: my_style["code"],  # class: 'nn'
        Name.Other: my_style["diagnostics"],  # class: 'nx'
        Name.Tag: my_style["code"],  # class: 'nt' - like a keyword
        Name.Variable: my_style["text"],  # class: 'nv'
        Name.Variable.Class: my_style["code"],  # class: 'vc'
        Name.Variable.Global: my_style["code"],  # class: 'vg'
        Name.Variable.Instance: my_style["text"],  # class: 'vi'
        #
        Number: my_style["numbers"],  # class: 'm'
        Number.Float: my_style["numbers"],  # class: 'mf'
        Number.Hex: my_style["numbers"],  # class: 'mh'
        Number.Integer: my_style["numbers"],  # class: 'mi'
        Number.Integer.Long: my_style["numbers"],  # class: 'il'
        Number.Oct: my_style["numbers"],  # class: 'mo'
        #
        Operator: my_style["operators"],  # class: 'o'
        Operator.Word: my_style["operators"],  # class: 'ow'
        #
        Punctuation: my_style["operators"],  # class: 'p'
        #
        String: my_style["string"],  # class: 's'
        String.Backtick: my_style["string"],  # class: 'sb'
        String.Char: my_style["string"],  # class: 'sc'
        String.Doc: my_style["string"],  # class: 'sd'
        String.Double: my_style["string"],  # class: 's2'
        String.Escape: my_style["string"],  # class: 'se'
        String.Heredoc: my_style["string"],  # class: 'sh'
        String.Interpol: my_style["string"],  # class: 'si'
        String.Other: my_style["string"],  # class: 'sx'
        String.Regex: my_style["string"],  # class: 'sr'
        String.Single: my_style["string"],  # class: 's1'
        String.Symbol: my_style["string"],  # class: 'ss'
    }
