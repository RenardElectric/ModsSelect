del ModsSelect.exe

pyinstaller ..\src\main.py --noconfirm --onefile --console --name "ModsSelect" --collect-data sv_ttk
move dist\ModsSelect.exe ..\build

del ModsSelect.spec
rmdir /s /q build
rmdir /s /q dist