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

# As a reference, here is a list that includes most of the colours
# found in SublimeText's Twilight theme.
#
# The names chosen and grouping by categories is very subjective
#
# yellow: #F9EE98 #E9C062 #E0C589 #DDF2A4 #DAEFA3
# orange -> brown: #CF7D34 #CF6A4C #9B5C2E
# beige -> brown: #CDA869 #AC885B #9B703F
# pink/mauve: #D2A8A1 #9B859D
# red/pink: #F92672
# green: #8F9D6A
# grey -> blue: #5F5A60 #A7A7A7 #8A9A95 #7587A6
#
# Note that the actual look of a given colour might greatly depend
# on the editor/terminal in which it is
#
# Rather than using these specific values, let's choose some
# somewhat similar ones from the standard named colors
# https://en.wikipedia.org/wiki/List_of_colors:_A%E2%80%93F A to F
# https://en.wikipedia.org/wiki/List_of_colors:_G%E2%80%93M G to M
# https://en.wikipedia.org/wiki/List_of_colors:_N%E2%80%93Z N to Z
# using some primary classification

# Yellow: "#F9EE98"  No corresponding name
# Orange: #FF8243 Mango tango
# Red: #D92121 Maximum red
# Green: #87A96B Asparagus
# White: #F4F0EC Isabelline
# Beige: #D99A6C Tan (Crayola)
# Brown:
# Blue: #6699CC Blue gray
# Gray: #555555

colours = {
    "yellow": "#F9EE98",
    "orange": "#FF8243",
    "red": "#D92121",
    "white": "#F4F0EC",
    "beige": "#D99A6C",
    "blue": "#6699CC",
    "gray": "#555555",
    "green": "#87A96B",
}


#
# Since we use Rich's pretty(), we try to ensure that the colours
# are consistent.  pretty() highlight objects based on their repr name
# with the following choices:

# repr.brace
# repr.comma
# repr.tag_start
# repr.tag_name
# repr.tag_contents
# repr.tag_end
# repr.attrib_name
# repr.attrib_equal
# repr.attrib_value
# prompt


rich_style = {
    "markdown.code": colours["beige"],
    "repr.tag_name": colours["beige"],  # for consistency with Python
    "markdown.h1": "bold #B22518",
    "markdown.h2": "bold #009999 underline",  # Exception message; location header
    "markdown.h3": "bold #CF6A4C",  # likely cause
    "markdown.h4": "bold #CF6A4C",  # warning header
    "markdown.link": "bold #DAEFA3 underline",
    "repr.url": "bold #DAEFA3 underline",
    "repr.number": colours["orange"],
    # The next three are identical for pygments, so we keep them identical
    "repr.bool_false": colours["orange"],
    "repr.bool_true": colours["orange"],
    "repr.none": colours["orange"],
    #
    "repr.str": colours["green"],
    "repr.error": colours["red"],
}

my_style = {
    "builtins": colours["yellow"],
    "keywords": colours["blue"],
    "comments": colours["gray"],
    "text": colours["white"],
    "operators": colours["white"],
    "diagnostics": "#FF00FF",  # Magenta
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
        Error: my_style["repr.error"],  # class: 'err'
        Other: my_style["diagnostics"],  # class 'x'
        #
        Comment: my_style["comments"],  # class: 'c'
        Comment.Multiline: my_style["comments"],  # class: 'cm'
        Comment.Preproc: my_style["comments"],  # class: 'cp'
        Comment.Single: my_style["comments"],  # class: 'c1'
        Comment.Special: my_style["comments"],  # class: 'cs'
        #
        Generic: my_style["text"],  # class: 'g'
        Generic.Deleted: my_style["repr.error"],  # class: 'gd'
        Generic.Emph: my_style["text"],  # class: 'ge'
        Generic.Error: my_style["repr.error"],  # class: 'gr'
        Generic.Heading: my_style["text"],  # class: 'gh'
        Generic.Inserted: my_style["text"],  # class: 'gi'
        Generic.Output: my_style["text"],  # class: 'go'
        Generic.Prompt: my_style["keywords"],  # class: 'gp'
        Generic.Strong: my_style["text"],  # class: 'gs'
        Generic.Subheading: my_style["text"],  # class: 'gu'
        Generic.Traceback: my_style["repr.error"],  # class: 'gt'
        #
        Keyword: my_style["keywords"],  # class: 'k' #FADA5E Royal yellow #FFFF66
        Keyword.Constant: my_style["repr.bool_true"],  # class: 'kc'
        Keyword.Declaration: my_style["keywords"],  # class: 'kd'
        Keyword.Namespace: my_style["keywords"],  # class: 'kn'
        Keyword.Pseudo: my_style["keywords"],  # class: 'kp'
        Keyword.Reserved: my_style["keywords"],  # class: 'kr'
        Keyword.Type: my_style["keywords"],  # class: 'kt'
        #
        Literal: my_style["text"],  # class: 'l'
        Literal.Date: my_style["text"],  # class: 'ld'
        #
        Name: my_style["markdown.code"],  # class: 'n'
        Name.Attribute: my_style["markdown.code"],  # class: 'na'
        # The following is for file path in tracebacks and Python builtins.
        Name.Builtin: my_style["builtins"],  # class: 'nb'
        Name.Builtin.Pseudo: my_style["builtins"],  # class: 'bp'
        Name.Class: my_style["markdown.code"],  # class: 'nc'
        Name.Constant: my_style["markdown.code"],  # class: 'no'
        Name.Decorator: my_style["markdown.code"],  # class: 'nd'
        Name.Entity: my_style["markdown.code"],  # class: 'ni'
        Name.Exception: my_style["repr.error"],  # class: 'ne'
        Name.Function: my_style["markdown.code"],  # class: 'nf'
        Name.Property: my_style["markdown.code"],  # class: 'py'
        Name.Label: my_style["markdown.code"],  # class: 'nl'
        Name.Namespace: my_style["markdown.code"],  # class: 'nn'
        Name.Other: my_style["markdown.code"],  # class: 'nx'
        Name.Tag: my_style["markdown.code"],  # class: 'nt' - like a keyword
        Name.Variable: my_style["markdown.code"],  # class: 'nv'
        Name.Variable.Class: my_style["markdown.code"],  # class: 'vc'
        Name.Variable.Global: my_style["markdown.code"],  # class: 'vg'
        Name.Variable.Instance: my_style["markdown.code"],  # class: 'vi'
        #
        Number: my_style["repr.number"],  # class: 'm'
        Number.Float: my_style["repr.number"],  # class: 'mf'
        Number.Hex: my_style["repr.number"],  # class: 'mh'
        Number.Integer: my_style["repr.number"],  # class: 'mi'
        Number.Integer.Long: my_style["repr.number"],  # class: 'il'
        Number.Oct: my_style["repr.number"],  # class: 'mo'
        #
        Operator: my_style["operators"],  # class: 'o'
        Operator.Word: my_style["operators"],  # class: 'ow'
        #
        Punctuation: my_style["operators"],  # class: 'p'
        #
        String: my_style["repr.str"],  # class: 's'
        String.Backtick: my_style["repr.str"],  # class: 'sb'
        String.Char: my_style["repr.str"],  # class: 'sc'
        String.Doc: my_style["repr.str"],  # class: 'sd'
        String.Double: my_style["repr.str"],  # class: 's2'
        String.Escape: my_style["repr.str"],  # class: 'se'
        String.Heredoc: my_style["repr.str"],  # class: 'sh'
        String.Interpol: my_style["repr.str"],  # class: 'si'
        String.Other: my_style["repr.str"],  # class: 'sx'
        String.Regex: my_style["repr.str"],  # class: 'sr'
        String.Single: my_style["repr.str"],  # class: 's1'
        String.Symbol: my_style["repr.str"],  # class: 'ss'
    }
