"""Friendly-rich

All Rich-related imports and redefinitions are done here.

"""

rich_available = True
try:
    from rich.console import Console, Segment
    from rich.markdown import Markdown, BlockQuote
    from rich.theme import Theme
except ImportError:
    rich_available = False
    Markdown = None
    Console = None


def init_console():
    if not rich_available:
        return None

    def _patch(self, console, options):
        """Formatting hack to be able to have consecutive block quotes
           without lines in between. Used for displaying possible typos
           in a block. A further correction is done in the rich_markdown
           formatter to insert a blank line after the 2 or 3 block quotes
           shown.
        """
        render_options = options.update(width=options.max_width - 4)
        lines = console.render_lines(self.elements, render_options, style=self.style)
        style = self.style
        padding = Segment("       ", style)
        for line in lines:
            yield padding
            yield from line

    BlockQuote.__rich_console__ = _patch

    dark_background_theme = Theme(
        {
            "markdown.h1.border": "bold yellow",
            "markdown.h1": "bold red",
            "markdown.h2": "bold green",
            "markdown.link": "white",
            "markdown.code": "deep_sky_blue1",
            "markdown.h3": "bold red underline",
            "markdown.block_quote": "bold yellow",
        }
    )
    return Console(theme=dark_background_theme)


console = init_console()
