@echo off
cd ..
set input=
set /p input=Levelpack File Name Without .json: 
python BabaMakeParabox.py -i %input%
pause