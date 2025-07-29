import asyncio
import click
import sys
from abc import ABC
from datetime import datetime
from llx.utils import get_provider

class ChatCommand(ABC):
    """Handle the interactive chat command logic"""
    
    def __init__(self, provider: str, model: str):
        self.provider = provider
        self.model = model
        self.client = get_provider(provider, model)
        self.conversation_history = []

    def _print_welcome(self):
        click.echo()
        click.echo(click.style("┌" + "─" * 78 + "┐", fg='blue'))
        click.echo(click.style("│", fg='blue') + click.style(f" LLX Chat - {self.provider}:{self.model}".center(78), fg='cyan', bold=True) + click.style("│", fg='blue'))
        click.echo(click.style("├" + "─" * 78 + "┤", fg='blue'))
        click.echo(click.style("│", fg='blue') + " Type your message and press Enter. Use '/help' for commands, '/bye' to exit. " + click.style("│", fg='blue'))
        click.echo(click.style("└" + "─" * 78 + "┘", fg='blue'))
        click.echo()

    def _print_help(self):
        click.echo()
        click.echo(click.style("Available commands:", fg='yellow', bold=True))
        click.echo(click.style("  /help", fg='cyan') + "    - Show this help message")
        click.echo(click.style("  /bye", fg='cyan') + "     - Exit the chat")
        click.echo(click.style("  /clear", fg='cyan') + "   - Clear conversation history")
        click.echo(click.style("  /history", fg='cyan') + " - Show conversation history")
        click.echo()

    def _print_user_prompt(self):
        timestamp = datetime.now().strftime("%H:%M")
        click.echo(click.style(f"[{timestamp}] ", fg='bright_black') + click.style("You", fg='blue', bold=True), nl=False)
        click.echo(click.style(" ▶ ", fg='bright_blue'), nl=False)

    async def _print_stream(self, stream):
        timestamp = datetime.now().strftime("%H:%M")
        click.echo(click.style(f"[{timestamp}] ", fg='bright_black') + click.style("Assistant", fg='green', bold=True), nl=False)
        click.echo(click.style(" ▶ ", fg='bright_green'), nl=False)
        
        response_text = ""
        async for text_chunk in stream:
            click.echo(text_chunk, nl=False)
            response_text += text_chunk
            sys.stdout.flush()
        
        click.echo()
        click.echo()
        return response_text

    def _show_history(self):
        if not self.conversation_history:
            click.echo(click.style("No conversation history yet.", fg='yellow'))
            return
        
        click.echo(click.style("\nConversation History:", fg='yellow', bold=True))
        click.echo(click.style("─" * 50, fg='yellow'))
        
        for i, (user_msg, assistant_msg) in enumerate(self.conversation_history, 1):
            click.echo(click.style(f"{i}. You: ", fg='blue', bold=True) + user_msg[:100] + ("..." if len(user_msg) > 100 else ""))
            click.echo(click.style("   Assistant: ", fg='green', bold=True) + assistant_msg[:100] + ("..." if len(assistant_msg) > 100 else ""))
            click.echo()

    def execute(self):
        self._print_welcome()
        
        while True:
            try:
                self._print_user_prompt()
                user_input = input().strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['/bye', '/exit', '/quit']:
                    click.echo(click.style("\n👋 Goodbye! Thanks for chatting.", fg='cyan'))
                    break
                elif user_input.lower() == '/help':
                    self._print_help()
                    continue
                elif user_input.lower() == '/clear':
                    self.conversation_history.clear()
                    click.echo(click.style("✨ Conversation history cleared.", fg='green'))
                    click.echo()
                    continue
                elif user_input.lower() == '/history':
                    self._show_history()
                    continue
                
                try:
                    # Pass conversation history only for Ollama providers
                    if self.provider.lower() == 'ollama':
                        stream = self.client.invoke(user_input, conversation_history=self.conversation_history)
                    else:
                        stream = self.client.invoke(user_input)
                    
                    response = asyncio.run(self._print_stream(stream))
                    self.conversation_history.append((user_input, response))
                except Exception as e:
                    click.echo(click.style(f"❌ Error: {str(e)}", fg='red'))
                    click.echo()
                    
            except (EOFError, KeyboardInterrupt):
                click.echo(click.style("\n\n👋 Goodbye! Thanks for chatting.", fg='cyan'))
                break
