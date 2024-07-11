@echo off
cd ..
set input=
set /p input=Levelpack File Name Without .json: 
BabaMakeParabox.exe -i %input%
pause