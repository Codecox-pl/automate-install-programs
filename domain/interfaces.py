from abc import ABC, abstractmethod
from domain.entities import Program, Configuration

class IProgramInstaller(ABC):
    """Contrato que cualquier instalador real deberá cumplir."""
    @abstractmethod
    def install(self, program: Program) -> bool:
        """Instala el programa y retorna True si fue exitoso, False en caso contrario."""
        pass

    @abstractmethod
    def is_installed(self, program: Program) -> bool:
        """Verifica si el programa ya se encuentra instalado en el sistema."""
        pass

class ISystemConfigurator(ABC):
    """Contrato para el manejador de configuraciones de Windows."""
    @abstractmethod
    def apply(self, config: Configuration) -> bool:
        """Aplica la configuración y retorna True si fue exitoso, False en caso contrario."""
        pass

    @abstractmethod
    def is_applied(self, config: Configuration) -> bool:
        """Verifica si la configuración ya se encuentra aplicada previamente en el sistema."""
        pass
