import inspect

import friendly_traceback as friendly

global_a = 1
global_annotated : "this"



def no_pytest_get_variables_in_frame_by_scope():
    # We cannot use pytest for this test as it messes with the frames
    # and generates a RuntimeError.

    get = friendly.info_variables.get_variables_in_frame_by_scope
    current_frame = None

    b = 2
    def outer():
        c = 3
        def inner():
            nonlocal current_frame
            d = 4
            current_frame = inspect.currentframe()
        inner()

    outer()

    assert "d" in get(current_frame, "local")
    assert "c" in get(current_frame, "nonlocal")
    assert "b" in get(current_frame, "nonlocal")
    assert "global_a" in get(current_frame, "global")
    print("no_pytest_get_variables_in_frame_by_scope: ok")


if __name__ == '__main__':
    no_pytest_get_variables_in_frame_by_scope()
