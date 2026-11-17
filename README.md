# Automate Install Programs (ATM)

Herramienta de despliegue y configuración automatizada para estaciones de trabajo Windows. Diseñada bajo principios de **Arquitectura Limpia (Clean Architecture)** e **idempotencia**, permitiendo ejecutar instalaciones desatendidas e interactivas, configuración de directivas locales de grupo (GPO), permisos de carpetas y selección dinámica de paquetes.

---

## 🚀 Características Principales

1. **Gestión Nativa de Directivas de Grupo (GPO):**
   * Modifica y sincroniza directamente el archivo binario maestro `C:\Windows\System32\GroupPolicy\Machine\Registry.pol` y `gpt.ini`.
   * Hace que las directivas figuren como **"Habilitada"** en `gpedit.msc` y sean persistentes ante reinicios y comandos `gpupdate /force`.
   * Incluye configuraciones de Windows Update (WSUS), apagado seguro, controladores y directivas de red.

2. **Idempotencia y Checklist Inteligente:**
   * Valida en el Registro de Desinstaladores de Windows (`winreg`) y en el sistema de archivos si cada programa o configuración ya existe antes de ejecutarlo.
   * Si ya está presente, se omite de forma instantánea.

3. **Flujo de Reintentos:**
   * Si un instalador devuelve un error o falla, no aborta el proceso completo. Ofrece un menú interactivo para **[R]eintentar**, **[O]mitir** o **[C]ancelar**.

4. **Instaladores Silenciosos e Interactivos:**
   * **Silenciosos:** 7-Zip, Google Chrome, Citrix Workspace, VLC Media Player, etc.
   * **Interactivos:** Autodesk DWG TrueView 2025, Synology Active Backup, USB Drive Letter Manager.

5. **Selector Dinámico de Microsoft Office:**
   * Menú interactivo para elegir entre **Office Standard 2024** (`ODT_STD_2024`) u **Office Standard 2021** (`ODT_STD_2021`).
   * Copia automática del paquete seleccionado a la raíz `C:\` y ejecución desatendida mediante el Office Deployment Tool (`setup.exe /configure`).

6. **Integración con Adobe Acrobat Reader:**
   * Detección automática en la carpeta `Descargas` o en la memoria USB (`Software_Base`).
   * Enlace asistido a la página oficial para descarga limpia (sin bloatware como Adobe Express).

7. **Configuración de Permisos en Carpetas Temporales:**
   * Asignación estricta de permisos de **Control Total** (`(OI)(CI)F`) al grupo local `Usuarios` (`hostname\Usuarios`) para `C:\TEMP` y `C:\Windows\TEMP`.

---

## 📁 Estructura del Proyecto

```text
atm/
├── application/             # Casos de uso y orquestación del flujo
│   ├── __init__.py
│   └── use_cases.py         # SystemDeploymentUseCase y manejo de Office
├── config/                  # Definición de políticas y lista de programas
│   ├── __init__.py
│   ├── policies.py          # Directivas GPO y scripts del sistema
│   └── programs.py          # Software base a desplegar
├── domain/                  # Entidades e interfaces del dominio
│   ├── __init__.py
│   ├── entities.py          # Modelos Program y Configuration
│   └── interfaces.py        # Contratos IProgramInstaller e ISystemConfigurator
├── infraestructure/         # Implementaciones concretas de Windows
│   ├── __init__.py
│   ├── group_policy_manager.py # Motor binario PReg para Registry.pol
│   ├── windows_config.py    # Configuración de Windows y DISM
│   └── windows_installer.py # Ejecución e inspección de instaladores
├── main.py                  # Punto de entrada principal con detección de privilegios
├── main.spec                # Especificación para empaquetado con PyInstaller
├── requirements.txt         # Dependencias del proyecto
└── README.md
```

---

## 🛠️ Requisitos e Instalación

* **Sistema Operativo:** Windows 10 / Windows 11 / Windows Server (64 bits).
* **Python:** 3.10 o superior (para ejecución en desarrollo).
* **Privilegios:** Requiere ejecución como **Administrador** para aplicar directivas y permisos.

### Instalación de dependencias:
```bash
pip install -r requirements.txt
```

### Ejecución directa con Python:
```bash
python main.py
```

### Compilar a binario `.exe` (PyInstaller):
```bash
pyinstaller main.spec
```
El ejecutable final se genera en la carpeta `dist/main.exe`.
