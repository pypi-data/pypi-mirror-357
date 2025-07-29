import os
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import Mock, patch
import click

from llx.plugin_manager import PluginManager
from llx.plugins.base_plugin import BasePlugin


class TestPlugin(BasePlugin):
    """Test plugin for unit tests"""
    
    @property
    def name(self) -> str:
        return "test-plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Test plugin for unit testing"
    
    @property
    def author(self) -> str:
        return "Test Author"
    
    def register_commands(self, cli_group):
        @cli_group.command()
        def test_command():
            """Test command"""
            click.echo("Test command executed")


class TestBadPlugin(BasePlugin):
    """Plugin with missing dependencies"""
    
    @property
    def name(self) -> str:
        return "bad-plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Plugin with bad dependencies"
    
    @property
    def dependencies(self):
        return {"nonexistent-package": ">=1.0.0"}
    
    def register_commands(self, cli_group):
        pass


class TestPluginSystem:
    """Test suite for the plugin system"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.plugin_manager = PluginManager()
        # Override plugin directories to use temp directory
        self.plugin_manager.plugin_dirs = [Path(self.temp_dir)]
        self.plugin_manager._config_file = Path(self.temp_dir) / "plugins.json"
    
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_plugin_discovery_empty_directory(self):
        """Test plugin discovery in empty directory"""
        discovered = self.plugin_manager.discover_plugins()
        assert discovered == []
    
    def test_plugin_discovery_with_files(self):
        """Test plugin discovery with plugin files"""
        # Create test plugin file
        plugin_file = Path(self.temp_dir) / "test_plugin.py"
        plugin_content = '''
from llx.plugins.base_plugin import BasePlugin

class TestPlugin(BasePlugin):
    @property
    def name(self):
        return "test"
    
    @property
    def version(self):
        return "1.0.0"
    
    @property
    def description(self):
        return "Test plugin"
    
    def register_commands(self, cli_group):
        pass
'''
        plugin_file.write_text(plugin_content)
        
        discovered = self.plugin_manager.discover_plugins()
        assert len(discovered) == 1
        assert str(plugin_file) in discovered
    
    def test_load_plugin_from_path_success(self):
        """Test successful plugin loading"""
        # Create test plugin file
        plugin_file = Path(self.temp_dir) / "test_plugin.py"
        plugin_content = '''
from llx.plugins.base_plugin import BasePlugin
import click

class TestPlugin(BasePlugin):
    @property
    def name(self):
        return "test-plugin"
    
    @property
    def version(self):
        return "1.0.0"
    
    @property
    def description(self):
        return "Test plugin"
    
    def register_commands(self, cli_group):
        @cli_group.command()
        def test_cmd():
            click.echo("test")
'''
        plugin_file.write_text(plugin_content)
        
        plugin = self.plugin_manager.load_plugin_from_path(str(plugin_file))
        assert plugin is not None
        assert plugin.name == "test-plugin"
        assert plugin.version == "1.0.0"
    
    def test_load_plugin_from_path_no_plugin_class(self):
        """Test loading file with no plugin class"""
        # Create file without plugin class
        plugin_file = Path(self.temp_dir) / "not_a_plugin.py"
        plugin_file.write_text("def some_function(): pass")
        
        with patch('click.echo') as mock_echo:
            plugin = self.plugin_manager.load_plugin_from_path(str(plugin_file))
            assert plugin is None
            mock_echo.assert_called()
    
    def test_load_plugin_with_bad_dependencies(self):
        """Test loading plugin with missing dependencies"""
        # Create plugin with bad dependencies
        plugin_file = Path(self.temp_dir) / "bad_plugin.py"
        plugin_content = '''
from llx.plugins.base_plugin import BasePlugin

class BadPlugin(BasePlugin):
    @property
    def name(self):
        return "bad-plugin"
    
    @property
    def version(self):
        return "1.0.0"
    
    @property
    def description(self):
        return "Bad plugin"
    
    @property
    def dependencies(self):
        return {"nonexistent-package": ">=1.0.0"}
    
    def register_commands(self, cli_group):
        pass
'''
        plugin_file.write_text(plugin_content)
        
        with patch('click.echo') as mock_echo:
            plugin = self.plugin_manager.load_plugin_from_path(str(plugin_file))
            assert plugin is None
            mock_echo.assert_called()
    
    def test_load_plugins_with_cli_group(self):
        """Test loading plugins and registering with CLI group"""
        # Create test plugin file
        plugin_file = Path(self.temp_dir) / "test_plugin.py"
        plugin_content = '''
from llx.plugins.base_plugin import BasePlugin
import click

class TestPlugin(BasePlugin):
    @property
    def name(self):
        return "test-plugin"
    
    @property
    def version(self):
        return "1.0.0"
    
    @property
    def description(self):
        return "Test plugin"
    
    def register_commands(self, cli_group):
        @cli_group.command()
        def test_cmd():
            click.echo("test command")
    
    def on_load(self):
        pass
'''
        plugin_file.write_text(plugin_content)
        
        # Mock CLI group
        mock_cli_group = Mock()
        
        with patch('click.echo') as mock_echo:
            self.plugin_manager.load_plugins(mock_cli_group)
            
            # Verify plugin was loaded
            assert "test-plugin" in self.plugin_manager.plugins
            plugin = self.plugin_manager.plugins["test-plugin"]
            assert plugin.name == "test-plugin"
            
            # Verify echo was called for successful load
            mock_echo.assert_called()
    
    def test_list_plugins(self):
        """Test listing plugins functionality"""
        # Add a loaded plugin
        test_plugin = TestPlugin()
        self.plugin_manager.plugins["test-plugin"] = test_plugin
        
        plugins_info = self.plugin_manager.list_plugins()
        
        assert "test-plugin" in plugins_info
        plugin_info = plugins_info["test-plugin"]
        assert plugin_info["name"] == "test-plugin"
        assert plugin_info["version"] == "1.0.0"
        assert plugin_info["description"] == "Test plugin for unit testing"
        assert plugin_info["author"] == "Test Author"
        assert plugin_info["status"] == "loaded"
    
    def test_enable_disable_plugin(self):
        """Test plugin enable/disable functionality"""
        plugin_name = "test-plugin"
        
        # Test enable
        result = self.plugin_manager.enable_plugin(plugin_name)
        assert result is True
        assert plugin_name in self.plugin_manager._config.get("enabled", [])
        
        # Test disable
        result = self.plugin_manager.disable_plugin(plugin_name)
        assert result is True
        assert plugin_name in self.plugin_manager._config.get("disabled", [])
        assert plugin_name not in self.plugin_manager._config.get("enabled", [])
    
    def test_get_plugin(self):
        """Test getting plugin by name"""
        test_plugin = TestPlugin()
        self.plugin_manager.plugins["test-plugin"] = test_plugin
        
        retrieved_plugin = self.plugin_manager.get_plugin("test-plugin")
        assert retrieved_plugin is test_plugin
        
        non_existent = self.plugin_manager.get_plugin("non-existent")
        assert non_existent is None
    
    def test_config_persistence(self):
        """Test plugin configuration persistence"""
        plugin_name = "test-plugin"
        
        # Enable plugin
        self.plugin_manager.enable_plugin(plugin_name)
        
        # Create new plugin manager instance with same config file
        new_manager = PluginManager()
        new_manager._config_file = self.plugin_manager._config_file
        new_config = new_manager._load_config()
        
        assert plugin_name in new_config.get("enabled", [])


class TestBasePlugin:
    """Test suite for BasePlugin base class"""
    
    def test_validate_dependencies_success(self):
        """Test dependency validation with available packages"""
        plugin = TestPlugin()
        # TestPlugin has no dependencies by default
        assert plugin.validate_dependencies() is True
    
    def test_validate_dependencies_failure(self):
        """Test dependency validation with missing packages"""
        plugin = TestBadPlugin()
        assert plugin.validate_dependencies() is False
    
    def test_optional_properties(self):
        """Test optional plugin properties"""
        plugin = TestPlugin()
        
        # Test optional properties
        assert plugin.author == "Test Author"
        assert plugin.dependencies == {}
        
        # Test lifecycle hooks (should not raise)
        plugin.on_load()
        plugin.on_unload()


if __name__ == "__main__":
    pytest.main([__file__])