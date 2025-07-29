import os
import json
import click
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from llx.plugins.base_plugin import BasePlugin


class TemplateManager:
    """Manages template loading and execution"""
    
    def __init__(self):
        self.template_dirs = [
            Path.home() / ".llx" / "templates",
            Path(__file__).parent / "templates"
        ]
    
    def discover_templates(self) -> List[str]:
        """Discover available templates"""
        templates = []
        for template_dir in self.template_dirs:
            if not template_dir.exists():
                continue
            for file in template_dir.glob("*.json"):
                templates.append(str(file))
        return templates
    
    def load_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Load a template by name"""
        for template_dir in self.template_dirs:
            template_file = template_dir / f"{template_name}.json"
            if template_file.exists():
                try:
                    with open(template_file, 'r') as f:
                        return json.load(f)
                except Exception as e:
                    click.echo(f"❌ Failed to load template {template_name}: {e}", err=True)
                    return None
        return None
    
    def list_templates(self) -> Dict[str, Dict[str, Any]]:
        """List all available templates"""
        templates = {}
        discovered = self.discover_templates()
        
        for template_path in discovered:
            template_file = Path(template_path)
            template_name = template_file.stem
            
            try:
                with open(template_file, 'r') as f:
                    template_data = json.load(f)
                    templates[template_name] = {
                        "name": template_data.get("name", template_name),
                        "description": template_data.get("description", "No description"),
                        "path": str(template_file),
                        "variables": template_data.get("variables", []),
                        "recommended_models": template_data.get("recommended_models", [])
                    }
            except Exception as e:
                click.echo(f"⚠️  Failed to parse template {template_name}: {e}", err=True)
        
        return templates
    
    def create_template_directory(self):
        """Create user template directory with examples"""
        template_dir = Path.home() / ".llx" / "templates"
        template_dir.mkdir(parents=True, exist_ok=True)
        
        # Create example templates
        examples = {
            "code-review.json": {
                "name": "code-review",
                "description": "Review code for best practices and potential issues",
                "prompt": "Please review the following code for:\n- Code quality and best practices\n- Potential bugs or security issues\n- Performance improvements\n- Documentation needs\n\nCode to review:\n{content}\n\n{additional_context}",
                "variables": [
                    {
                        "name": "content",
                        "required": True,
                        "description": "Code content to review"
                    },
                    {
                        "name": "additional_context",
                        "required": False,
                        "description": "Additional context or specific focus areas"
                    }
                ],
                "recommended_models": [
                    "anthropic:claude-3-sonnet",
                    "openai:gpt-4"
                ]
            },
            "translate.json": {
                "name": "translate",
                "description": "Translate text between languages",
                "prompt": "Translate the following text from {from_language} to {to_language}:\n\n{text}\n\nPlease provide a natural, accurate translation.",
                "variables": [
                    {
                        "name": "text",
                        "required": True,
                        "description": "Text to translate"
                    },
                    {
                        "name": "from_language",
                        "required": True,
                        "description": "Source language"
                    },
                    {
                        "name": "to_language",
                        "required": True,
                        "description": "Target language"
                    }
                ],
                "recommended_models": [
                    "openai:gpt-4",
                    "anthropic:claude-3-sonnet"
                ]
            },
            "summarize.json": {
                "name": "summarize",
                "description": "Summarize text or documents",
                "prompt": "Please provide a {summary_type} summary of the following content:\n\n{content}\n\nFocus on the key points and main ideas.",
                "variables": [
                    {
                        "name": "content",
                        "required": True,
                        "description": "Content to summarize"
                    },
                    {
                        "name": "summary_type",
                        "required": False,
                        "description": "Type of summary (brief, detailed, bullet points)",
                        "default": "concise"
                    }
                ],
                "recommended_models": [
                    "anthropic:claude-3-sonnet",
                    "openai:gpt-4"
                ]
            }
        }
        
        created_count = 0
        for filename, template_data in examples.items():
            template_file = template_dir / filename
            if not template_file.exists():
                with open(template_file, 'w') as f:
                    json.dump(template_data, f, indent=2)
                created_count += 1
        
        return template_dir, created_count


class TemplatePlugin(BasePlugin):
    """Template system plugin for LLX"""
    
    def __init__(self):
        self.template_manager = TemplateManager()
    
    @property
    def name(self) -> str:
        return "template"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Template system for common LLM tasks"
    
    @property
    def author(self) -> str:
        return "LLX Team"
    
    @property
    def dependencies(self) -> Dict[str, str]:
        return {}
    
    def register_commands(self, cli_group):
        @cli_group.group()
        def template():
            """Template management and execution commands"""
            pass
        
        @template.command()
        @click.option('--verbose', '-v', is_flag=True, help='Show detailed template information')
        def list(verbose: bool):
            """List all available templates"""
            templates = self.template_manager.list_templates()
            
            if not templates:
                click.echo("No templates found.")
                click.echo("Run 'llx template init' to create the template directory with examples.")
                return
            
            click.echo(click.style("📝 Available Templates", fg='cyan', bold=True))
            click.echo("=" * 50)
            
            for template_name, template_info in sorted(templates.items()):
                click.echo(click.style(f"  {template_name}", fg='green', bold=True))
                click.echo(f"    {template_info['description']}")
                
                if verbose:
                    if template_info['variables']:
                        click.echo("    Variables:")
                        for var in template_info['variables']:
                            required = "required" if var.get('required', False) else "optional"
                            click.echo(f"      - {var['name']} ({required}): {var.get('description', 'No description')}")
                    
                    if template_info['recommended_models']:
                        models = ", ".join(template_info['recommended_models'])
                        click.echo(f"    Recommended models: {models}")
                
                click.echo()
        
        @template.command()
        @click.argument('template_name')
        @click.option('--var', '-v', multiple=True, help='Template variables in format key=value')
        @click.option('--file', '-f', type=click.Path(exists=True), help='File to read content from')
        @click.option('--interactive', '-i', is_flag=True, help='Prompt for missing variables interactively')
        @click.option('--content', help='Content variable (alternative to stdin/file)')
        @click.option('--text', help='Text variable for translation templates')
        @click.option('--from_language', '--from-language', help='Source language for translation')
        @click.option('--to_language', '--to-language', help='Target language for translation') 
        @click.option('--summary_type', '--summary-type', help='Type of summary (brief, detailed, bullet points)')
        @click.option('--additional_context', '--additional-context', help='Additional context for code review')
        def use(template_name: str, var: tuple, file: Optional[str], interactive: bool, **kwargs):
            """Use a template to generate a formatted prompt"""
            template_data = self.template_manager.load_template(template_name)
            if not template_data:
                click.echo(f"❌ Template '{template_name}' not found")
                return
            
            # Parse variables from --var options
            variables = {}
            for v in var:
                if '=' not in v:
                    click.echo(f"❌ Invalid variable format: {v}. Use key=value", err=True)
                    return
                key, value = v.split('=', 1)
                variables[key] = value
            
            # Add direct CLI options as variables (filter out None values)
            for key, value in kwargs.items():
                if value is not None:
                    variables[key] = value
            
            # Read content from file, stdin, or variables
            if file:
                with open(file, 'r') as f:
                    file_content = f.read()
                variables['content'] = file_content
            elif 'content' not in variables and not sys.stdin.isatty():
                # Read from stdin if content not provided and stdin has data
                stdin_content = sys.stdin.read().strip()
                if stdin_content:
                    variables['content'] = stdin_content
            
            # Check for required variables and set defaults
            template_vars = template_data.get('variables', [])
            for var_info in template_vars:
                var_name = var_info['name']
                is_required = var_info.get('required', False)
                
                if var_name not in variables:
                    if 'default' in var_info:
                        variables[var_name] = var_info['default']
                    elif interactive and is_required:
                        description = var_info.get('description', var_name)
                        value = click.prompt(f"Enter {var_name} ({description})")
                        variables[var_name] = value
                    elif is_required:
                        click.echo(f"❌ Required variable '{var_name}' not provided", err=True)
                        click.echo(f"   Description: {var_info.get('description', 'No description')}", err=True)
                        return
                    else:
                        # Set optional variables to empty string if not provided
                        variables[var_name] = ''
            
            # Format prompt
            try:
                prompt = template_data['prompt'].format(**variables)
            except KeyError as e:
                click.echo(f"❌ Missing variable: {e}", err=True)
                return
            
            # Output formatted prompt to stdout
            click.echo(prompt)
        
        @template.command()
        @click.argument('template_name')
        def show(template_name: str):
            """Show detailed information about a template"""
            template_data = self.template_manager.load_template(template_name)
            if not template_data:
                click.echo(f"❌ Template '{template_name}' not found")
                return
            
            click.echo(click.style(f"📝 Template: {template_data.get('name', template_name)}", fg='cyan', bold=True))
            click.echo("=" * 50)
            click.echo(f"Description: {template_data.get('description', 'No description')}")
            
            variables = template_data.get('variables', [])
            if variables:
                click.echo("\nVariables:")
                for var in variables:
                    required = "required" if var.get('required', False) else "optional"
                    default = f" (default: {var['default']})" if 'default' in var else ""
                    click.echo(f"  - {var['name']} ({required}){default}")
                    click.echo(f"    {var.get('description', 'No description')}")
            
            recommended = template_data.get('recommended_models', [])
            if recommended:
                click.echo(f"\nRecommended models: {', '.join(recommended)}")
            
            click.echo(f"\nPrompt template:")
            click.echo("-" * 20)
            click.echo(template_data.get('prompt', 'No prompt defined'))
        
        @template.command()
        def init():
            """Initialize template directory with example templates"""
            template_dir, created_count = self.template_manager.create_template_directory()
            
            click.echo(click.style(f"✅ Template directory: {template_dir}", fg='green'))
            if created_count > 0:
                click.echo(f"📝 Created {created_count} example templates")
            
            click.echo("\nExample usage:")
            click.echo("  llx template list                                    # List templates")
            click.echo("  llx template show code-review                        # Show template details")
            click.echo("  llx template use summarize --var content='Some text' # Generate prompt")
            click.echo("  cat file.py | llx template use code-review           # Use with stdin")
            click.echo("  echo 'Hello' | llx template use translate --from_language=English --to_language=Spanish")
            click.echo("")
            click.echo("Pipe to LLM commands:")
            click.echo("  cat article.txt | llx template use summarize | llx prompt -m anthropic:claude-3-5-sonnet-20241022")
            click.echo("  llx template use translate --var text='Hello' --from_language=English --to_language=Spanish | llx prompt -m openai:gpt-4")