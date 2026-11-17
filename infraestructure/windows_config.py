import subprocess
import shutil
import os
from domain.entities import Configuration
from domain.interfaces import ISystemConfigurator
from infraestructure.group_policy_manager import LocalGroupPolicyManager

class WindowsSystemConfigurator(ISystemConfigurator):
    def is_applied(self, config: Configuration) -> bool:
        """Verifica si la configuración ya se encuentra aplicada previamente en el sistema."""
        try:
            # Si es una directiva de refresco (como gpupdate), no es un estado estático individual
            if getattr(config, 'is_refresh', False):
                return False

            # Para directivas GPO, verificar tanto el registro como Registry.pol si corresponde
            if config.action_type == "gpo":
                check_key = config.parameters.get("check_key")
                if check_key:
                    res = subprocess.run(f'reg query {check_key}', shell=True, capture_output=True, text=True, errors="replace")
                    if res.returncode != 0:
                        return False
                    expected_val = config.parameters.get("expected_val")
                    if expected_val and expected_val.lower() not in res.stdout.lower():
                        return False
                # Verificar que Registry.pol exista (para gpedit.msc)
                pol_path = LocalGroupPolicyManager.get_machine_pol_path()
                if not os.path.exists(pol_path):
                    return False
                return True

            # 1. Verificación por consulta de Registro de Windows (check_key)
            check_key = config.parameters.get("check_key")
            if check_key:
                res = subprocess.run(f'reg query {check_key}', shell=True, capture_output=True, text=True, errors="replace")
                if res.returncode != 0:
                    return False
                expected_val = config.parameters.get("expected_val")
                if expected_val:
                    return expected_val.lower() in res.stdout.lower()
                return True

            # 2. Verificación por ruta de archivo o carpeta (check_path)
            check_path = config.parameters.get("check_path")
            if check_path:
                return os.path.exists(os.path.expandvars(check_path))

            # 3. Verificación de desactivación de Firewall
            if "netsh advfirewall set allprofiles state off" in config.parameters.get("command", ""):
                res = subprocess.run('netsh advfirewall show allprofiles state', shell=True, capture_output=True, text=True, errors="replace")
                if res.returncode == 0:
                    out = res.stdout.upper()
                    # Si no contiene 'ACTIVAR' ni 'ON', ya está desactivado
                    return not any(term in out for term in ["ACTIVAR", " ON", "\tON"])

            # 4. Verificación por tipo de acción
            if config.action_type == "feature":
                return self._is_feature_enabled(config.parameters.get("feature_name", ""))
            elif config.action_type == "copy":
                dest = config.parameters.get("destination", "")
                return os.path.exists(os.path.expandvars(dest)) if dest else False

            return False
        except Exception:
            return False

    def _is_feature_enabled(self, feature_name: str) -> bool:
        """Verifica si una característica opcional de Windows ya está habilitada."""
        if not feature_name:
            return False

        # Verificación rápida por registro para .NET 3.5
        if feature_name.lower() == "netfx3":
            reg_check = subprocess.run(
                r'reg query "HKLM\SOFTWARE\Microsoft\NET Framework Setup\NDP\v3.5" /v Install',
                shell=True, capture_output=True, text=True, errors="replace"
            )
            if reg_check.returncode == 0 and "0x1" in reg_check.stdout:
                return True

        # Verificación estándar con DISM
        command = f'dism.exe /Online /Get-FeatureInfo /FeatureName:{feature_name}'
        res = subprocess.run(command, shell=True, capture_output=True, text=True, errors="replace")
        if res.returncode == 0:
            stdout_upper = res.stdout.upper()
            return "ENABLED" in stdout_upper or "HABILITADO" in stdout_upper
        return False

    def apply(self, config: Configuration) -> bool:
        try:
            # Enrutamos la acción según el tipo definido en la entidad
            if config.action_type == "gpo":
                gpo_entries = config.parameters.get("gpo_entries", [])
                gpo_success = LocalGroupPolicyManager.apply_gpo_entries(gpo_entries)
                # Opcionalmente ejecutar comando CMD de respaldo si existe
                cmd = config.parameters.get("command")
                if cmd:
                    self._run_script(cmd)
                return gpo_success
            elif config.action_type == "feature":
                return self._enable_windows_feature(config.parameters.get("feature_name", ""))
            elif config.action_type == "copy":
                return self._copy_files(config.parameters.get("source", ""), config.parameters.get("destination", ""))
            elif config.action_type == "script":
                return self._run_script(config.parameters.get("command", ""))
            else:
                print(f"  -> [ERROR] Tipo de acción desconocida: {config.action_type}")
                return False
        except Exception as e:
            print(f"  -> [EXCEPCIÓN] Fallo al aplicar configuración {config.name}: {e}")
            return False

    def _enable_windows_feature(self, feature_name: str) -> bool:
        """Utiliza DISM para habilitar características opcionales de Windows silenciosamente."""
        command = f'dism.exe /Online /Enable-Feature /FeatureName:{feature_name} /All /NoRestart /Quiet'
        result = subprocess.run(command, shell=True, capture_output=True, text=True, errors="replace")
        return result.returncode in (0, 3010)

    def _copy_files(self, src: str, dest: str) -> bool:
        """Copia archivos o carpetas, útil para mover configuraciones o licencias."""
        if not os.path.exists(src):
            print(f"  -> [ERROR] Origen no encontrado: {src}")
            return False
            
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if os.path.isdir(src):
            shutil.copytree(src, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dest)
        return True

    def _run_script(self, command: str) -> bool:
        """Ejecuta un comando CMD o PowerShell directo (ej. para gpedit o registro)."""
        result = subprocess.run(command, shell=True, capture_output=True, text=True, errors="replace")
        if result.returncode != 0:
            error_msg = result.stderr.strip() or result.stdout.strip()
            print(f"  -> [ERROR Script]: {error_msg}")
            return False
        return True