import data_3_6
import data_3_7
import data_3_8
import data_3_9
import data_3_10

info_36 = data_3_6.info
info_37 = data_3_7.info
info_38 = data_3_8.info
info_39 = data_3_9.info
info_310 = data_3_10.info

output = open("compare_data.html", "w", encoding="utf8")

output.write("<div>\n")
files = set([])


def print_different(filename, in_36, in_37, in_38, in_39, in_310, topic):
    # Just tracking changes going forward in time, from
    # one version to the next.
    if topic == "message":
        header = "<h5>Different messages - from Python</h5>\n"
    else:
        header = "<h5>Different explanation - by Friendly-traceback</h5>\n"
    header_added = False
    printed_37 = False
    printed_38 = False
    printed_39 = False
    if in_36 != in_37:
        if filename not in files:
            output.write("<div class='filename-header'>\n")
            files.add(filename)
            output.write(filename)
            output.write("</div>\n")
        if not header_added:
            output.write(header)
            header_added = True
        output.write("<pre class='highlight friendly-small-pre'>")
        output.write("<b>3.6: </b>" + in_36 + "\n")
        output.write("<b>3.7: </b>" + in_37 + "\n")
        printed_37 = True
        output.write("</pre>\n")
    if in_37 != in_38:
        if filename not in files:
            output.write("<div class='filename-header'>\n")
            files.add(filename)
            output.write(filename)
            output.write("</div>\n")
        if not header_added:
            output.write(header)
            header_added = True
        output.write("<pre class='highlight friendly-small-pre'>")
        if not printed_37:
            output.write("<b>3.7: </b>" + in_37 + "\n")
        output.write("<b>3.8: </b>" + in_38 + "\n")
        output.write("</pre>\n")
    if in_38 != in_39:
        if filename not in files:
            output.write("<div class='filename-header'>")
            files.add(filename)
            output.write(filename)
            output.write("</div>\n")
        if not header_added:
            output.write(header)
            header_added = True
        output.write("<pre class='highlight friendly-small-pre'>")
        if not printed_38:
            output.write("<b>3.8: </b>" + in_38 + "\n")
        output.write("<b>3.9: </b>" + in_39 + "\n")
        output.write("</pre>\n")
    if in_39 != in_310:
        if filename not in files:
            output.write("<div class='filename-header'>")
            files.add(filename)
            output.write(filename)
            output.write("</div>\n")
        if not header_added:
            output.write(header)
        output.write("<pre class='highlight friendly-small-pre'>")
        if not printed_39:
            output.write("<b>3.9: </b>" + in_39 + "\n")
        output.write("<b>3.10: </b>" + in_310 + "\n")
        output.write("</pre>\n")


all_names = (
    set(info_36.keys())
    | set(info_37.keys())
    | set(info_38.keys())
    | set(info_39.keys())
    | set(info_310.keys())
)


for filename in all_names:
    if filename in info_36:
        data_36 = info_36[filename]
    else:
        data_36 = {
            "message": "Likely not a SyntaxError",
            "cause": "Likely not a SyntaxError",
        }

    if filename in info_37:
        data_37 = info_37[filename]
    else:
        data_37 = {
            "message": "Likely not a SyntaxError",
            "cause": "Likely not a SyntaxError",
        }

    if filename in info_38:
        data_38 = info_38[filename]
    else:
        data_38 = {
            "message": "Likely not a SyntaxError",
            "cause": "Likely not a SyntaxError",
        }

    if filename in info_39:
        data_39 = info_39[filename]
    else:
        data_39 = {
            "message": "Likely not a SyntaxError",
            "cause": "Likely not a SyntaxError",
        }

    if filename in info_310:
        data_310 = info_310[filename]
    else:
        data_310 = {
            "message": "Likely not a SyntaxError",
            "cause": "Likely not a SyntaxError",
        }

    print_different(
        filename,
        data_36["message"],
        data_37["message"],
        data_38["message"],
        data_39["message"],
        data_310["message"],
        "message",
    )
    print_different(
        filename,
        data_36["cause"],
        data_37["cause"],
        data_38["cause"],
        data_39["cause"],
        data_310["cause"],
        "explanation",
    )

output.write("</div>\n")
output.close()
