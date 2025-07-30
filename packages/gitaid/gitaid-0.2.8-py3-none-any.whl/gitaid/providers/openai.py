import click

from gitaid.utils.validators import is_valid_openai_key

def prompt_openai_config():
    """
    Prompts user for OpenAI configuration and validates API key.

    Returns:
        tuple: (config dict, validated API key)
    """
    config = {
        "provider": "openai",
        "base_url": "",
        "model": click.prompt("Model name (Default option is gpt-4o-mini)", default="gpt-4o-mini", show_default=False),
        "api_version": None,
    }

    api_key = click.prompt("🔑 Enter your OpenAI API key", hide_input=True)

    while not is_valid_openai_key(api_key, "https://api.openai.com/v1"):
        click.secho("❌ Invalid OpenAI API key. Please try again.", fg="red")
        api_key = click.prompt("🔑 Enter your OpenAI API key", hide_input=True)

    return config, api_key
