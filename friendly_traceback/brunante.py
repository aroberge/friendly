"""Theme inspired from the Twilight coding scheme.

Currently, pygments does not include a "twilight" theme but this
could happen at any time. To avoid a potential conflict, I chose a different name.

Twilight can be translated in French as either crépuscule or as brunante,
with the former being the most often-used term. However, I chose the second
since the word 'brunante' starts with 'brun' which is French for 'brown',
and many colours in Twilight are essentially different shades of brown.
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


class BrunanteStyle(Style):
    """
    This style is strongly inspired by the Twilight scheme
    """

    background_color = "#101010"
    default_style = "#363636"

    styles = {
        Text: "#f8f8f8",  # class:  ''
        Whitespace: "",  # class: 'w'
        Error: "#B22518",  # class: 'err'
        Other: "#f8f8f8",  # class 'x'
        #
        Comment: "italic #5F5A60",  # class: 'c'
        Comment.Multiline: "italic #5F5A60",  # class: 'cm'
        Comment.Preproc: "italic #5F5A60",  # class: 'cp'
        Comment.Single: "italic #5F5A60",  # class: 'c1'
        Comment.Special: "italic #5F5A60",  # class: 'cs'
        #
        Generic: "#f8f8f8",  # class: 'g'
        Generic.Deleted: "#B22518",  # class: 'gd'
        Generic.Emph: "italic #f8f8f8",  # class: 'ge'
        Generic.Error: "#ef2929",  # class: 'gr'
        Generic.Heading: "bold #000080",  # class: 'gh'
        Generic.Inserted: "#00A000",  # class: 'gi'
        Generic.Output: "italic #f8f8f8",  # class: 'go'
        Generic.Prompt: "#8f5902",  # class: 'gp'
        Generic.Strong: "bold #f8f8f8",  # class: 'gs'
        Generic.Subheading: "bold #800080",  # class: 'gu'
        Generic.Traceback: "#ef2929",  # class: 'gt'
        #
        Keyword: "bold #F9EE98",  # class: 'k'
        Keyword.Constant: "bold #F9EE98",  # class: 'kc'
        Keyword.Declaration: "bold #F9EE98",  # class: 'kd'
        Keyword.Namespace: "bold #F9EE98",  # class: 'kn'
        Keyword.Pseudo: "bold #F9EE98",  # class: 'kp'
        Keyword.Reserved: "bold #F9EE98",  # class: 'kr'
        Keyword.Type: "bold #F9EE98",  # class: 'kt'
        #
        Literal: "#f8f8f8",  # class: 'l'
        Literal.Date: "#f8f8f8",  # class: 'ld'
        #
        Name: "#CDA869",  # class: 'n'
        Name.Attribute: "#CDA869",  # class: 'na'
        Name.Builtin: "#F9EE98",  # class: 'nb'
        Name.Builtin.Pseudo: "#CDA869",  # class: 'bp'
        Name.Class: "#CDA869",  # class: 'nc'
        Name.Constant: "#CDA869",  # class: 'no'
        Name.Decorator: "bold #CDA869",  # class: 'nd'
        Name.Entity: "#CDA869",  # class: 'ni'
        Name.Exception: "#ef2929",  # class: 'ne'
        Name.Function: "#CDA869",  # class: 'nf'
        Name.Property: "#CDA869",  # class: 'py'
        Name.Label: "#CDA869",  # class: 'nl'
        Name.Namespace: "#CDA869",  # class: 'nn'
        Name.Other: "#CDA869",  # class: 'nx'
        Name.Tag: "bold #F9EE98",  # class: 'nt' - like a keyword
        Name.Variable: "#CDA869",  # class: 'nv'
        Name.Variable.Class: "#CDA869",  # class: 'vc'
        Name.Variable.Global: "#CDA869",  # class: 'vg'
        Name.Variable.Instance: "#CDA869",  # class: 'vi'
        Number: "bold #CF6A4C",  # class: 'm'
        Number.Float: "bold #CF6A4C",  # class: 'mf'
        Number.Hex: "bold #CF6A4C",  # class: 'mh'
        Number.Integer: "bold #CF6A4C",  # class: 'mi'
        Number.Integer.Long: "bold #CF6A4C",  # class: 'il'
        Number.Oct: "bold #CF6A4C",  # class: 'mo'
        #
        Operator: "bold #DAEFA3",  # class: 'o'
        Operator.Word: "bold #F9EE98",  # class: 'ow' - like keywords
        #
        Punctuation: "bold #DAEFA3",  # class: 'p'
        #
        String: "#8F9D6A",  # class: 's'
        String.Backtick: "#8F9D6A",  # class: 'sb'
        String.Char: "#8F9D6A",  # class: 'sc'
        String.Doc: "italic #5F5A60",  # class: 'sd' - like a comment
        String.Double: "#8F9D6A",  # class: 's2'
        String.Escape: "#8F9D6A",  # class: 'se'
        String.Heredoc: "#8F9D6A",  # class: 'sh'
        String.Interpol: "#8F9D6A",  # class: 'si'
        String.Other: "#8F9D6A",  # class: 'sx'
        String.Regex: "#8F9D6A",  # class: 'sr'
        String.Single: "#8F9D6A",  # class: 's1'
        String.Symbol: "#8F9D6A",  # class: 'ss'
    }
