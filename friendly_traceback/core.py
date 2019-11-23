"""core.py

The exception hook at the heart of Friendly-traceback
"""

import traceback

from .session import state

from . import info_traceback


def explain(etype, value, tb, redirect=None):
    """Replaces a standard traceback by a friendlier one,
       except for SystemExit and KeyboardInterrupt which
       are re-raised.

       The values of the required arguments are typically the following:

           etype, value, tb = sys.exc_info()

       By default, the output goes to sys.stderr or to some other stream
       set to be the default by another API call.  However, if
          redirect = some_stream
       is specified, the output goes to that stream, but without changing
       the global settings.
    """
    if redirect is not None:
        saved_current_redirect = state.write_err
        state.set_redirect(redirect=redirect)

    if state.level == 0:
        state.write_err("".join(traceback.format_exception(etype, value, tb)))
        return

    if etype.__name__ == "SystemExit":
        raise SystemExit(str(value))
    if etype.__name__ == "KeyboardInterrupt":
        raise KeyboardInterrupt(str(value))

    state.traceback_info = info_traceback.get_traceback_info(
        etype, value, tb, state.write_err
    )
    explanation = state.formatter(state.traceback_info, level=state.level)
    state.write_err(explanation)
    # Ensures that we start on a new line for the console
    if not explanation.endswith("\n"):
        state.write_err("\n")

    if redirect is not None:
        state.write_err = saved_current_redirect
