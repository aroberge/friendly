cd tests

call ..\venv-friendly3.8\scripts\activate
call python trb_english.py
call python trb_french.py
call  python trb_syntax_english.py
call  python trb_syntax_french.py
call  python trb_english_markdown.py
call  python trb_syntax_markdown.py
call  deactivate

call ..\venv-friendly3.6\scripts\activate
call  python trb_english.py
call  python trb_syntax_english.py
call  deactivate

call ..\venv-friendly3.7\scripts\activate
call  python trb_english.py
call  python trb_syntax_english.py
call  deactivate

call ..\venv-friendly3.9\scripts\activate
call  python trb_english.py
call  python trb_syntax_english.py
call  deactivate

cd ..\..\friendly-traceback-docs\docs
call make html
cd ..\..\friendly-traceback
call venv-friendly3.8\scripts\activate
