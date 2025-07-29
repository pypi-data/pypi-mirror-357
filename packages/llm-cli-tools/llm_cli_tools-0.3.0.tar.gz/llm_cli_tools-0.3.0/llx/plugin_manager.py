import os
import sys
import importlib
import importlib.util
import json
import click
from pathlib import Path
from typing import Dict, List, Optional, Type
from llx.plugins.base_plugin import BasePlugin


class PluginManager:
    """Manages plugin loading, discovery, and lifecycle"""
    
    def __init__(self):
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_dirs = [
            Path.home() / ".llx" / "plugins",
            Path(__file__).parent / "plugins" / "builtin"
        ]
        self._config_file = Path.home() / ".llx" / "plugins.json"
        self._config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load plugin configuration"""
        if self._config_file.exists():
            try:
                with open(self._config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {"enabled": [], "disabled": []}
    
    def _save_config(self):
        """Save plugin configuration"""
        self._config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self._config_file, 'w') as f:
            json.dump(self._config, f, indent=2)
    
    def discover_plugins(self) -> List[str]:
        """Discover available plugins in plugin directories"""
        discovered = []
        
        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.exists():
                continue
                
            for item in plugin_dir.iterdir():
                if item.is_file() and item.suffix == '.py' and not item.name.startswith('_'):
                    discovered.append(str(item))
                elif item.is_dir() and (item / "__init__.py").exists():
                    discovered.append(str(item))
        
        return discovered
    
    def load_plugin_from_path(self, plugin_path: str) -> Optional[BasePlugin]:
        """Load a plugin from a file path"""
        try:
            plugin_path = Path(plugin_path)
            
            if plugin_path.is_file():
                # Load from .py file
                spec = importlib.util.spec_from_file_location(
                    plugin_path.stem, plugin_path
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            else:
                # Load from directory (package)
                spec = importlib.util.spec_from_file_location(
                    plugin_path.name, plugin_path / "__init__.py"
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            
            # Find plugin class
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, BasePlugin) and 
                    attr != BasePlugin):
                    plugin_class = attr
                    break
            
            if plugin_class is None:
                click.echo(f"⚠️  No plugin class found in {plugin_path}", err=True)
                return None
            
            # Instantiate plugin
            plugin_instance = plugin_class()
            
            # Validate dependencies
            if not plugin_instance.validate_dependencies():
                click.echo(f"⚠️  Plugin {plugin_instance.name} has unmet dependencies", err=True)
                return None
            
            return plugin_instance
            
        except Exception as e:
            click.echo(f"❌ Failed to load plugin from {plugin_path}: {e}", err=True)
            return None
    
    def load_plugins(self, cli_group):
        """Load all enabled plugins and register their commands"""
        discovered = self.discover_plugins()
        
        for plugin_path in discovered:
            plugin_name = Path(plugin_path).stem
            
            # Skip if explicitly disabled
            if plugin_name in self._config.get("disabled", []):
                continue
            
            # Load plugin
            plugin = self.load_plugin_from_path(plugin_path)
            if plugin:
                try:
                    # Register with CLI
                    plugin.register_commands(cli_group)
                    
                    # Store reference
                    self.plugins[plugin.name] = plugin
                    
                    # Call load hook
                    plugin.on_load()
                    
                    click.echo(f"✅ Loaded plugin: {plugin.name} v{plugin.version}", err=True)
                    
                except Exception as e:
                    click.echo(f"❌ Failed to register plugin {plugin.name}: {e}", err=True)
    
    def list_plugins(self) -> Dict[str, Dict]:
        """List all available plugins (loaded and discovered)"""
        plugins_info = {}
        
        # Add loaded plugins
        for name, plugin in self.plugins.items():
            plugins_info[name] = {
                "name": plugin.name,
                "version": plugin.version,
                "description": plugin.description,
                "author": plugin.author,
                "status": "loaded",
                "dependencies": plugin.dependencies
            }
        
        # Add discovered but not loaded plugins
        discovered = self.discover_plugins()
        for plugin_path in discovered:
            plugin_name = Path(plugin_path).stem
            if plugin_name not in plugins_info:
                # Try to load plugin metadata without registering
                plugin = self.load_plugin_from_path(plugin_path)
                if plugin:
                    plugins_info[plugin.name] = {
                        "name": plugin.name,
                        "version": plugin.version,
                        "description": plugin.description,
                        "author": plugin.author,
                        "status": "disabled" if plugin.name in self._config.get("disabled", []) else "available",
                        "dependencies": plugin.dependencies
                    }
        
        return plugins_info
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin"""
        if plugin_name in self._config.get("disabled", []):
            self._config["disabled"].remove(plugin_name)
        
        if plugin_name not in self._config.get("enabled", []):
            self._config.setdefault("enabled", []).append(plugin_name)
        
        self._save_config()
        return True
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin"""
        if plugin_name in self._config.get("enabled", []):
            self._config["enabled"].remove(plugin_name)
        
        if plugin_name not in self._config.get("disabled", []):
            self._config.setdefault("disabled", []).append(plugin_name)
        
        # Unload if currently loaded
        if plugin_name in self.plugins:
            self.plugins[plugin_name].on_unload()
            del self.plugins[plugin_name]
        
        self._save_config()
        return True
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get a loaded plugin by name"""
        return self.plugins.get(plugin_name)


# Global plugin manager instance
plugin_manager = PluginManager()