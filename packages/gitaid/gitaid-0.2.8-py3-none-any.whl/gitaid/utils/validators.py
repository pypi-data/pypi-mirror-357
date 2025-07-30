from urllib.parse import urlparse
import requests
import openai

def is_valid_url(url):
    """
    Check if the provided URL is valid (http or https).
    """
    parsed = urlparse(url)
    return all([parsed.scheme in ("http", "https"), parsed.netloc])


def is_valid_openai_key(api_key, base_url):
    """
    Validate a regular OpenAI key by calling the /models endpoint.

    Args:
        api_key (str): The API key to validate.
        base_url (str): OpenAI's base URL.

    Returns:
        bool: True if valid, False otherwise.
    """
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = requests.get(f"{base_url}/models", headers=headers, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def is_valid_azure_key(api_key, base_url, api_version, model):
    """
    Validate an Azure OpenAI key by listing deployments.

    Args:
        api_key (str): Azure OpenAI API key.
        base_url (str): Azure OpenAI endpoint (e.g., https://my-resource.openai.azure.com).
        api_version (str): API version string.

    Returns:
        bool: True if the key is valid, False otherwise.
    """
    try:
        client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url,
            default_query={"api-version": api_version},
        )

        # Make a minimal test call
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": "ping"}, {"role": "user", "content": "ping"}],
            max_tokens=1
        )

        return bool(response.choices)
    except openai.OpenAIError:
        return False
    