# import sys

from friendly_traceback.idle import new_run

from idlelib import run

run.main = new_run.main
