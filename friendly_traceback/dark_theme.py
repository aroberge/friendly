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
    This style is strongly inspired by the Twilight schem
    """

    background_color = "#101010"
    default_style = "#363636"

    styles = {
        # No corresponding class for the following:
        Text: "#f8f8f8",  # class:  ''
        Whitespace: "",  # class: 'w'
        Error: "#B22518",  # class: 'err'
        Other: "#f8f8f8",  # class 'x'
        Comment: "italic #5F5A60",  # class: 'c'
        Comment.Multiline: "italic #5F5A60",  # class: 'cm'
        Comment.Preproc: "italic #5F5A60",  # class: 'cp'
        Comment.Single: "italic #5F5A60",  # class: 'c1'
        Comment.Special: "italic #5F5A60",  # class: 'cs'
        Keyword: "bold #F9EE98",  # class: 'k'
        Keyword.Constant: "bold #F9EE98",  # class: 'kc'
        Keyword.Declaration: "bold #F9EE98",  # class: 'kd'
        Keyword.Namespace: "bold #F9EE98",  # class: 'kn'
        Keyword.Pseudo: "bold #F9EE98",  # class: 'kp'
        Keyword.Reserved: "bold #F9EE98",  # class: 'kr'
        Keyword.Type: "bold #F9EE98",  # class: 'kt'
        Operator: "bold #DAEFA3",  # class: 'o'
        Operator.Word: "bold #F9EE98",  # class: 'ow' - like keywords
        Punctuation: "bold #DAEFA3",  # class: 'p'
        # because special names such as Name.Class, Name.Function, etc.
        # are not recognized as such later in the parsing, we choose them
        # to look the same as ordinary variables.
        Name: "#CDA869",  # class: 'n'
        Name.Attribute: "#CDA869",  # class: 'na' - to be revised
        Name.Builtin: "#F9EE98",  # class: 'nb'
        Name.Builtin.Pseudo: "#CDA869",  # class: 'bp'
        Name.Class: "#CDA869",  # class: 'nc' - to be revised
        Name.Constant: "#CDA869",  # class: 'no' - to be revised
        Name.Decorator: "bold #CDA869",  # class: 'nd' - to be revised
        Name.Entity: "#CDA869",  # class: 'ni'
        Name.Exception: "bold #CDA869",  # class: 'ne'
        Name.Function: "#CDA869",  # class: 'nf'
        Name.Property: "#CDA869",  # class: 'py'
        Name.Label: "#CDA869",  # class: 'nl'
        Name.Namespace: "#CDA869",  # class: 'nn' - to be revised
        Name.Other: "#CDA869",  # class: 'nx'
        Name.Tag: "bold #F9EE98",  # class: 'nt' - like a keyword
        Name.Variable: "#CDA869",  # class: 'nv' - to be revised
        Name.Variable.Class: "#CDA869",  # class: 'vc' - to be revised
        Name.Variable.Global: "#CDA869",  # class: 'vg' - to be revised
        Name.Variable.Instance: "#CDA869",  # class: 'vi' - to be revised
        # since the tango light blue does not show up well in text, we choose
        # a pure blue instead.
        Number: "bold #CF6A4C",  # class: 'm'
        Number.Float: "bold #CF6A4C",  # class: 'mf'
        Number.Hex: "bold #CF6A4C",  # class: 'mh'
        Number.Integer: "bold #CF6A4C",  # class: 'mi'
        Number.Integer.Long: "bold #CF6A4C",  # class: 'il'
        Number.Oct: "bold #CF6A4C",  # class: 'mo'
        Literal: "#f8f8f8",  # class: 'l'
        Literal.Date: "#f8f8f8",  # class: 'ld'
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
        Generic.Traceback: "#B22518",  # class: 'gt'
    }
