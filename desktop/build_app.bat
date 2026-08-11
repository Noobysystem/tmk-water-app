@echo off
chcp 65001 > nul
echo Сборка Windows-приложения ТМК Водоподготовка...

pip install pyinstaller
pyinstaller --noconfirm --onedir --windowed --name "TMK_Water_App" gui_app.py

echo.
echo Сборка завершена! Исполняемый файл находится в директории: desktop\dist\TMK_Water_App\
pause