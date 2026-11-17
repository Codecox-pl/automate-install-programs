import os
from domain.entities import Program

def get_programs_list(base_path: str) -> list:

    return [
        Program(
            name="Autodesk DWG TrueView 2025",
            installer_path=os.path.join(base_path, "Software_Base", "DWGTrueView_2025_English_64bit_db.sfx.exe"),
            silent_args="", 
            is_msi=False,
            is_interactive=True,
            check_names=["Autodesk DWG TrueView", "DWG TrueView"],
            check_paths=[r"C:\Program Files\Autodesk\DWG TrueView 2025 - English\dwgviewr.exe"]
        ),
        Program(
            name="7 ZIP",
            installer_path=os.path.join(base_path, "Software_Base", "7z2600-x64.exe"),
            silent_args="/S",
            is_msi=False,
            is_interactive=False,
            check_names=["7-Zip"],
            check_paths=[r"C:\Program Files\7-Zip\7z.exe", r"C:\Program Files (x86)\7-Zip\7z.exe"]
        ),
        Program(
            name="Chrome",
            installer_path=os.path.join(base_path, "Software_Base", "ChromeSetup.exe"),
            silent_args="/silent /install",
            is_msi=False,
            is_interactive=False,
            check_names=["Google Chrome"],
            check_paths=[r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"]
        ),
        Program(
            name="Citrix",
            installer_path=os.path.join(base_path, "Software_Base", "CitrixWorkspace2409.10.exe"),
            silent_args="/silent",
            is_msi=False,
            is_interactive=False,
            check_names=["Citrix Workspace"],
            check_paths=[
                r"C:\Program Files (x86)\Citrix\ICA Client\SelfServicePlugin\SelfService.exe",
                r"C:\Program Files\Citrix\ICA Client\SelfServicePlugin\SelfService.exe"
            ]
        ),
        Program(
            name="Microsoft Teams",
            installer_path=os.path.join(base_path, "Software_Base", "MSTeamsSetup.exe"),
            silent_args="/silent",
            is_msi=False,
            is_interactive=False,
            check_names=["Microsoft Teams"],
            check_paths=[r"%LOCALAPPDATA%\Microsoft\Teams\current\Teams.exe"]
        ),
        Program(
            name="USB Drive Letter Manager",
            installer_path=os.path.join(base_path, "Software_Base", "Usb Drive Letter Manager WXYZ.exe"),
            silent_args="",
            is_msi=False,
            is_interactive=True,
            check_names=["USBDLM", "USB Drive Letter Manager"],
            check_paths=[r"C:\Program Files\USBDLM\USBDLM.exe", r"C:\Program Files (x86)\USBDLM\USBDLM.exe"]
        ),
        Program(
            name="VLC Media Player",
            installer_path=os.path.join(base_path, "Software_Base", "vlc-3.0.21-win64.exe"),
            silent_args="/S",
            is_msi=False,
            is_interactive=False,
            check_names=["VLC media player", "VideoLAN VLC"],
            check_paths=[r"C:\Program Files\VideoLAN\VLC\vlc.exe", r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"]
        ),
        Program(
            name="Synology Active Backup",
            installer_path=os.path.join(base_path, "Software_Base", "Synology", "synologyABB-61.msi"),
            silent_args="",
            is_msi=True,
            is_interactive=True,
            check_names=["Synology Active Backup"],
            check_paths=[r"C:\Program Files\Synology\ActiveBackupforBusinessAgent\ui\ActiveBackup_Agent.exe"]
        ),
        Program(
            name="Adobe Acrobat Reader",
            installer_path=os.path.join(base_path, "Software_Base", "readerdc64_es_xa_crd_install.exe"),
            silent_args="",
            is_msi=False,
            is_interactive=True,
            check_names=["Adobe Acrobat", "Adobe Reader", "Acrobat Reader"],
            check_paths=[
                r"C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe",
                r"C:\Program Files (x86)\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe"
            ]
        ),
        Program(
            name="DISCOVERY",
            installer_path=os.path.join(base_path, "Software_Base", "DISCOVERY", "install.exe"),
            silent_args="/silent",
            is_msi=False,
            is_interactive=False,
            check_names=["Discovery", "DISCOVERY"],
            check_paths=[r"C:\DISCOVERY\install.exe", r"C:\Program Files\Discovery\install.exe"]
        )
    ]
