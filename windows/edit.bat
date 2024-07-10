@echo off
cd ..
set input=
set /p input=World File Name For Input Without .json: 
set output=
set /p output=World File Name For Output Without .json: 
BabaMakeParabox.exe -e -i %input% -o %output%
pause