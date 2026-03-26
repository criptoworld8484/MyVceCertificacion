@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo ================================================
echo   MyVCE Certificacion - Generador de Instalador
echo ================================================
echo.

REM Verificar si Inno Setup esta instalado
set "INNO_SETUP_PATH="

REM Buscar en Program Files
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
    set "INNO_SETUP_PATH=%ProgramFiles%\Inno Setup 6\ISCC.exe"
) else if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
    set "INNO_SETUP_PATH=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
) else if exist "%ProgramFiles%\Inno Setup 5\ISCC.exe" (
    set "INNO_SETUP_PATH=%ProgramFiles%\Inno Setup 5\ISCC.exe"
) else if exist "%ProgramFiles(x86)%\Inno Setup 5\ISCC.exe" (
    set "INNO_SETUP_PATH=%ProgramFiles(x86)%\Inno Setup 5\ISCC.exe"
)

REM Buscar en otras ubicaciones
if "!INNO_SETUP_PATH!"=="" (
    for %%i in (C D E F G H) do (
        if exist "%%i:\Program Files\Inno Setup 6\ISCC.exe" set "INNO_SETUP_PATH=%%i:\Program Files\Inno Setup 6\ISCC.exe"
        if exist "%%i:\Program Files\Inno Setup 5\ISCC.exe" set "INNO_SETUP_PATH=%%i:\Program Files\Inno Setup 5\ISCC.exe"
        if exist "%%i:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "INNO_SETUP_PATH=%%i:\Program Files (x86)\Inno Setup 6\ISCC.exe"
        if exist "%%i:\Program Files (x86)\Inno Setup 5\ISCC.exe" set "INNO_SETUP_PATH=%%i:\Program Files (x86)\Inno Setup 5\ISCC.exe"
    )
)

if "!INNO_SETUP_PATH!"=="" (
    echo [ERROR] Inno Setup no esta instalado.
    echo.
    echo ================================================
    echo   INSTRUCCIONES DE INSTALACION
    echo ================================================
    echo.
    echo 1. DESCARGAR INNO SETUP:
    echo    - Ve a: https://jrsoftware.org/isdl.php
    echo    - Haz clic en "Download"
    echo.
    echo 2. INSTALAR:
    echo    - Ejecuta el archivo descargado
    echo    - Acepta los terminos de licencia
    echo    - Usa la ubicacion predeterminada
    echo    - Completa la instalacion
    echo.
    echo 3. VOLVER A EJECUTAR ESTE SCRIPT:
    echo    - Una vez instalado Inno Setup
    echo    - Ejecuta este script de nuevo
    echo.
    echo DESCARGA DIRECTA:
    echo https://jrsoftware.org/download.php/is.exe
    echo.
    pause
    exit /b 1
)

echo [OK] Inno Setup encontrado: !INNO_SETUP_PATH!
echo.

REM Crear directorio de salida
if not exist "installer" mkdir installer

REM Verificar ejecutable compilado
if not exist "dist\MyVCE_Certificacion" (
    echo [ERROR] No se encontro la distribucion compilada.
    echo.
    echo Primero ejecuta:
    echo   build\build_windows.bat
    echo.
    echo Luego ejecuta este script de nuevo.
    echo.
    pause
    exit /b 1
)

echo [OK] Archivos verificados
echo.
echo Generando instalador...
echo.

REM Obtener directorio del proyecto
set "PROJECT_DIR=%~dp0"
set "PROJECT_DIR=!PROJECT_DIR:~0,-1!"

REM Ejecutar Inno Setup
cd /d "!PROJECT_DIR!"
"!INNO_SETUP_PATH!" setup.iss

if errorlevel 1 (
    echo.
    echo [ERROR] Fallo la generacion del instalador.
    pause
    exit /b 1
)

echo.
echo ================================================
echo   INSTALADOR GENERADO EXITOSAMENTE
echo ================================================
echo.
echo Ubicacion del instalador:
echo   !PROJECT_DIR!\installer\MyVCE_Certificacion_Setup_v1.0.exe
echo.
echo Caracteristicas del instalador:
echo   - Instala la aplicacion en Program Files
echo   - Crea acceso directo en el Menu Inicio
echo   - Crea icono en el escritorio (opcional)
echo   - Incluye desinstalador
echo   - Elimina archivos al desinstalar
echo.
echo Para distribuir:
echo   - Copia el archivo .exe
echo   - Compartelo con otros usuarios
echo   - Funciona en cualquier Windows 10/11
echo.
pause
