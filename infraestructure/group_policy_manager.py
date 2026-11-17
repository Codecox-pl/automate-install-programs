import os
import sys
import struct
import winreg
from typing import List, Tuple, Any

REG_SZ = 1
REG_EXPAND_SZ = 2
REG_BINARY = 3
REG_DWORD = 4
REG_MULTI_SZ = 7
REG_QWORD = 11

class LocalGroupPolicyManager:
    """
    Administra y sincroniza políticas locales de Windows escribiendo directamente
    en Registry.pol (el archivo fuente de gpedit.msc) y en el Registro (HKLM).
    """

    @staticmethod
    def get_machine_pol_path() -> str:
        system_root = os.environ.get("SystemRoot", r"C:\Windows")
        # En caso de ejecutarse en proceso de 32 bits en Windows de 64 bits:
        sysnative = os.path.join(system_root, "Sysnative")
        if os.path.exists(sysnative):
            base_dir = os.path.join(sysnative, "GroupPolicy")
        else:
            base_dir = os.path.join(system_root, "System32", "GroupPolicy")
        return os.path.join(base_dir, "Machine", "Registry.pol")

    @staticmethod
    def get_gpt_ini_path() -> str:
        system_root = os.environ.get("SystemRoot", r"C:\Windows")
        sysnative = os.path.join(system_root, "Sysnative")
        if os.path.exists(sysnative):
            base_dir = os.path.join(sysnative, "GroupPolicy")
        else:
            base_dir = os.path.join(system_root, "System32", "GroupPolicy")
        return os.path.join(base_dir, "gpt.ini")

    @classmethod
    def read_registry_pol(cls, file_path: str) -> List[Tuple[str, str, int, bytes]]:
        """Lee y deserializa el formato binario PReg de Registry.pol."""
        if not os.path.exists(file_path):
            return []
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            if len(data) < 8 or data[:4] != b"PReg":
                return []

            entries = []
            idx = 8
            open_bracket = "[".encode("utf-16le")
            close_bracket = "]".encode("utf-16le")
            semicolon = ";".encode("utf-16le")

            while idx < len(data):
                if data[idx:idx+2] != open_bracket:
                    idx += 2
                    continue
                idx += 2
                end = data.find(close_bracket, idx)
                if end == -1:
                    break
                raw = data[idx:end]
                idx = end + 2

                # Estructura: key\0 ; val\0 ; type (4B) ; size (4B) ; data (size B)
                p1 = raw.find(semicolon)
                if p1 == -1:
                    continue
                key = raw[:p1].decode("utf-16le", "ignore").rstrip("\x00")
                rest = raw[p1+2:]

                p2 = rest.find(semicolon)
                if p2 == -1:
                    continue
                val = rest[:p2].decode("utf-16le", "ignore").rstrip("\x00")
                rest = rest[p2+2:]

                if len(rest) < 12:
                    continue
                reg_type = struct.unpack("<I", rest[:4])[0]
                size = struct.unpack("<I", rest[6:10])[0]
                val_data = rest[12:12+size]

                entries.append((key, val, reg_type, val_data))
            return entries
        except Exception:
            return []

    @classmethod
    def write_registry_pol(cls, file_path: str, entries: List[Tuple[str, str, int, bytes]]) -> bool:
        """Serializa y escribe las directivas en el formato PReg para gpedit.msc."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            body = [b"PReg\x01\x00\x00\x00"]
            for key, val, reg_type, data in entries:
                k_b = (key + "\x00").encode("utf-16le")
                v_b = (val + "\x00").encode("utf-16le")
                entry = (
                    "[".encode("utf-16le") +
                    k_b +
                    ";".encode("utf-16le") +
                    v_b +
                    ";".encode("utf-16le") +
                    struct.pack("<I", reg_type) +
                    ";".encode("utf-16le") +
                    struct.pack("<I", len(data)) +
                    ";".encode("utf-16le") +
                    data +
                    "]".encode("utf-16le")
                )
                body.append(entry)

            with open(file_path, "wb") as f:
                f.write(b"".join(body))
            return True
        except Exception as e:
            print(f"  -> [ERROR GPO] No se pudo escribir Registry.pol: {e}")
            return False

    @classmethod
    def update_gpt_ini(cls) -> bool:
        """Actualiza gpt.ini para registrar la extensión de directiva de máquina."""
        gpt_path = cls.get_gpt_ini_path()
        try:
            os.makedirs(os.path.dirname(gpt_path), exist_ok=True)
            current_version = 0
            if os.path.exists(gpt_path):
                with open(gpt_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if line.strip().lower().startswith("version="):
                            try:
                                current_version = int(line.strip().split("=")[1])
                            except Exception:
                                pass
            new_version = current_version + 1 if current_version > 0 else 65537
            content = (
                "[General]\n"
                f"Version={new_version}\n"
                "gpcMachineExtensionNames=[{35378EAC-683F-11D2-A89A-00600810724B}{D02B1F72-3407-48AE-BA88-E8213C6761F1}]\n"
            )
            with open(gpt_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"  -> [ADVERTENCIA GPO] No se pudo actualizar gpt.ini: {e}")
            return False

    @classmethod
    def apply_gpo_entries(cls, entries_to_add: List[Tuple[str, str, str, Any]]) -> bool:
        """
        Aplica directivas tanto en Registry.pol (para que gpedit.msc las reconozca como Habilitadas)
        como directamente en el registro HKLM para aplicación inmediata.
        """
        pol_path = cls.get_machine_pol_path()
        existing = cls.read_registry_pol(pol_path)

        # Mapa para evitar duplicados y actualizar valores
        entries_map = {}
        for key, val, reg_type, val_data in existing:
            entries_map[(key.lower(), val.lower())] = (key, val, reg_type, val_data)

        for key, val_name, type_str, raw_val in entries_to_add:
            # 1. Preparar datos binarios para Registry.pol
            if type_str == "REG_DWORD":
                reg_type = REG_DWORD
                data_bytes = struct.pack("<I", int(raw_val))
            elif type_str == "REG_SZ":
                reg_type = REG_SZ
                data_bytes = (str(raw_val) + "\x00").encode("utf-16le")
            else:
                continue

            entries_map[(key.lower(), val_name.lower())] = (key, val_name, reg_type, data_bytes)

            # 2. Aplicar también en vivo en HKEY_LOCAL_MACHINE
            cls._write_to_hklm(key, val_name, type_str, raw_val)

        # 3. Guardar Registry.pol
        saved = cls.write_registry_pol(pol_path, list(entries_map.values()))
        if saved:
            cls.update_gpt_ini()
        return saved

    @classmethod
    def _write_to_hklm(cls, key_path: str, val_name: str, type_str: str, raw_val: Any):
        """Escribe la clave directamente en el Registro de Windows."""
        try:
            with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path) as k:
                if type_str == "REG_DWORD":
                    winreg.SetValueEx(k, val_name, 0, winreg.REG_DWORD, int(raw_val))
                elif type_str == "REG_SZ":
                    winreg.SetValueEx(k, val_name, 0, winreg.REG_SZ, str(raw_val))
        except Exception:
            pass

