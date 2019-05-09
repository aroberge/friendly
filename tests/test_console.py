# # pylint: disable=C0103
import subprocess

sessions = [
    (
        "python -im friendly_traceback tests.test_name_error --as_main",
        "a = 41 \na+=1\nprint(a)\nd=e\n",
        ["42", "NameError", "-->7:         b = c"],
        ["-->1: d=e", "NameError"],
    )
]


def test_console():
    """Function discoverable and run by pytest"""
    for command, inp, out, err in sessions:
        process = subprocess.Popen(
            command,
            shell=False,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,  # use strings as input
        )
        # I have found comparisons with stderr problematic, so I ignore it
        # However, since all tests are supposed not to raise exceptions
        # but only valid output, this does not impact the reliability
        # of these tests: if stdout is not as expected, we have a problem.
        stdout, stderr = process.communicate(inp)
        process.wait()
        for item in out:
            assert item in stdout
        for item in err:
            assert item in stderr


if __name__ == "__main__":
    test_console()
