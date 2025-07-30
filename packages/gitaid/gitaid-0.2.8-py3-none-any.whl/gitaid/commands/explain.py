"""
A utility script that uses LLM to analyze and explain staged Git changes.

Use case:
Ideal for developers who want a quick, AI-generated explanation of what their staged changes are doing,
e.g., for pull requests or code reviews.

Usage:
    1. Stage your changes using `git add`.
    2. Run this script.

Requirements:
    - git
    - openai (Python SDK)
    - OPENAI_API_KEY
"""
import sys
import subprocess
import click
from loguru import logger


def get_staged_diff() -> str:
    """
    Retrieves the staged Git diff from the current repository.

    Returns:
        str: The diff output as a string.

    Raises:
        SystemExit: If there are no staged changes or an error occurs while fetching the diff.
    """
    logger.debug("Attempting to retrieve staged Git diff...")
    try:
        result = subprocess.run(
            ["git", "diff", "--cached"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )

        if result.returncode != 0:
            logger.error(f"Git diff command failed: {result.stderr.strip()}")
            click.secho("❌ Failed to run git diff. Are you in a Git repo?", fg="red")
            sys.exit(1)

        if not result.stdout.strip():
            logger.warning("No staged changes found.")
            click.secho("⚠️ No staged changes found. Stage changes with `git add`.", fg="yellow")
            sys.exit(1)

        logger.info("Successfully retrieved staged Git diff.")
        return result.stdout

    except Exception as e:
        logger.exception(f"Unexpected error while getting staged diff. Error: {e}")
        click.secho("❌ Unexpected error retrieving git diff.", fg="red")
        sys.exit(1)


def main():
    """
    Main entry point of the 'explain' command.
    Uses LLM to explain the staged changes in Git.
    """
    logger.info("🧠 Starting 'explain' command.")

    diff = get_staged_diff()

    system_prompt = (
        "You are a skilled AI assistant that helps to explain code changes clearly and professionally.\n\n"
        "Given a Git diff, summarize the staged changes as a list of bullet points:\n"
        "- Group related changes under the same section when appropriate.\n"
        "- Label each major change as 'Change 1', 'Change 2', etc.\n"
        "- Focus only on what changed — do not speculate on reasons unless obvious.\n"
        "- Use precise, professional language suitable for code reviews.\n"
        "- Be concise and factual. Avoid repetition or unnecessary detail.\n"
        "- Keep the explanation brief and to the point."
    )

    user_prompt = f"Please explain the following Git diff:\n\n{diff}"

    try:
        from gitaid.core.llm import LLM
        llm = LLM(system_prompt)
        explanation = llm.completion(user_prompt)

        logger.info("Successfully received explanation from LLM.")

        print("\n🧠 Explanation of staged changes:\n")
        print(explanation)

    except click.Abort:
        logger.warning("LLM initialization aborted due to missing config or API key.")
        sys.exit(1)

    except Exception as e:
        logger.exception(f"Unexpected error while generating explanation. Error: {e}")
        click.secho("❌ An error occurred while generating the explanation.", fg="red")
        sys.exit(1)
