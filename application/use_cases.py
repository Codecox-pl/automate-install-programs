import os
import shutil
import subprocess
from typing import List
from domain.entities import Program, Configuration
from domain.interfaces import IProgramInstaller, ISystemConfigurator


class SystemDeploymentUseCase:
    """Orquesta la instalación de programas y la aplicación de configuraciones"""
    def __init__(self, installer: IProgramInstaller, configurator: ISystemConfigurator):
        self.installer = installer
        self.configurator = configurator

    def execute(self, programs: List[Program], configurations: List[Configuration], base_path: str = "") -> bool:
        """Ejecuta todo el flujo de despliegue automatizado con validación previa de instalaciones y reintentos."""

        print("\n--- INICIANDO DESPLIEGUE DE CONFIGURACIONES ---")
        applied_configs_count = 0
        for config in configurations:
            # Si es directiva de refresco (gpupdate)
            if getattr(config, 'is_refresh', False):
                if applied_configs_count > 0:
                    print(f"\nEjecutando acción de actualización: {config.name}...")
                    self.configurator.apply(config)
                else:
                    print(f"[OMITIDO] {config.name} (no hubieron cambios nuevos en directivas).")
                continue

            # Verificar si ya está aplicada en el sistema
            if self.configurator.is_applied(config):
                print(f"[OMITIDO] '{config.name}' ya está aplicada en el sistema.")
                continue

            print(f"Aplicando configuración: {config.name}...")
            success = self.configurator.apply(config)
            if success:
                print(f"[Ok] {config.name} aplicada correctamente")
                applied_configs_count += 1
            else:
                print(f"[ERROR] Falló al aplicar {config.name}")

        installed_programs = []
        already_installed_programs = []
        skipped_programs = []

        # Despliegue interactivo de Microsoft Office (2024 vs 2021)
        if base_path:
            self._handle_office_deployment(base_path, installed_programs, already_installed_programs, skipped_programs)

        print("\n--- INICIANDO INSTALACIÓN DE PROGRAMAS ---")
        for program in programs:
            # 1. Comprobar si el programa ya se encuentra instalado
            if self.installer.is_installed(program):
                print(f"\n[OMITIDO] '{program.name}' ya se encuentra instalado en el equipo.")
                already_installed_programs.append(program.name)
                continue

            # 2. Si no está instalado, proceder con la instalación y ciclo de reintentos
            while True:
                print(f"\nInstalando: {program.name}")
                success = self.installer.install(program)
                if success:
                    print(f"[Ok] {program.name} se ha instalado correctamente.")
                    installed_programs.append(program.name)
                    break
                else:
                    print(f"\n[ERROR] No se pudo instalar '{program.name}'.")
                    print("  Puedes revisar el problema en el equipo, subsanarlo y luego reintentar.")
                    try:
                        opcion = input(f"  ¿Deseas reintentar la instalación de '{program.name}'? ([R]eintentar / [O]mitir / [C]ancelar todo) [R]: ").strip().lower()
                    except (EOFError, KeyboardInterrupt):
                        opcion = 'c'

                    if opcion in ('', 'r', 'reintentar'):
                        print(f"  -> Reintentando instalación de '{program.name}'...")
                        continue
                    elif opcion in ('c', 'cancelar'):
                        print("\n[INFO] Despliegue cancelado por el usuario.")
                        skipped_programs.append(f"{program.name} (Cancelado)")
                        self._print_summary(installed_programs, already_installed_programs, skipped_programs)
                        return False
                    else:
                        print(f"  -> Omitiendo '{program.name}' y continuando con el siguiente programa...")
                        skipped_programs.append(program.name)
                        break

        self._print_summary(installed_programs, already_installed_programs, skipped_programs)
        return True

    def _is_office_installed(self) -> bool:
        """Verifica si alguna versión de Microsoft Office ya se encuentra instalada."""
        office_paths = [
            r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
            r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE",
            r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
            r"C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE"
        ]
        return any(os.path.exists(p) for p in office_paths)

    def _handle_office_deployment(self, base_path: str, installed_programs: List[str], already_installed: List[str], skipped_programs: List[str]):
        """Permite elegir entre Office 2024 y Office 2021, copia la carpeta a C:\\ y ejecuta Setup /configure."""
        print("\n==========================================================")
        print("              SELECCIÓN DE MICROSOFT OFFICE               ")
        print("==========================================================")

        if self._is_office_installed():
            print("[AVISO] Se detectó que Microsoft Office ya se encuentra instalado en este equipo.")
            already_installed.append("Microsoft Office")
            try:
                opc = input("¿Deseas instalar o configurar otra versión de Office de todas formas? ([S]í / [N]o) [N]: ").strip().lower()
            except Exception:
                opc = 'n'
            if opc not in ('s', 'si', 'y', 'yes'):
                print("-> Manteniendo la instalación existente de Office.")
                return

        print("Selecciona la versión de Office que deseas instalar:")
        print("  [1] Microsoft Office Standard 2024 (ODT_STD_2024)")
        print("  [2] Microsoft Office Standard 2021 (ODT_STD_2021)")
        print("  [3] Omitir instalación de Office")

        folder_name = ""
        xml_name = ""
        display_name = ""

        while True:
            try:
                choice = input("\nElige una opción (1, 2 o 3) [1]: ").strip()
            except Exception:
                choice = '3'

            if choice == '' or choice == '1':
                folder_name = "ODT_STD_2024"
                xml_name = "OFFICE2024.xml"
                display_name = "Microsoft Office Standard 2024"
                break
            elif choice == '2':
                folder_name = "ODT_STD_2021"
                xml_name = "office2021.xml"
                display_name = "Microsoft Office Standard 2021"
                break
            elif choice == '3':
                print("[OMITIDO] Se omitió la instalación de Microsoft Office.")
                skipped_programs.append("Microsoft Office (Omitido por el usuario)")
                return
            else:
                print("Opción inválida. Por favor ingresa 1, 2 o 3.")

        src_folder = os.path.join(base_path, "Software_Base", folder_name)
        dest_folder = os.path.join(r"C:\\", folder_name)

        if not os.path.exists(src_folder):
            # Alternativa: verificar si la carpeta está directamente en la raíz del USB
            alt_src = os.path.join(base_path, folder_name)
            if os.path.exists(alt_src):
                src_folder = alt_src
            else:
                print(f"[ERROR] No se encontró la carpeta de origen: {src_folder}")
                skipped_programs.append(f"{display_name} (Origen no encontrado)")
                return

        while True:
            try:
                # 1. Copiar la carpeta a la raíz del disco C:
                print(f"\n[PASO 1/2] Copiando carpeta '{folder_name}' hacia '{dest_folder}'...")
                shutil.copytree(src_folder, dest_folder, dirs_exist_ok=True)
                print(f"[Ok] Carpeta copiada exitosamente en: {dest_folder}")

                # 2. Trasladarse y ejecutar: Setup.exe /configure <xml>
                print(f"\n[PASO 2/2] Ejecutando instalación en {dest_folder}: Setup.exe /configure {xml_name} ...")
                print("  -> Por favor espera a que el Asistente de Office complete la instalación...")

                cmd = f'Setup.exe /configure "{xml_name}"'
                res = subprocess.run(cmd, cwd=dest_folder, shell=True)

                if res.returncode == 0:
                    print(f"[Ok] {display_name} se ha instalado correctamente.")
                    installed_programs.append(display_name)
                    break
                else:
                    print(f"[ERROR] La instalación de {display_name} finalizó con código: {res.returncode}")
                    try:
                        retry = input("¿Deseas reintentar la instalación de Office? ([R]eintentar / [O]mitir) [R]: ").strip().lower()
                    except Exception:
                        retry = 'o'
                    if retry in ('', 'r', 'reintentar'):
                        continue
                    else:
                        skipped_programs.append(f"{display_name} (Falló)")
                        break
            except Exception as e:
                print(f"[EXCEPCIÓN] Error durante la instalación de Office: {e}")
                try:
                    retry = input("¿Deseas reintentar? ([R]eintentar / [O]mitir) [R]: ").strip().lower()
                except Exception:
                    retry = 'o'
                if retry in ('', 'r', 'reintentar'):
                    continue
                else:
                    skipped_programs.append(f"{display_name} (Error)")
                    break

    def _print_summary(self, installed: List[str], already_installed: List[str], skipped: List[str]):
        """Imprime un resumen visual del estado final de las instalaciones."""
        print("\n================ RESUMEN DE INSTALACIONES ================")
        if already_installed:
            print(f"Ya instalados previamente ({len(already_installed)}):")
            for name in already_installed:
                print(f"  [✓] {name} (Omitido)")
        if installed:
            print(f"\nInstalados en esta sesión ({len(installed)}):")
            for name in installed:
                print(f"  [+] {name}")
        if skipped:
            print(f"\nOmitidos o no instalados ({len(skipped)}):")
            for name in skipped:
                print(f"  [-] {name}")
        print("==========================================================")
        print("\n--- DESPLIEGUE FINALIZADO ---")
