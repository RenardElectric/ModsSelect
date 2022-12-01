#dependencies: sv_ttk,ntkutils,darkdetect,requests,keyboard,Pillow

del ModsSelect.exe

pyinstaller src/main.py --noconfirm --onefile --console --name "ModsSelect" --collect-data sv_ttk
move "D:\Antony\PycharmProjects\ModsSelect\dist\ModsSelect.exe" "D:\Antony\PycharmProjects\ModsSelect"

del ModsSelect.spec
rmdir /s /q build
rmdir /s /q dist