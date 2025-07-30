import click

from gitaid.utils.validators import is_valid_url

def prompt_vllm_config():
    """
    Prompts user for vLLM (custom or local inference server) configuration.

    Returns:
        tuple: (config dict, validated API key or None)
    """
    base_url = click.prompt(
        "vLLM Base URL (e.g. http://localhost:8000/v1)",
        default="http://localhost:8000/v1",  # Default URL for vLLM
        show_default = False
    )
    
    while not is_valid_url(base_url):
        click.secho("❌ Invalid URL. Use http/https format.", fg="red")
        base_url = click.prompt(
            "vLLM Base URL (e.g. http://localhost:8000/v1)",
            default="http://localhost:8000/v1",
            show_default = False  # Default URL again if user re-enters
        )

    model = click.prompt("Model name (e.g. Qwen/Qwen2.5-1.5B-Instruct)",
        default="Qwen/Qwen2.5-1.5B-Instruct",
        show_default = False               
        )

    # Optional: Prompt for API key if required
    api_key = click.prompt("🔑 Enter your vLLM API key", hide_input=True, default="EMPTY")
    
    config = {
        "provider": "vllm",
        "base_url": base_url,
        "model": model,
    }

    return config, api_key