@echo off
cd ..
set input=
set /p input=World File Name Without .json: 
BabaMakeParabox.exe -i %input%
pause