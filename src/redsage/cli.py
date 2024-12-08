import os
import click
import platform
import yaml
from typing import Optional
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from dotenv import load_dotenv, set_key
from redsage.core.agent import RedSageAgent
from redsage.core.watcher import FileWatcher
from redsage.utils.config import Config
from redsage.utils.git import GitManager
import subprocess

# Load the .env file
load_dotenv()

class RedSageCLI:
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize RedSage CLI with optional configuration path.
        """
        # Load configuration
        self.config = Config(config_path)

        # Ensure the directory is a valid Git repository
        project_root = os.getcwd()  # Assuming the project root is the current working directory

        if not os.path.isdir(os.path.join(project_root, '.git')):
            click.echo(f"No Git repository found at {project_root}.")
            create_git_repo = click.prompt("Would you like to initialize a Git repository?", type=bool, default=True)
            if create_git_repo:
                try:
                    # Initialize Git repository
                    subprocess.check_call(['git', 'init'], cwd=project_root)
                    click.echo(f"Initialized a new Git repository at {project_root}.")
                except subprocess.CalledProcessError:
                    raise ValueError(f"Failed to initialize Git repository at {project_root}. Please check your Git setup.")
            else:
                raise ValueError(f"Project is not a Git repository and Git initialization was declined.")

        # Initialize GitManager with the correct path (project root or Git root)
        self.git_ops = GitManager(self.config)

        # Initialize LLM agent
        self.agent = RedSageAgent(config=self.config)

        # Initialize file watcher
        watch_paths = self.config.get('watch.paths', ['.'])
        self.watcher = FileWatcher(paths=watch_paths)

        # Setup prompt session with command completions
        self.session = PromptSession(
            completer=WordCompleter([
                '/help', '/context', '/suggest',
                '/explain', '/diff', '/save',
                '/undo', '/switch', '/quit', '/paste', '/ask'
            ]),
            # Disable styles to prevent ANSI escape codes in the prompt
            style=None
        )

        # To store pasted content
        self.pasted_content = None

    def start_interactive_mode(self):
        """
        Start the interactive RedSage CLI session.
        """
        click.echo(click.style("Welcome to RedSage Pair Programmer!", fg="magenta"))
        click.echo(click.style("Type /help for available commands.", fg="magenta"))

        # Start file watcher in the background
        self.watcher.start_watching()

        while True:
            try:
                # Prompt user input without ANSI escape codes
                user_input = self.session.prompt('redsage> ')

                # Process command
                if user_input.startswith('/'):
                    self._handle_command(user_input)
                else:
                    # Process natural language query
                    self._process_query(user_input)

            except KeyboardInterrupt:
                continue
            except EOFError:
                break

    def _handle_command(self, command: str):
        """
        Handle user-entered commands.
        """
        command_handlers = {
            '/help': self._show_help,
            '/context': self._show_context,
            '/suggest': self._get_suggestions,
            '/explain': self._explain_code,
            '/diff': self._show_changes,
            '/save': self._save_changes,
            '/undo': self._undo_last_change,
            '/switch': self._switch_provider,
            '/quit': self._quit,
            '/paste': self._paste_content,
            '/ask': self._ask_question
        }

        cmd_parts = command.split(maxsplit=1)
        base_cmd = cmd_parts[0]
        
        handler = command_handlers.get(base_cmd)
        if handler:
            handler(cmd_parts[1] if len(cmd_parts) > 1 else None)
        else:
            click.echo(f"Unknown command: {base_cmd}. Type /help for available commands.")

    def _show_help(self, _: Optional[str] = None):
        """Show the available commands."""
        click.echo(click.style(""" 
        Available commands:
        /help      - Show available commands
        /context   - Display current conversation context
        /suggest   - Get code improvement suggestions
        /explain   - Explain recent code context
        /diff      - Show recent file changes
        /save      - Save current changes to a git branch
        /undo      - Undo the most recent change
        /switch    - Switch LLM provider
        /quit      - Quit the program
        /paste     - Paste code for further queries
        /ask       - Ask questions about pasted content
        """, fg="magenta"))

    def _paste_content(self, _: Optional[str] = None):
        """Allow user to paste content (multiline)."""
        click.echo(click.style("Please paste your content and press Enter when done.", fg="magenta"))
        content = ""
        while True:
            try:
                line = self.session.prompt('paste> ')
                if not line:
                    break
                content += line + "\n"
            except EOFError:
                break
        self.pasted_content = content
        click.echo(click.style("Content successfully pasted. You can now ask questions about it using /ask.", fg="magenta"))

    def _ask_question(self, question: Optional[str] = None):
        """Allow user to ask questions about the pasted content."""
        if self.pasted_content is None:
            click.echo("No content pasted. Use /paste to provide content first.")
            return
        if not question:
            question = click.prompt("What would you like to ask about the pasted content?")
        response = self.agent.get_suggestion(f"Answer the following question about this code: {self.pasted_content}\n\nQuestion: {question}")
        click.echo(response)

    def _show_context(self, _: Optional[str] = None):
        """Display the current context."""
        click.echo(str(self.agent.context))

    def _get_suggestions(self, query: Optional[str] = None):
        """Get code suggestions based on optional query."""
        query = query or "Provide code improvement suggestions"
        suggestion = self.agent.get_suggestion(query)
        click.echo(suggestion)

    def _explain_code(self, code: Optional[str] = None):
        """Explain the provided code or last context."""
        explanation_query = f"Explain the following code: {code}" if code else "Explain recent code context"
        explanation = self.agent.get_suggestion(explanation_query)
        click.echo(explanation)

    def _show_changes(self, _: Optional[str] = None):
        """Show recent file changes."""
        click.echo(str(self.agent.context['recent_changes']))

    def _save_changes(self, branch_name: Optional[str] = None):
        """Save current changes to a git branch."""
        result = self.git_ops.save_changes(branch_name)
        click.echo(result)

    def _undo_last_change(self, _: Optional[str] = None):
        """Undo the most recent change."""
        result = self.git_ops.undo_last_change()
        click.echo(result)

    def _switch_provider(self, new_provider: Optional[str] = None):
        """Switch the current LLM provider."""
        if not new_provider:
            click.echo("Please specify a provider (openai).")
            return
        self.agent.llm_provider = self.agent._initialize_llm_provider(new_provider)
        click.echo(f"Switched to {new_provider} provider.")

    def _quit(self, _: Optional[str] = None):
        """Exit the RedSage CLI."""
        click.echo(click.style("Exiting RedSage CLI.", fg="magenta"))
        exit()

    def _process_query(self, query: str):
        """Process natural language query."""
        result = self.agent.get_suggestion(query)
        click.echo(result)

@click.group()
def main():
    """
    Main entry point for RedSage CLI.
    """
    pass

@main.command()
@click.option('--config', default=None, help='Path to configuration file')
def init(config):
    """
    Initialize the RedSage program. 
    """
    click.echo("Initializing RedSage...")
    default_config_path = config or os.path.join(os.getcwd(), 'redsage.yaml')
    if os.path.exists(default_config_path):
        click.echo(f"Using existing configuration file at {default_config_path}")
    else:
        click.echo(f"Configuration file not found at {default_config_path}. Please create one.")

@main.command()
def start():
    """
    Start the RedSage program.
    """
    click.echo("Starting RedSage...")
    cli = RedSageCLI()
    cli.start_interactive_mode()

if __name__ == '__main__':
    main()
