import sys


import friendly_traceback

items = (
    "header",
    "message",
    "generic",
    "parsing_error",
    "parsing_error_source",
    "cause_header",
    "cause",
    "last_call_header",
    "last_call_source",
    "last_call_variables",
    "exception_raised_header",
    "exception_raised_source",
    "exception_raised_variables",
)


def make_empty_dict():
    d = {}
    for item in items:
        d[item] = ""
    return d


begin_html = """
<html>
<head>
<style>
h1 {color:red}
h2 {color:blue}
pre {color:yellow; background: black}
body {width:600px; margin:auto}
</style>
</head>
<body>
"""

template = """
<h1>{header}</h1>
<h3>{message}</h3>
<p>{parsing_error}</p>
<p>{parsing_error_source}</p>
<h2>{cause_header}</h2>
<p>{cause}</p>
<h4>{last_call_header}<h4>
<pre>{last_call_source}</pre>
<pre class='var'>{last_call_variables}</pre>
<h4>{exception_raised_header}<h4>
<pre>{exception_raised_source}</pre>
<pre class='var'>{exception_raised_variables}</pre>
"""

end_html = "</body></html>"


def html_formatter(info, level=None):
    items = make_empty_dict()
    for key in info:
        items[key] = info[key]

    return template.format(**items)


friendly_traceback.set_formatter(formatter=html_formatter)

try:
    b = a + c  # noqa
except Exception:
    friendly_traceback.explain(*sys.exc_info(), redirect="capture")

result = begin_html + friendly_traceback.get_output() + end_html

with open("test.html", "w") as f:
    f.write(result)
