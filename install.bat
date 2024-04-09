pyinstaller %1 --windowed --onefile
@if %errorlevel% neq 0 (
    exit /b %errorlevel%
)

copy dist\%~n1.exe %SystemRoot%\System32\%~n1%.scr
@if %errorlevel% neq 0 (
    exit /b %errorlevel%
)

@echo.
@echo ===== Screen savers currently in %SystemRoot%\System32:
@dir %SystemRoot%\System32\*.scr
@echo.
