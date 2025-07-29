import click
from typing import Optional
from llx.plugin_manager import plugin_manager


class PluginCommand:
    """Handle plugin management commands"""
    
    def list_plugins(self, verbose: bool = False):
        """List all available plugins"""
        plugins = plugin_manager.list_plugins()
        
        if not plugins:
            click.echo("No plugins found.")
            return
        
        click.echo(click.style("📦 Available Plugins", fg='cyan', bold=True))
        click.echo("=" * 50)
        
        # Group by status
        statuses = {"loaded": [], "available": [], "disabled": []}
        for plugin_info in plugins.values():
            status = plugin_info["status"]
            if status in statuses:
                statuses[status].append(plugin_info)
        
        # Display each status group
        for status, plugin_list in statuses.items():
            if not plugin_list:
                continue
                
            status_colors = {
                "loaded": "green",
                "available": "yellow", 
                "disabled": "red"
            }
            status_icons = {
                "loaded": "✅",
                "available": "⭕",
                "disabled": "❌"
            }
            
            click.echo(f"\n{status_icons[status]} {status.upper()}:")
            click.echo("-" * 20)
            
            for plugin in sorted(plugin_list, key=lambda x: x["name"]):
                name_version = f"{plugin['name']} v{plugin['version']}"
                click.echo(click.style(f"  {name_version}", fg=status_colors[status], bold=True))
                click.echo(f"    {plugin['description']}")
                
                if verbose:
                    if plugin['author']:
                        click.echo(f"    Author: {plugin['author']}")
                    if plugin['dependencies']:
                        deps = ", ".join(plugin['dependencies'].keys())
                        click.echo(f"    Dependencies: {deps}")
                
                click.echo()
    
    def enable_plugin(self, plugin_name: str):
        """Enable a plugin"""
        if plugin_manager.enable_plugin(plugin_name):
            click.echo(click.style(f"✅ Enabled plugin: {plugin_name}", fg='green'))
            click.echo("Note: Restart required for changes to take effect.")
        else:
            click.echo(click.style(f"❌ Failed to enable plugin: {plugin_name}", fg='red'))
    
    def disable_plugin(self, plugin_name: str):
        """Disable a plugin"""
        if plugin_manager.disable_plugin(plugin_name):
            click.echo(click.style(f"✅ Disabled plugin: {plugin_name}", fg='green'))
            click.echo("Note: Restart required for changes to take effect.")
        else:
            click.echo(click.style(f"❌ Failed to disable plugin: {plugin_name}", fg='red'))
    
    def show_plugin(self, plugin_name: str):
        """Show detailed information about a plugin"""
        plugins = plugin_manager.list_plugins()
        plugin_info = plugins.get(plugin_name)
        
        if not plugin_info:
            click.echo(click.style(f"❌ Plugin '{plugin_name}' not found", fg='red'))
            return
        
        click.echo(click.style(f"📦 {plugin_info['name']} v{plugin_info['version']}", fg='cyan', bold=True))
        click.echo("=" * 40)
        click.echo(f"Description: {plugin_info['description']}")
        click.echo(f"Status: {plugin_info['status']}")
        
        if plugin_info['author']:
            click.echo(f"Author: {plugin_info['author']}")
        
        if plugin_info['dependencies']:
            click.echo("Dependencies:")
            for dep, version in plugin_info['dependencies'].items():
                click.echo(f"  - {dep} {version}")
        else:
            click.echo("Dependencies: None")
    
    def install_plugin(self, plugin_path: str):
        """Install a plugin from a path or URL (placeholder for future implementation)"""
        click.echo(click.style("🚧 Plugin installation not yet implemented", fg='yellow'))
        click.echo("For now, manually copy plugin files to ~/.llx/plugins/")
        click.echo(f"Attempted to install from: {plugin_path}")
    
    def create_plugin_directory(self):
        """Create the user plugin directory if it doesn't exist"""
        import os
        from pathlib import Path
        
        plugin_dir = Path.home() / ".llx" / "plugins"
        plugin_dir.mkdir(parents=True, exist_ok=True)
        
        # Create example plugin
        example_plugin = plugin_dir / "example_plugin.py"
        if not example_plugin.exists():
            example_content = '''from llx.plugins.base_plugin import BasePlugin
import click


class ExamplePlugin(BasePlugin):
    """Example plugin demonstrating the plugin interface"""
    
    @property
    def name(self) -> str:
        return "example"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Example plugin for demonstration purposes"
    
    @property
    def author(self) -> str:
        return "LLX Team"
    
    def register_commands(self, cli_group):
        @cli_group.group()
        def example():
            """Example plugin commands"""
            pass
        
        @example.command()
        @click.argument('message')
        def hello(message):
            """Say hello with a custom message"""
            click.echo(f"Hello from example plugin: {message}")
        
        @example.command()
        def info():
            """Show plugin information"""
            click.echo(f"Plugin: {self.name} v{self.version}")
            click.echo(f"Description: {self.description}")
'''
            with open(example_plugin, 'w') as f:
                f.write(example_content)
        
        click.echo(click.style(f"✅ Created plugin directory: {plugin_dir}", fg='green'))
        if not example_plugin.exists():
            click.echo(f"📝 Created example plugin: {example_plugin}")
        click.echo("\nTo get started:")
        click.echo("1. Copy your plugin files to this directory")
        click.echo("2. Run 'llx plugin list' to see available plugins")
        click.echo("3. Run 'llx plugin enable <plugin-name>' to enable a plugin")