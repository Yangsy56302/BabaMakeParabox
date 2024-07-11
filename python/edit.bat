@echo off
cd ..
set input=
set /p input=Levelpack File Name For Input Without .json: 
set output=
set /p output=Levelpack File Name For Output Without .json: 
python BabaMakeParabox.py -e -i %input% -o %output%
pause