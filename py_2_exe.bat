set PYINSTALLER=TRUE
pyinstaller --specpath . --distpath . --workpath ./temp/make --onefile --console --icon BabaMakeParabox.ico --name BabaMakeParabox BabaMakeParabox.py
pause