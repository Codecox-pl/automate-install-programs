from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class Program:
    """Representa un programa que debe ser instalado"""
    name: str
    installer_path: str # Ruta relativa o absoluta del instalador
    silent_args: str = "" # Argumentos para instalación desatendida (ej. '/S' o '/quiet')
    is_msi: bool = False # Bandera para identificar si requiere msiexec
    is_interactive: bool = False # Si requiere interacción del usuario (asistente en pantalla con 'Siguiente')
    check_names: List[str] = field(default_factory=list) # Nombres o patrones a buscar en el Registro de Desinstaladores de Windows
    check_paths: List[str] = field(default_factory=list) # Rutas de ejecutables conocidos para validar si ya está instalado

@dataclass
class Configuration:
    """Representa una configuracion del sistema a aplicar"""
    name: str
    action_type: str # Valores esperados: 'feature' (dism), 'copy' (archivos), 'script' (cmd/powershell)
    parameters: Dict[str, str] # Diccionario con rutas, comandos o nombres de características
    is_refresh: bool = False # Si es una directiva de actualización/refresco (ej. gpupdate)