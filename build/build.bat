del ModsSelect.exe

pyinstaller ..\src\main.py --noconfirm --onefile --windowed --name "ModsSelect" --collect-data sv_ttk
move dist\ModsSelect.exe ..\build

del ModsSelect.spec
rmdir build
rmdir dist