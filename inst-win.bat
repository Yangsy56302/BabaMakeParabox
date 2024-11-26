pip install -r requirements.txt
set PYINSTALLER=TRUE
pyinstaller --specpath . --distpath . --workpath ./temp/make --onefile --console --icon bmp.ico --name bmp bmp.py
pyinstaller --specpath . --distpath . --workpath ./temp/make --onefile --windowed --icon bmp.ico --name submp submp.py
pause