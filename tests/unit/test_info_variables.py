import inspect

import friendly_traceback as friendly

global_a = 1
global_b = 2
global_annotated : "this"


def test_get_variables_in_frame_by_scope():
    # We cannot use pytest for this test as it messes with the frames
    # and generates a RuntimeError.

    get = friendly.info_variables.get_variables_in_frame_by_scope
    current_frame = None

    b = 2
    def outer():
        c = 3
        d = 4
        def inner():
            global global_a
            global global_b
            nonlocal current_frame
            nonlocal c
            e = 5
            global_b += 1
            current_frame = inspect.currentframe()
        inner()

    outer()

    # declaring a variable global and changing (or not) its value
    # does not make it a local variable
    assert "global_a" in get(current_frame, "global")
    assert "global_a" not in get(current_frame, "local")
    assert "global_b" not in get(current_frame, "local")

    # nonlocal variable two frames removed is the same as one frame removed
    # b: two frames removed
    assert "b" in get(current_frame, "nonlocal")
    assert "b" not in get(current_frame, "local")
    assert "b" not in get(current_frame, "global")
    # d: one frame removed
    assert "d" in get(current_frame, "nonlocal")
    assert "d" not in get(current_frame, "local")
    assert "d" not in get(current_frame, "global")

    # declaring a variable nonlocal makes it also a local variable
    assert "c" in get(current_frame, "local")
    assert "c" in get(current_frame, "nonlocal")
    assert "c" not in get(current_frame, "global")

    assert "e" in get(current_frame, "local")

if __name__ == '__main__':
    test_get_variables_in_frame_by_scope()
