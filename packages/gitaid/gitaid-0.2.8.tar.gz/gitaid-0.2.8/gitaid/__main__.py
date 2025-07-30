import click
import importlib
import pkgutil
import shutil

from gitaid.logs import setup_logger
import gitaid.commands as commands


@click.group()
@click.option('--verbose', is_flag=True, help='Enable verbose debug logging')
def cli(verbose):
    """
    GitAid CLI entry point.
    Checks for dependencies before allowing subcommands to proceed.
    """
    # ✅ Initialize logging here
    setup_logger(verbose=verbose)

    # Check if Git is installed
    if shutil.which("git") is None:
        click.secho(
            "❌ Git is not installed or not found in PATH. Please install Git to use GitAid.",
            fg="red"
        )
        raise click.Abort()


def load_command_modules():
    """
    Discover all available command modules in the gitaid.commands package.

    Yields the module name (string) for each non-private, non-package Python
    module found in the gitaid.commands directory.
    """
    for _, module_name, is_pkg in pkgutil.iter_modules(commands.__path__):
        if not is_pkg and not module_name.startswith('_'):
            yield module_name


def create_command(module):
    """
    Wrap the given module's main() function as a Click command.

    Uses the module's docstring or the main() function's docstring as the
    help text for the command.
    """
    helptext = getattr(module.main, '__doc__', '') or getattr(module, '__doc__', '') or ''

    @click.command(name=module.__name__.split('.')[-1], help=helptext)
    def _cmd():
        """
        Entry point for dynamically generated command.
        Calls the main() function in the corresponding module.
        """
        return module.main()

    return _cmd


# ✅ Dynamically register all commands
for modname in load_command_modules():
    module = importlib.import_module(f"gitaid.commands.{modname}")
    cmd = create_command(module)
    cli.add_command(cmd, name=modname)


if __name__ == "__main__":
    cli()
