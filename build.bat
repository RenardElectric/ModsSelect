
cd D:/Antony/PycharmProjects/ModsSelect

rmdir /s /q dist
del ModsSelect_run.exe

pyinstaller src/main.py --noconfirm --onefile --console --name "ModsSelect_run" --collect-data sv_ttk

del ModsSelect.spec
rmdir /s /q build

move "D:\Antony\PycharmProjects\ModsSelect\dist\ModsSelect.exe" "D:\Antony\PycharmProjects\ModsSelect"
rmdir /s /q dist