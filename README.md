# MyVCE Certificacion

Simulador de examenes de certificacion F5 BIG-IP.

---

## Instalacion Rapida

### Windows

1. Ir a la carpeta `dist\MyVCE_Certificacion\`
2. Doble clic en `MyVCE_Certificacion.bat`

La primera vez, el launcher:
- Creara un entorno virtual de Python
- Instalara Streamlit y dependencias automaticamente
- Iniciara la aplicacion

### Linux / macOS

```bash
cd dist/MyVCE_Certificacion
chmod +x MyVCE_Certificacion.sh
./MyVCE_Certificacion.sh
```

---

## Requisitos

- **Python 3.10 o superior** instalado en el sistema

### Instalar Python

**Linux:**
```bash
sudo apt install python3 python3-pip
```

**Windows:**
1. Descargar de https://www.python.org/downloads/
2. Ejecutar el instalador
3. Marcar "Add Python to PATH"

---

## Despues de Ejecutar

1. Se abrira automaticamente el navegador
2. Si no, ir a la URL que muestre en la terminal
3. La primera vez, configurar la API Key de Google Gemini (opcional)

---

## Configurar API Key (Opcional)

Para usar la funcion de OCR:

1. Ir a: https://makersuite.google.com/app/apikey
2. Crear una API Key de Google Gemini
3. En la app, ingresar la clave cuando lo solicite

---

## Compilar / Preparar Distribucion

### Windows

1. Ejecutar `build\build_windows.bat`
2. Los archivos se generan en `dist\MyVCE_Certificacion\`

### Linux

1. Ejecutar `build\build_linux.sh`
2. Los archivos se generan en `dist/MyVCE_Certificacion/`

---

## Crear Instalador .exe (Windows)

### Paso 1: Instalar Inno Setup

1. Descargar de: https://jrsoftware.org/isdl.php
2. Instalar con opciones predeterminadas

### Paso 2: Generar la distribucion

```batch
build\build_windows.bat
```

### Paso 3: Generar el instalador

```batch
build_installer.bat
```

El instalador se generara en: `installer\MyVCE_Certificacion_Setup_v1.0.exe`

---

## Estructura del Proyecto

```
MyVCE_Funcional/
├── app.py                    # Codigo fuente principal
├── preguntas.json            # Base de preguntas del examen
├── imagenes_preguntas/       # Imagenes de preguntas (116 archivos)
├── requirements.txt         # Dependencias de Python
├── README.md                # Esta documentacion
├── setup.iss               # Script para Inno Setup (generar instalador)
├── build_installer.bat     # Script para generar el instalador .exe
├── src/                    # Modulos auxiliares
│   ├── paths.py            # Gestion de rutas
│   ├── api_key_manager.py  # Almacenamiento seguro de API keys
│   └── __init__.py
├── build/                  # Scripts de compilacion
│   ├── build_windows.bat   # Preparar distribucion Windows
│   ├── build_linux.sh      # Preparar distribucion Linux
│   ├── MyVCE_Certificacion.bat  # Launcher Windows
│   └── MyVCE_Certificacion.sh   # Launcher Linux
├── dist/                   # (Generado por build scripts)
│   └── MyVCE_Certificacion/
│       ├── MyVCE_Certificacion.sh
│       ├── MyVCE_Certificacion.bat
│       ├── venv/               # Entorno virtual con dependencias
│       └── _internal/
│           ├── app.py
│           ├── preguntas.json
│           ├── imagenes_preguntas/
│           └── src/
└── installer/              # (Generado por Inno Setup)
    └── MyVCE_Certificacion_Setup_v1.0.exe
```

---

## Flujo de Trabajo

### Para Desarrollo
1. Modificar `app.py` y demas archivos fuente
2. Probar con: `python -m streamlit run app.py`

### Para Distribucion

**Windows:**
```
build\build_windows.bat    -> prepara dist\
build_installer.bat        -> genera installer\MyVCE_Certificacion_Setup_v1.0.exe
```

**Linux:**
```
build\build_linux.sh       -> prepara dist/
```

---

## Solucion de Problemas

### "Python no encontrado"
- Verificar que Python este instalado
- En Windows, reiniciar despues de instalar Python

### "Puerto en uso"
- Cerrar otras aplicaciones que usen ese puerto
- La app usara automaticamente otro puerto disponible

### La app no inicia
- Ejecutar `build\build_windows.bat` primero
- Verificar que `dist\MyVCE_Certificacion\_internal\app.py` existe

### Primera ejecucion lenta
- Es normal, necesita instalar dependencias
- La segunda ejecucion sera mas rapida
