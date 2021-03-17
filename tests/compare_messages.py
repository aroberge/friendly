"""Compare messages for exceptions other than SyntaxError"""
import messages_3_6
import messages_3_7
import messages_3_8
import messages_3_9
import messages_3_10

info_36 = messages_3_6.messages
info_37 = messages_3_7.messages
info_38 = messages_3_8.messages
info_39 = messages_3_9.messages
info_310 = messages_3_10.messages

output = open("compare_messages.html", "w", encoding="utf8")

output.write("<div>\n")
files = set()


def print_different(fn_name, in_36, in_37, in_38, in_39, in_310):
    # Just tracking changes going forward in time, from
    # one version to the next.
    printed_37 = False
    printed_38 = False
    if in_36 != in_37:
        if fn_name not in files:
            output.write("<div class='filename-header'>\n")
            files.add(fn_name)
            output.write(fn_name)
            output.write("</div>\n")
        output.write("<pre class='highlight friendly-small-pre'>")
        output.write("<b>3.6: </b>" + in_36 + "\n")
        output.write("<b>3.7: </b>" + in_37 + "\n")
        printed_37 = True
        output.write("</pre>\n")
    if in_37 != in_38:
        if fn_name not in files:
            output.write("<div class='filename-header'>\n")
            files.add(fn_name)
            output.write(fn_name)
            output.write("</div>\n")
        output.write("<pre class='highlight friendly-small-pre'>")
        if not printed_37:
            output.write("<b>3.7: </b>" + in_37 + "\n")
        output.write("<b>3.8: </b>" + in_38 + "\n")
        output.write("</pre>\n")
    if in_38 != in_39:
        if fn_name not in files:
            output.write("<div class='filename-header'>")
            files.add(fn_name)
            output.write(fn_name)
            output.write("</div>\n")
        output.write("<pre class='highlight friendly-small-pre'>")
        if not printed_38:
            output.write("<b>3.8: </b>" + in_38 + "\n")
        output.write("<b>3.9: </b>" + in_39 + "\n")
        output.write("</pre>\n")
    if in_39 != in_310:
        if fn_name not in files:
            output.write("<div class='filename-header'>")
            files.add(fn_name)
            output.write(fn_name)
            output.write("</div>\n")
        output.write("<pre class='highlight friendly-small-pre'>")
        if not printed_38:
            output.write("<b>3.9: </b>" + in_39 + "\n")
        output.write("<b>3.10: </b>" + in_310 + "\n")
        output.write("</pre>\n")


for f_name in info_36:
    try:
        messages_36 = info_36[f_name].replace("<", "&lt;").replace(">", "&gt;")
        messages_37 = info_37[f_name].replace("<", "&lt;").replace(">", "&gt;")
        messages_38 = info_38[f_name].replace("<", "&lt;").replace(">", "&gt;")
        messages_39 = info_39[f_name].replace("<", "&lt;").replace(">", "&gt;")
        messages_310 = info_310[f_name].replace("<", "&lt;").replace(">", "&gt;")
    except KeyError:
        output.write("<div class='filename-header'>")
        output.write("entry does not exist in one data file for " + f_name)
        output.write("</div>\n")
        continue

    print_different(
        f_name, messages_36, messages_37, messages_38, messages_39, messages_310
    )

output.write("</div>\n")
output.close()
