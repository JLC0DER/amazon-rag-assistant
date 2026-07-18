import os
from pathlib import Path

import yaml
from jinja2 import Template
from langsmith import Client

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def prompt_template_config(yaml_path: str | Path, prompt_key: str) -> Template:
    path = Path(yaml_path)

    if not path.is_absolute():
        # Resolve relative paths against the package prompts directory so this
        # works from Docker, local API, and Makefile evals at the repo root.
        candidate = PROMPTS_DIR / path.name
        path = candidate if candidate.exists() else (PROMPTS_DIR / path)

    with path.open() as file:
        config = yaml.safe_load(file)

    template_content = config["prompts"][prompt_key]
    return Template(template_content)


def _get_langsmith_client() -> Client:
    api_key = os.getenv("LANGSMITH_API_KEY")
    api_url = os.getenv("LANGSMITH_ENDPOINT") or os.getenv("LANGCHAIN_ENDPOINT")

    if not api_key or not api_url:
        raise ValueError("LANGSMITH_API_KEY and LANGSMITH_ENDPOINT must be set.")

    return Client(api_key=api_key, api_url=api_url)


def prompt_template_registry(prompt_name: str) -> Template:
    template_content = (
        _get_langsmith_client()
        .pull_prompt(prompt_name)
        .messages[0]
        .prompt.template
    )
    return Template(template_content)
