@echo off
setlocal EnableDelayedExpansion

:: Get the flash drive root directory
set "FLASH_DRIVE=%~dp0"
set "FLASH_DRIVE=%FLASH_DRIVE:~0,-1%"
set "PYTHON_DIR=%FLASH_DRIVE%\python_embed"
set "PYTHON_EXE=%PYTHON_DIR%\python.exe"
set "GET_PIP_URL=https://bootstrap.pypa.io/get-pip.py"
set "GET_PIP_PATH=%FLASH_DRIVE%\get-pip.py"

:: Check if Python is already installed in python_embed
if exist "%PYTHON_EXE%" (
    echo Python found at %PYTHON_DIR%
    call :run_program
    goto :eof
)

:: Check if system Python is available
where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo System Python found.
    call :run_program
    goto :eof
)

:: Prompt user to install Python
echo Python is not found on this computer or flash drive.
set /p INSTALL="Would you like to install a portable Python on the flash drive? (y/n): "
if /i "!INSTALL!"=="y" (
    echo Downloading Python embeddable package...
    :: Use curl to download the embeddable Python zip (Python 3.10.11 for Windows 64-bit)
    curl -o "%FLASH_DRIVE%\python.zip" https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip
    if %ERRORLEVEL% neq 0 (
        echo Failed to download Python. Please check your internet connection.
        pause
        goto :eof
    )

    echo Extracting Python to %PYTHON_DIR%...
    :: Use PowerShell to unzip (Windows native, no external tools needed)
    powershell -command "Expand-Archive -Path '%FLASH_DRIVE%\python.zip' -DestinationPath '%PYTHON_DIR%' -Force"
    if %ERRORLEVEL% neq 0 (
        echo Failed to extract Python.
        pause
        goto :eof
    )

    :: Clean up zip file
    del "%FLASH_DRIVE%\python.zip"

    :: Enable site module by uncommenting import site in the .pth file
    for %%F in ("%PYTHON_DIR%\python*._pth") do (
        set "PTH_FILE=%%F"
        powershell -command "(Get-Content '!PTH_FILE!') -replace '#import site', 'import site' | Set-Content '!PTH_FILE!'"
    )

    :: Download and install pip
    echo Installing pip...
    curl -o "%GET_PIP_PATH%" "%GET_PIP_URL%"
    if %ERRORLEVEL% neq 0 (
        echo Failed to download get-pip.py.
        pause
        goto :eof
    )
    "%PYTHON_EXE%" "%GET_PIP_PATH%"
    if %ERRORLEVEL% neq 0 (
        echo Failed to install pip.
        pause
        goto :eof
    )
    del "%GET_PIP_PATH%"

    :: Install dependencies from requirements.txt
    echo Installing dependencies...
    "%PYTHON_DIR%\Scripts\pip.exe" install -r "%FLASH_DRIVE%\requirements.txt"
    if %ERRORLEVEL% neq 0 (
        echo Failed to install dependencies.
        pause
        goto :eof
    )

    echo Python installed successfully.
    call :run_program
) else (
    echo Python is required to run this program. Exiting.
    pause
    goto :eof
)

:run_program
:: Run the main Python script
echo Starting Tool Functions...
if exist "%PYTHON_EXE%" (
    "%PYTHON_EXE%" "%FLASH_DRIVE%\main_app.py"
) else (
    python "%FLASH_DRIVE%\main_app.py"
)
if %ERRORLEVEL% neq 0 (
    echo Failed to run the program. Ensure all files are present and Python is installed correctly.
    pause
)
goto :eof