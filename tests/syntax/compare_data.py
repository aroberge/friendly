import data_3_6
import data_3_7
import data_3_8
import data_3_9

info_36 = data_3_6.info
info_37 = data_3_7.info
info_38 = data_3_8.info
info_39 = data_3_9.info

output = open("compare_data.html", "w", encoding="utf8")

output.write("<div>\n")
files = set([])


def print_different(filename, in_36, in_37, in_38, in_39, topic):
    # Just tracking changes going forward in time, from
    # one version to the next.
    if topic == "message":
        header = "<h5>Different messages</h5>\n"
    else:
        header = "<h5>Different explanation</h5>\n"
    header_added = False
    printed_37 = False
    printed_38 = False
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


for filename in info_36:
    try:
        data_36 = info_36[filename]
        data_37 = info_37[filename]
        data_38 = info_38[filename]
        data_39 = info_39[filename]
    except KeyError:
        output.write("<div class='filename-header'>")
        output.write("entry does not exist in one data file for " + filename)
        output.write("</div>\n")
        continue

    print_different(
        filename,
        data_36["message"],
        data_37["message"],
        data_38["message"],
        data_39["message"],
        "message",
    )
    # Leave the following data out for now as it does not give us anything
    # useful ... so far.
    # print_different(
    #     filename,
    #     data_36["parsing_error_source"],
    #     data_37["parsing_error_source"],
    #     data_38["parsing_error_source"],
    # )
    print_different(
        filename,
        data_36["cause"],
        data_37["cause"],
        data_38["cause"],
        data_39["cause"],
        "explanation",
    )

output.write("</div>\n")
output.close()
