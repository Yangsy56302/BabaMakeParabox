pip install -r requirements.txt
set PYINST=TRUE
pyinstaller --specpath . --distpath . --workpath ./temp/make --onefile --console --icon logo/a2icon.ico --name bmp bmp.py
pyinstaller --specpath . --distpath . --workpath ./temp/make --onefile --windowed --icon logo/a2icon.ico --name submp submp.py
pause