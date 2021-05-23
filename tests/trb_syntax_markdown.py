"""Creates a version of syntax_traceback_en.rst to insert in the documentation.
"""

# When creating a new translation, you need to:
# 1. Make a copy of this file
# 2. Change the value of LANG as well as 'intro_text' so that they reflect the
#    appropriate language
# 3. Change the first line of this file so that the name of the rst file
#    is correct!


import os
import sys
import platform
this_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(this_dir, ".."))
import friendly


# Make it possible to find docs and tests source
docs_root_dir = os.path.abspath(
    os.path.join(this_dir, "..", "..", "friendly-traceback-docs")
)
assert os.path.isdir(docs_root_dir), "Separate docs repo need to exist"

friendly.install()
friendly.set_lang("en")
friendly.set_formatter("markdown_docs")

sys.path.insert(0, this_dir)
py_version = f"{sys.version_info.major}.{sys.version_info.minor}"

import trb_syntax_common

target = os.path.normpath(
    os.path.join(
        docs_root_dir, "docs/source/tracebacks_syntax_markdown.md"
    )
)

intro_text = """
# Syntax errors - markdown_docs format

<div class="admonition note">
<p class="admonition-title">Note</p>
<p>The content of this page is generated by running
{name} located in the <code class="docutils literal notranslate"><span class="pre">tests/</span></code> directory.
This needs to be done explicitly, independently of updating the
documentation using Sphinx.
</p>
</div>

Friendly version: {friendly}
Python version: {python}

""".format(
    friendly=friendly._doc_version(),
    python=platform.python_version(),
    name=__file__,
)

print(f"Python version: {platform.python_version()}; --- markdown format")

trb_syntax_common.create_tracebacks(target, intro_text, formatter="markdown_docs")
