set PYINSTALLER=TRUE
pyinstaller --specpath . --distpath . --workpath ./temp/make --onefile --console --icon BabaMakeParabox.ico --name BabaMakeParabox BabaMakeParabox.py
pyinstaller --specpath . --distpath . --workpath ./temp/make --onefile --windowed --icon BabaMakeParabox.ico --name SubabaMakeParabox SubabaMakeParabox.py
pause