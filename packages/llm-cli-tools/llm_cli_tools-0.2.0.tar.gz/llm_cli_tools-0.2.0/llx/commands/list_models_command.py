import asyncio
import click
from typing import Dict, List
from llx.utils import get_provider


class ListModelsCommand:
    """Handle the list-models command logic"""
    
    def __init__(self):
        self.providers = {
            'openai': 'gpt-4',  # dummy model for initialization
            'anthropic': 'claude-3-sonnet-20240229',
            'ollama': 'llama3.2',
            'deepseek': 'deepseek-chat',
            'gemini': 'gemini-1.5-pro',
            'mistral': 'mistral-large-latest',
            'xai': 'grok-beta',
            'perplexity': 'llama-3.1-sonar-small-128k-online'
        }
    
    def execute(self, provider: str = None, output_format: str = "table"):
        """Execute list-models command"""
        
        if provider:
            # List models for specific provider
            if provider not in self.providers:
                click.echo(click.style(f"❌ Unknown provider: {provider}", fg='red'))
                click.echo(f"Available providers: {', '.join(self.providers.keys())}")
                return
            
            click.echo(click.style(f"🔍 Listing models for {provider}...", fg='cyan', bold=True))
            models = asyncio.run(self._get_models_for_provider(provider))
            
            if output_format == "json":
                self._output_json({provider: models})
            else:
                self._output_table({provider: models})
        else:
            # List models for all providers
            click.echo(click.style("🔍 Listing models for all providers...", fg='cyan', bold=True))
            all_models = asyncio.run(self._get_all_models())
            
            if output_format == "json":
                self._output_json(all_models)
            else:
                self._output_table(all_models)
    
    async def _get_models_for_provider(self, provider_name: str) -> List[str]:
        """Get models for a specific provider"""
        try:
            # Use a dummy model name to initialize the provider
            dummy_model = self.providers[provider_name]
            provider = get_provider(provider_name, dummy_model)
            models = await provider.list_models()
            return sorted(models) if models else []
        except Exception as e:
            click.echo(click.style(f"⚠️  Failed to get models for {provider_name}: {str(e)}", fg='yellow'))
            return []
    
    async def _get_all_models(self) -> Dict[str, List[str]]:
        """Get models for all providers"""
        all_models = {}
        
        for provider_name in self.providers.keys():
            models = await self._get_models_for_provider(provider_name)
            all_models[provider_name] = models
        
        return all_models
    
    def _output_table(self, models_data: Dict[str, List[str]]):
        """Output models in table format"""
        click.echo()
        
        for provider_name, models in models_data.items():
            if not models:
                click.echo(click.style(f"{provider_name.upper()}:", fg='blue', bold=True))
                click.echo(click.style("  No models available or API error", fg='yellow'))
                click.echo()
                continue
            
            click.echo(click.style(f"{provider_name.upper()} ({len(models)} models):", fg='blue', bold=True))
            
            for i, model in enumerate(models, 1):
                # Format model name with provider prefix for usage
                full_model_name = f"{provider_name}:{model}"
                click.echo(f"  {i:2d}. {model}")
                if i == 1:  # Show usage example for first model
                    click.echo(click.style(f"      Usage: llx prompt -m \"{full_model_name}\" -p \"Hello\"", dim=True))
            
            click.echo()
        
        # Show summary
        total_models = sum(len(models) for models in models_data.values())
        available_providers = len([p for p, models in models_data.items() if models])
        
        click.echo(click.style("📊 Summary:", fg='cyan', bold=True))
        click.echo(f"   Total models: {total_models}")
        click.echo(f"   Available providers: {available_providers}/{len(models_data)}")
    
    def _output_json(self, models_data: Dict[str, List[str]]):
        """Output models in JSON format"""
        import json
        
        output = {
            "providers": models_data,
            "summary": {
                "total_models": sum(len(models) for models in models_data.values()),
                "available_providers": len([p for p, models in models_data.items() if models]),
                "total_providers": len(models_data)
            }
        }
        
        click.echo(json.dumps(output, indent=2))