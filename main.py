import sys
import os
import ctypes
import traceback


def pause_and_exit(code: int = 0):
    """Pausa la consola para que el usuario pueda ver los mensajes antes de cerrarse."""
    try:
        input("\nPresiona Enter para salir...")
    except Exception:
        pass
    sys.exit(code)


try:
    from infraestructure.windows_installer import WindowsProgramInstaller
    from infraestructure.windows_config import WindowsSystemConfigurator
    from application.use_cases import SystemDeploymentUseCase
    from config.programs import get_programs_list
    from config.policies import get_policies_list
except Exception:
    print("\n==================================================")
    print("[ERROR CRÍTICO] Falló al cargar los módulos del sistema:")
    print("==================================================\n")
    traceback.print_exc()
    print("\n==================================================")
    pause_and_exit(1)


def get_base_path() -> str:
    """Detecta automáticamente la letra y ruta del USB desde donde se ejecuta."""
    if getattr(sys, 'frozen', False):
        # Si se ejecuta como el main.exe final (PyInstaller)
        return os.path.dirname(sys.executable)
    else:
        # Si se ejecuta como main.py durante el desarrollo
        return os.path.dirname(os.path.abspath(__file__))


def is_admin() -> bool:
    """Valida si el script se está ejecutando con privilegios de administrador."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def main():
    if not is_admin():
        print("==================================================")
        print("[ADVERTENCIA] Por favor, ejecuta este programa como Administrador.")
        print("Haz clic derecho sobre el archivo y selecciona 'Ejecutar como administrador'.")
        print("==================================================")
        pause_and_exit(1)

    base_path = get_base_path()
    print(f"[INFO] Directorio base de ejecución: {base_path}")

    # 1. Definir los programas a instalar y configuraciones
    programs = get_programs_list(base_path)
    configurations = get_policies_list()

    # 2. Inicializar la Infraestructura (Adaptadores)
    windows_installer = WindowsProgramInstaller()
    windows_configurator = WindowsSystemConfigurator()

    # 3. Inicializar el Caso de Uso (Inyección de dependencias)
    deployment_use_case = SystemDeploymentUseCase(
        installer=windows_installer,
        configurator=windows_configurator
    )

    # 4. Ejecutar la orquestación
    deployment_use_case.execute(programs=programs, configurations=configurations, base_path=base_path)

    print("\n==================================================")
    print("[ÉXITO] Proceso completado exitosamente.")
    print("==================================================")
    pause_and_exit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
    except Exception:
        print("\n==================================================")
        print("[ERROR CRÍTICO] El script falló inesperadamente:")
        print("==================================================\n")
        traceback.print_exc()
        print("\n==================================================")
        pause_and_exit(1)
