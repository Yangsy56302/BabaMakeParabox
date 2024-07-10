@echo off
cd ..
set input=
set /p input=World File Name Without .json: 
python BabaMakeParabox.py -i %input%
pause