import os
from domain.entities import Configuration

def get_policies_list() -> list:

    return [
        Configuration(
            name="Habilitar caracteristica .NET 3.5",
            action_type="feature",
            parameters={"feature_name": "NetFx3"}
        ),
        Configuration(
            name="Habilitar protocolo SMB 1.0/CIFS",
            action_type="feature",
            parameters={"feature_name": "SMB1Protocol"}
        ),
        Configuration(
            name="Desactivar Firewall de Windows",
            action_type="script",
            parameters={"command": "netsh advfirewall set allprofiles state off"}
        ),
        # ==========================================
        # 1. Administrar actualizaciones ofrecidas por el servicio de actualización de Windows Server
        # ==========================================
        Configuration(
            name="GPO: Especificar la ubicación del servicio Windows Update en la intranet",
            action_type="gpo",
            parameters={
                "gpo_entries": [
                    ("Software\\Policies\\Microsoft\\Windows\\WindowsUpdate", "WUServer", "REG_SZ", "http://fdswinsus:8530"),
                    ("Software\\Policies\\Microsoft\\Windows\\WindowsUpdate", "WUStatusServer", "REG_SZ", "http://fdswinsus:8530"),
                    ("Software\\Policies\\Microsoft\\Windows\\WindowsUpdate", "UpdateServiceUrlAlternate", "REG_SZ", "http://fdswinsus:8530"),
                    ("Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU", "UseWUServer", "REG_DWORD", 1),
                ],
                "command": 'reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate" /v WUServer /t REG_SZ /d "http://fdswinsus:8530" /f & reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate" /v WUStatusServer /t REG_SZ /d "http://fdswinsus:8530" /f & reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate" /v UpdateServiceUrlAlternate /t REG_SZ /d "http://fdswinsus:8530" /f & reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /v UseWUServer /t REG_DWORD /d 1 /f',
                "check_key": '"HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate" /v WUServer',
                "expected_val": "http://fdswinsus:8530"
            }
        ),
        Configuration(
            name="GPO: Frecuencia de detección de Actualizaciones automáticas",
            action_type="gpo",
            parameters={
                "gpo_entries": [
                    ("Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU", "DetectionFrequencyEnabled", "REG_DWORD", 1),
                    ("Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU", "DetectionFrequency", "REG_DWORD", 22),
                ],
                "command": 'reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /v DetectionFrequencyEnabled /t REG_DWORD /d 1 /f & reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /v DetectionFrequency /t REG_DWORD /d 22 /f',
                "check_key": '"HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /v DetectionFrequency',
                "expected_val": "0x16"
            }
        ),
        Configuration(
            name="GPO: Permitir actualizaciones firmadas procedentes de la intranet",
            action_type="gpo",
            parameters={
                "gpo_entries": [
                    ("Software\\Policies\\Microsoft\\Windows\\WindowsUpdate", "AcceptTrustedPublisherCerts", "REG_DWORD", 1),
                ],
                "command": 'reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate" /v AcceptTrustedPublisherCerts /t REG_DWORD /d 1 /f',
                "check_key": '"HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate" /v AcceptTrustedPublisherCerts',
                "expected_val": "0x1"
            }
        ),
        Configuration(
            name="GPO: Especificar el servicio de origen para clases específicas de actualizaciones",
            action_type="gpo",
            parameters={
                "gpo_entries": [
                    ("Software\\Policies\\Microsoft\\Windows\\WindowsUpdate", "SetPolicyDrivenUpdateSourceForFeatureUpdates", "REG_DWORD", 1),
                    ("Software\\Policies\\Microsoft\\Windows\\WindowsUpdate", "SetPolicyDrivenUpdateSourceForQualityUpdates", "REG_DWORD", 1),
                ],
                "command": 'reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate" /v SetPolicyDrivenUpdateSourceForFeatureUpdates /t REG_DWORD /d 1 /f & reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate" /v SetPolicyDrivenUpdateSourceForQualityUpdates /t REG_DWORD /d 1 /f',
                "check_key": '"HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate" /v SetPolicyDrivenUpdateSourceForFeatureUpdates',
                "expected_val": "0x1"
            }
        ),
        # ==========================================
        # 2. Administrar la experiencia del usuario final
        # ==========================================
        Configuration(
            name="GPO: Permitir descargas en conexiones de uso medido",
            action_type="gpo",
            parameters={
                "gpo_entries": [
                    ("Software\\Policies\\Microsoft\\Windows\\WindowsUpdate", "AllowAutoWindowsUpdateDownloadOverMeteredNetwork", "REG_DWORD", 1),
                ],
                "command": 'reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate" /v AllowAutoWindowsUpdateDownloadOverMeteredNetwork /t REG_DWORD /d 1 /f',
                "check_key": '"HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate" /v AllowAutoWindowsUpdateDownloadOverMeteredNetwork',
                "expected_val": "0x1"
            }
        ),
        Configuration(
            name="GPO: Configurar Actualizaciones Automáticas (Opción 4, 13:00 hrs, Microsoft Updates)",
            action_type="gpo",
            parameters={
                "gpo_entries": [
                    ("Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU", "NoAutoUpdate", "REG_DWORD", 0),
                    ("Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU", "AUOptions", "REG_DWORD", 4),
                    ("Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU", "ScheduledInstallDay", "REG_DWORD", 0),
                    ("Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU", "ScheduledInstallTime", "REG_DWORD", 13),
                    ("Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU", "ScheduledInstallEveryWeek", "REG_DWORD", 1),
                    ("Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU", "AllowMUUpdateService", "REG_DWORD", 1),
                ],
                "command": (
                    'reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /v NoAutoUpdate /t REG_DWORD /d 0 /f & '
                    'reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /v AUOptions /t REG_DWORD /d 4 /f & '
                    'reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /v ScheduledInstallDay /t REG_DWORD /d 0 /f & '
                    'reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /v ScheduledInstallTime /t REG_DWORD /d 13 /f & '
                    'reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /v ScheduledInstallEveryWeek /t REG_DWORD /d 1 /f & '
                    'reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /v AllowMUUpdateService /t REG_DWORD /d 1 /f'
                ),
                "check_key": '"HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /v AUOptions',
                "expected_val": "0x4"
            }
        ),
        # ==========================================
        # 3. Administrar las actualizaciones ofrecidas desde Windows Update
        # ==========================================
        Configuration(
            name="GPO: No incluir controladores con las actualizaciones de Windows",
            action_type="gpo",
            parameters={
                "gpo_entries": [
                    ("Software\\Policies\\Microsoft\\Windows\\WindowsUpdate", "ExcludeWUDriversInQualityUpdate", "REG_DWORD", 1),
                ],
                "command": 'reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate" /v ExcludeWUDriversInQualityUpdate /t REG_DWORD /d 1 /f',
                "check_key": '"HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate" /v ExcludeWUDriversInQualityUpdate',
                "expected_val": "0x1"
            }
        ),
        # ==========================================
        # 4. Directivas heredadas de Windows Update
        # ==========================================
        Configuration(
            name="GPO: Opciones de Apagado (Ocultar y quitar predeterminado de Instalar y Apagar)",
            action_type="gpo",
            parameters={
                "gpo_entries": [
                    ("Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU", "NoAUShutdownOption", "REG_DWORD", 1),
                    ("Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU", "NoAUAsDefaultShutdownOption", "REG_DWORD", 1),
                ],
                "command": (
                    'reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /v NoAUShutdownOption /t REG_DWORD /d 1 /f & '
                    'reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /v NoAUAsDefaultShutdownOption /t REG_DWORD /d 1 /f'
                ),
                "check_key": '"HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /v NoAUShutdownOption',
                "expected_val": "0x1"
            }
        ),
        Configuration(
            name="GPO: Comportamiento de notificaciones y reinicio (No reiniciar con usuarios logueados)",
            action_type="gpo",
            parameters={
                "gpo_entries": [
                    ("Software\\Policies\\Microsoft\\Windows\\WindowsUpdate", "AutoRestartRequiredNotificationDismissal", "REG_DWORD", 1),
                    ("Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU", "NoAutoRebootWithLoggedOnUsers", "REG_DWORD", 1),
                ],
                "command": (
                    'reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate" /v AutoRestartRequiredNotificationDismissal /t REG_DWORD /d 1 /f & '
                    'reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /v NoAutoRebootWithLoggedOnUsers /t REG_DWORD /d 1 /f'
                ),
                "check_key": '"HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /v NoAutoRebootWithLoggedOnUsers',
                "expected_val": "0x1"
            }
        ),
        Configuration(
            name="GPO: Deshabilitar Dual Scan (No permitir directivas de aplazamiento)",
            action_type="gpo",
            parameters={
                "gpo_entries": [
                    ("Software\\Policies\\Microsoft\\Windows\\WindowsUpdate", "DisableDualScan", "REG_DWORD", 1),
                ],
                "command": 'reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate" /v DisableDualScan /t REG_DWORD /d 1 /f',
                "check_key": '"HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate" /v DisableDualScan',
                "expected_val": "0x1"
            }
        ),
        Configuration(
            name="GPO: Tipos de actualizaciones y notificaciones de software",
            action_type="gpo",
            parameters={
                "gpo_entries": [
                    ("Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU", "SoftwareNotifications", "REG_DWORD", 1),
                    ("Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU", "AutoInstallMinorUpdates", "REG_DWORD", 1),
                    ("Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU", "IncludeRecommendedUpdates", "REG_DWORD", 1),
                ],
                "command": (
                    'reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /v SoftwareNotifications /t REG_DWORD /d 1 /f & '
                    'reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /v AutoInstallMinorUpdates /t REG_DWORD /d 1 /f & '
                    'reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /v IncludeRecommendedUpdates /t REG_DWORD /d 1 /f'
                ),
                "check_key": '"HKLM\\Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /v SoftwareNotifications',
                "expected_val": "0x1"
            }
        ),
        
        # ==========================================
        # 5. Creación y permisos de carpetas Temporales
        # ==========================================
        Configuration(
            name="Crear C:\\TEMP y asignar permisos Full Control al grupo Usuarios (C:\\TEMP y C:\\Windows\\TEMP)",
            action_type="script",
            parameters={
                "command": (
                    'if not exist "C:\\TEMP" mkdir "C:\\TEMP" & '
                    'icacls "C:\\TEMP" /grant Usuarios:(OI)(CI)F /grant "%COMPUTERNAME%\\Usuarios":(OI)(CI)F /grant *S-1-5-32-545:(OI)(CI)F /T /C /Q & '
                    'icacls "C:\\Windows\\TEMP" /grant Usuarios:(OI)(CI)F /grant "%COMPUTERNAME%\\Usuarios":(OI)(CI)F /grant *S-1-5-32-545:(OI)(CI)F /T /C /Q'
                )
            }
        ),

        # ==========================================
        # 6. Aplicar todos los cambios al sistema (Refresco final)
        # ==========================================
        Configuration(
            name="Forzar actualización de políticas locales (GPUpdate)",
            action_type="script",
            parameters={
                "command": "gpupdate /force"
            },
            is_refresh=True
        ),
    ]
