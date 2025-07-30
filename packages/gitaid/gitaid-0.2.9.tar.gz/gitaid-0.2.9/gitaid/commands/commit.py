"""
A command-line tool that uses LLM to generate Git commit messages 
based on the staged changes. It analyzes the staged diff and produces a 
high-quality, concise commit message summarizing the main changes.

Requirements:
- git
- openai (Python SDK)
- OPENAI_API_KEY

Usage:
    1. Stage your changes using `git add`.
    2. Run this script.
    3. Approve or reject the suggested commit message.
"""

import subprocess
import sys
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
    Main entry point.
    """
    logger.info("🧠 Starting 'explain' command.")

    diff = get_staged_diff()

    system_prompt = (
        "You are an AI assistant that writes high-quality Git commit messages. "
        "Analyze the staged Git diff and produce a concise, clear summary of the changes."
        "Write in imperative mood (e.g., 'Fix bug', 'Add feature')."
        "Keep the message short unless additional detail is necessary for clarity."
        "Capture only the major, meaningful changes — omit trivial or stylistic edits."
        "If the commit includes multiple logical changes, list them as bullet points."
        "Follow conventional commit message style used in professional teams."
    )

    user_prompt = f"Here is a git diff of the staged changes:\n\n{diff}"
    
    try:
        from gitaid.core.llm import LLM
        llm = LLM(system_prompt)
        commit_message = llm.completion(user_prompt)

        logger.info("Successfully received commit_message from LLM.")

        print("\n💬 Suggested commit message:\n")
        print(commit_message)
        print("\nDo you want to use this commit message? (y/n): ", end="")

        if input().lower() == 'y':
            subprocess.run(["git", "commit", "-m", commit_message])
            print("✅ Commit successful.")
        else:
            print("❌ Commit aborted.")

    except click.Abort:
        logger.warning("LLM initialization aborted due to missing config or API key.")
        sys.exit(1)

    except Exception as e:
        logger.exception(f"Unexpected error while generating explanation. Error: {e}")
        click.secho("❌ An error occurred while generating the explanation.", fg="red")
        sys.exit(1)
