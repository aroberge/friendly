cd tests\syntax

call ..\..\venv-friendly3.6\scripts\activate
call python compile_data.py
call deactivate

call ..\..\venv-friendly3.7\scripts\activate
call python compile_data.py
call deactivate

call ..\..\venv-friendly3.8\scripts\activate
call python compile_data.py
call deactivate

call ..\..\venv-friendly3.9\scripts\activate
call python compile_data.py
call deactivate

call ..\..\venv-friendly3.10\scripts\activate
call python compile_data.py
call deactivate

call python compare_data.py
copy compare_data.html ..\..\..\friendly-traceback-docs\docs\source\compare_data.html
del compare_data.html


cd ..

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

call ..\venv-friendly3.10\scripts\activate
call  python trb_english.py
call  python trb_syntax_english.py
call  deactivate

cd ..\..\friendly-traceback-docs\docs
call make html
cd ..\..\friendly-traceback
call venv-friendly3.8\scripts\activate
