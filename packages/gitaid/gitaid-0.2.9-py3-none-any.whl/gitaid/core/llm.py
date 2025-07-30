import os
import keyring
import click
from loguru import logger

from gitaid.utils.config import load_config

class LLM:
    """
    A class to interact with a Large Language Model (LLM) using OpenAI or Azure OpenAI APIs.

    Handles configuration loading, API key retrieval, client instantiation, and generating responses.
    """

    def __init__(self, system_prompt: str):
        """
        Initialize the LLM client with a system prompt and load configuration.

        Args:
            system_prompt (str): The prompt used to guide the LLM's behavior.
        """
        logger.debug("Initializing LLM instance.")
        self.system_prompt = system_prompt
        self.config = self._load_config()
        self.api_key = self._get_api_key()
        self.client, self.model = None, None

    def _load_config(self) -> dict:
        """
        Load and validate configuration from YAML.

        Returns:
            dict: Configuration dictionary with necessary values.

        Raises:
            click.ClickException: If required keys are missing in the config.
        """
        logger.debug("Loading configuration.")
        cfg = load_config()

        required = ["provider", "model"]
        missing = [k for k in required if k not in cfg]
        if missing:
            logger.error(f"Missing config keys: {missing}")
            raise click.ClickException(f"Missing config keys: {', '.join(missing)}")

        # Set defaults for optional config values
        cfg["base_url"] = cfg.get("base_url", "")
        cfg["api_version"] = cfg.get("api_version", None)

        logger.debug(f"Configuration loaded: {cfg}")
        return cfg

    def _get_api_key(self) -> str:
        """
        Retrieve the API key from environment variables or OS keyring.

        Returns:
            str: The retrieved API key.

        Raises:
            click.Abort: If the API key is not found.
        """
        logger.debug("Retrieving API key.")
        key = os.getenv("OPENAI_API_KEY") or keyring.get_password("gitaid", "OPENAI_API_KEY")
        if not key:
            logger.error("OpenAI API key not found.")
            click.secho("❌ OpenAI API key not found. Run `gitaid setup`.", fg="red")
            raise click.Abort()
        logger.debug("API key successfully retrieved.")
        return key

    def _create_client(self):
        """
        Create and initialize the OpenAI-compatible client.

        Returns:
            tuple: The initialized client and model name.

        Raises:
            click.ClickException: For known errors with client initialization.
        """
        if self.client is not None:
            return self.client, self.model

        logger.debug("Creating OpenAI client.")
        try:
            from openai import OpenAI, OpenAIError
        except ImportError:
            logger.error("Missing 'openai' package.")
            raise click.ClickException("❌ Missing OpenAI package. Install it with `pip install openai`.")

        client_args = {
            "api_key": self.api_key
        }

        if self.config.get("base_url"):
            client_args["base_url"] = self.config["base_url"]

        if self.config.get("api_version"):
            client_args["default_query"] = {"api-version": self.config["api_version"]}

        try:
            self.client = OpenAI(**client_args)
            self.model = self.config["model"]
            logger.info(f"OpenAI client created with model: {self.model}")
            return self.client, self.model

        except OpenAIError as e:
            logger.error(f"OpenAIError during client initialization: {e}")
            raise click.ClickException("❌ Could not connect to OpenAI API. Check your credentials or network.")

        except Exception as e:
            logger.exception(f"Unexpected error while creating LLM client: {e}")
            raise click.ClickException("❌ Unexpected error while setting up the LLM client.")

    def completion(self, user_prompt: str) -> str:
        """
        Generate a completion response using the LLM.

        Args:
            user_prompt (str): The user's message or question to send to the LLM.

        Returns:
            str: The generated response from the LLM.

        Raises:
            click.ClickException: If there is an error during completion.
        """
        logger.info("Requesting LLM completion.")
        client, model = self._create_client()

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=500,
                temperature=0.3,
            )
            content = response.choices[0].message.content.strip()
            logger.debug(f"LLM response received: {content}")
            return content

        except Exception as e:
            logger.exception(f"Failed to generate LLM completion: {e}")
            raise click.ClickException("❌ Failed to generate a response from the LLM.")
