import data_3_6
import data_3_7
import data_3_8

info_36 = data_3_6.info
info_37 = data_3_7.info
info_38 = data_3_8.info

print("<pre>")
files = set([])


def print_different(filename, in_36, in_37, in_38):
    if (in_36 != in_37) and (in_37 != in_38) and (info_36 != info_38):
        if filename not in files:
            print("\n", "=" * 50, sep="")
            files.add(filename)
            print(filename, "\n", "-" * 50, sep="")
        print("\n3.6:\n", in_36, sep="")
        print("\n3.7:\n", in_37, sep="")
        print("\n3.8:\n", in_38, sep="")
    elif in_37 != in_38:
        if filename not in files:
            print("\n", "=" * 50, sep="")
            files.add(filename)
            print(filename, "\n", "-" * 50, sep="")
        print("\n3.7:\n", in_37, sep="")
        print("\n3.8:\n", in_38, sep="")
    elif in_36 != in_37:
        if filename not in files:
            print("\n", "=" * 50, sep="")
            files.add(filename)
            print(filename, "\n", "-" * 50, sep="")
        print("\n3.6:\n", in_36, sep="")
        print("\n3.7:\n", in_37, sep="")
    elif in_36 != in_38:
        if filename not in files:
            print("\n", "=" * 50, sep="")
            files.add(filename)
            print(filename, "\n", "-" * 50, sep="")
        print("\n3.6:\n", in_36, sep="")
        print("\n3.8:\n", in_38, sep="")


for filename in info_36:
    try:
        data_36 = info_36[filename]
        data_37 = info_37[filename]
        data_38 = info_38[filename]
    except KeyError:
        print("=" * 50)
        print("entry does not exist in one data file for ", filename)
        print("=" * 50)
        continue

    print_different(
        filename, data_36["message"], data_37["message"], data_38["message"]
    )
    print_different(
        filename,
        data_36["parsing_error_source"],
        data_37["parsing_error_source"],
        data_38["parsing_error_source"],
    )
    print_different(filename, data_36["cause"], data_37["cause"], data_38["cause"])

print("</pre>")
