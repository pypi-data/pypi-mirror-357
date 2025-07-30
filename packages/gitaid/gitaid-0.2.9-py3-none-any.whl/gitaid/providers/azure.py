import click

from gitaid.utils.validators import is_valid_azure_key, is_valid_url

def prompt_azure_config():
    """
    Prompts user for Azure OpenAI configuration and validates API key.

    Returns:
        tuple: (config dict, validated API key)
    """
    base_root = click.prompt("What is your Azure endpoint (URL)? (e.g. https://myresource.azure.com)")
    while not is_valid_url(base_root):
        click.secho("❌ Invalid URL. Use http/https format.", fg="red")
        base_root = click.prompt("What is your Azure endpoint (URL)?")

    deployment_name = click.prompt("Deployment name (Azure)")

    api_version = click.prompt(
        "API version (leave blank for default '2024-07-01-preview')",
        default="2024-07-01-preview",
        show_default=False,
    )

    full_base_url = f"{base_root}/openai/deployments/{deployment_name}"

    config = {
        "provider": "azure",
        "base_url": full_base_url,
        "model": deployment_name,
        "api_version": api_version if api_version else "2024-07-01-preview",
    }

    api_key = click.prompt("🔑 Enter your Azure API key", hide_input=True)

    while not is_valid_azure_key(api_key, config["base_url"], config["api_version"], config["model"]):
        click.secho("❌ Invalid Azure API key or endpoint. Try again.", fg="red")
        api_key = click.prompt("🔑 Enter your Azure API key", hide_input=True)

    return config, api_key