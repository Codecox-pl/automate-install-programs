import subprocess
import os
import winreg
from typing import List, Optional
from domain.entities import Program
from domain.interfaces import IProgramInstaller

class WindowsProgramInstaller(IProgramInstaller):
    def __init__(self):
        self._installed_apps_cache: Optional[List[str]] = None

    def _get_installed_apps(self) -> List[str]:
        """Obtiene la lista de nombres de programas instalados en el Registro de Windows."""
        if self._installed_apps_cache is not None:
            return self._installed_apps_cache

        apps = set()
        roots = [
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
        ]
        for root, subkey in roots:
            try:
                with winreg.OpenKey(root, subkey) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as sub:
                                try:
                                    name, _ = winreg.QueryValueEx(sub, "DisplayName")
                                    if name and isinstance(name, str):
                                        apps.add(name)
                                except OSError:
                                    pass
                        except OSError:
                            pass
            except OSError:
                pass

        self._installed_apps_cache = list(apps)
        return self._installed_apps_cache

    def is_installed(self, program: Program) -> bool:
        """Determina si un programa ya está instalado validando rutas de archivos o el registro."""
        # 1. Comprobar rutas conocidas en el sistema de archivos
        for path in program.check_paths:
            if path:
                expanded = os.path.expandvars(path)
                if os.path.exists(expanded):
                    return True

        # 2. Comprobar por nombres/patrones en el Registro de Windows
        if program.check_names:
            installed = self._get_installed_apps()
            for pattern in program.check_names:
                pattern_lower = pattern.lower()
                for app_name in installed:
                    if pattern_lower in app_name.lower():
                        return True

        return False

    def install(self, program: Program) -> bool:
        # Manejo especial para Adobe Reader si no está en la ruta indicada
        if "adobe" in program.name.lower() and not os.path.exists(program.installer_path):
            downloads_dir = os.path.join(os.environ.get("USERPROFILE", ""), "Downloads")
            candidate = None
            if os.path.exists(downloads_dir):
                for f in os.listdir(downloads_dir):
                    if (f.lower().startswith("readerdc") or "reader" in f.lower()) and f.lower().endswith(".exe"):
                        candidate = os.path.join(downloads_dir, f)
                        break
            if candidate and os.path.exists(candidate):
                print(f"  -> [INFO] Instalador de Adobe Reader detectado en Descargas: {candidate}")
                program.installer_path = candidate
            else:
                print("  -> [AVISO] No se encontró el instalador de Adobe Reader en el USB ni en Descargas.")
                try:
                    opc = input("     ¿Deseas abrir la web oficial de Adobe Reader para descargarlo ahora? ([S]í / [N]o) [S]: ").strip().lower()
                except Exception:
                    opc = 'n'
                if opc in ('', 's', 'si', 'y', 'yes'):
                    import webbrowser
                    webbrowser.open("https://get.adobe.com/es/reader/")
                    print("     [INFO] Se ha abierto https://get.adobe.com/es/reader/ en el navegador.")
                    print("     IMPORTANTE: Desmarca la casilla 'Adobe Express' antes de descargar.")
                    try:
                        input("     Cuando finalice la descarga en tu carpeta 'Descargas', presiona Enter para continuar...")
                    except Exception:
                        pass
                    # Re-buscar en descargas
                    if os.path.exists(downloads_dir):
                        for f in os.listdir(downloads_dir):
                            if (f.lower().startswith("readerdc") or "reader" in f.lower()) and f.lower().endswith(".exe"):
                                candidate = os.path.join(downloads_dir, f)
                                break
                    if candidate and os.path.exists(candidate):
                        program.installer_path = candidate

        # Validar que el archivo exista en el medio de instalación
        if not os.path.exists(program.installer_path):
            print(f"  -> [ERROR] No se encontró el archivo en: {program.installer_path}")
            return False
        
        try:
            # Formatear el comando dependiendo si es MSI o EXE
            args = (program.silent_args or "").strip()
            if program.is_msi:
                # msiexec requiere /i para instalar
                if args:
                    command = f'msiexec.exe /i "{program.installer_path}" {args}'
                else:
                    command = f'msiexec.exe /i "{program.installer_path}"'
            else:
                if args:
                    command = f'"{program.installer_path}" {args}'
                else:
                    command = f'"{program.installer_path}"'

            if program.is_interactive:
                print(f"  -> [INTERACTIVO] Se ha iniciado el instalador de '{program.name}'.")
                print("     Por favor completa el asistente en pantalla ('Siguiente' / 'Instalar')...")
                # En modo interactivo no capturamos salida para permitir visualización e interacción directa
                result = subprocess.run(command, shell=True)
            else:
                # En modo silencioso capturamos la salida para mantener limpia la consola
                result = subprocess.run(command, shell=True, capture_output=True, text=True, errors="replace")

            # Validar el código de salida (0 = éxito, 3010 = éxito requiriendo reinicio)
            if result.returncode in (0, 3010):
                # Invalidar cache para que reconozca el nuevo programa si se consulta
                self._installed_apps_cache = None
                return True
            else:
                if not program.is_interactive:
                    error_msg = result.stderr.strip() or result.stdout.strip()
                    if error_msg:
                        print(f"  -> [Error Interno] Código {result.returncode}: {error_msg}")
                    else:
                        print(f"  -> [Error Interno] Código de salida: {result.returncode}")
                else:
                    print(f"  -> [Error Interno] El asistente finalizó con código: {result.returncode}")
                return False
        
        except Exception as e:
            print(f"  -> [EXCEPCIÓN] Fallo crítico al ejecutar {program.name}: {e}")
            return False