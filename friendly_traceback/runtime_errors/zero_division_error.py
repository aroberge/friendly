from .. import debug_helper


def get_cause(value, frame, tb_data):
    try:
        return _get_cause(value, frame, tb_data)
    except Exception:
        debug_helper.log_error()
        return None, None


def _get_cause(value, frame, tb_data):
    return None, None
