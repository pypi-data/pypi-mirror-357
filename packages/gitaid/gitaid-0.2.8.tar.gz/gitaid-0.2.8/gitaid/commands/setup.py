import click
import keyring
from loguru import logger

from gitaid.utils.config import save_config, get_config_path
from gitaid.logs import setup_logger

PROVIDERS = {}

def main():
    """
    Entry point for the `gitaid setup` command.

    Guides the user through setting up the model provider (OpenAI, Azure, or VLLM),
    validates and stores the API key if applicable, and writes configuration to a YAML file.
    """
    # Initialize logging configuration
    setup_logger()

    logger.info("Starting GitAid setup process.")
    from gitaid.providers import openai, azure, vllm

    global PROVIDERS
    PROVIDERS = {
        '1': ("OpenAI", openai.prompt_openai_config),
        '2': ("Azure OpenAI", azure.prompt_azure_config),
        '3': ("vLLM", vllm.prompt_vllm_config),
    }

    click.secho("\n🛠️  GitAid Setup\n", bold=True)
    click.echo("GitAid requires a Large Language Model (LLM) to function. Let's set it up!\n")
    click.secho("NOTE: Currently, GitAid supports only OpenAI-compatible APIs.\n", fg="yellow", bold=True)

    try:
    
        for number, (name, _) in PROVIDERS.items():
            click.echo(f"{number}. {name}")

        # Ask for user input
        choice = click.prompt("Enter the number", type=click.Choice(PROVIDERS.keys()))
        logger.debug(f"User selected provider option: {choice} ({PROVIDERS[choice][0]})")

        # Call the correct function based on the choice
        provider_name, config_func = PROVIDERS[choice]
        logger.info(f"Prompting configuration for provider: {provider_name}")
        config, api_key = config_func()

        if api_key:
            keyring.set_password("gitaid", "OPENAI_API_KEY", api_key)
            click.secho("✅ API key validated and stored securely.\n", fg="cyan")

        save_config(config)
        config_path = get_config_path()
        logger.info(f"Configuration saved to {config_path}")
        click.secho(f"📝 Configuration saved to {config_path}\n", fg="cyan")
        
        click.secho("\n⚙️  (Optional) Enable tab-completion\n", bold=True)
        click.echo("""
    Zsh:
        eval "$(_GITAID_COMPLETE=zsh_source gitaid)"      # add to ~/.zshrc

    Bash:
        eval "$(_GITAID_COMPLETE=bash_source gitaid)"     # add to ~/.bashrc

    More info: https://pypi.org/project/gitaid/
    """)
    
    except Exception as e:
        logger.exception(f"An error occurred during setup: {e}")
        click.secho("❌ Setup failed due to an unexpected error. See logs for details.", fg="red")
        raise click.Abort()

if __name__ == "__main__":
    main()
