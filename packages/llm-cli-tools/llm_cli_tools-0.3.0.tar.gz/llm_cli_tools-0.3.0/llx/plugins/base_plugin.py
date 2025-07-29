from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BasePlugin(ABC):
    """Base class for all LLX plugins"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name (used for identification)"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description"""
        pass
    
    @property
    def author(self) -> Optional[str]:
        """Plugin author (optional)"""
        return None
    
    @property
    def dependencies(self) -> Dict[str, str]:
        """Plugin dependencies (package_name: version_spec)"""
        return {}
    
    @abstractmethod
    def register_commands(self, cli_group):
        """Register plugin commands with the CLI group
        
        Args:
            cli_group: Click group to register commands with
        """
        pass
    
    def on_load(self):
        """Called when plugin is loaded (optional hook)"""
        pass
    
    def on_unload(self):
        """Called when plugin is unloaded (optional hook)"""
        pass
    
    def validate_dependencies(self) -> bool:
        """Validate that all dependencies are available"""
        import importlib
        
        for package, version_spec in self.dependencies.items():
            try:
                importlib.import_module(package)
                # TODO: Add version checking if needed
            except ImportError:
                return False
        return True