cd tests
py -3.7 trb_english.py
py -3.7 trb_french.py
py -3.7 trb_syntax_english.py
py -3.7 trb_syntax_french.py
py -3.6 trb_english.py
py -3.6 trb_syntax_english.py
py -3.8 trb_english.py
py -3.8 trb_syntax_english.py
cd ..\..\friendly-traceback-docs\docs
call make html
cd ..\..\friendly-traceback
