
call venv-friendly3.6\scripts\activate & python -m pytest --cov=friendly --cov-report html tests

echo Python 3.7:
call venv-friendly3.7\scripts\activate & python -m pytest --cov=friendly --cov-append --cov-report html tests

echo Python 3.8:
call venv-friendly3.8\scripts\activate & python -m pytest --cov=friendly --cov-append --cov-report html tests

echo Python 3.9:
call venv-friendly3.9\scripts\activate & python -m pytest --cov=friendly --cov-append --cov-report html tests

echo Python 3.10:
call venv-friendly3.10\scripts\activate & python -m pytest --cov=friendly --cov-append --cov-report html tests

call venv-friendly3.8\scripts\activate
