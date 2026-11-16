from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

PROMPTS_ROOT = Path(__file__).resolve().parent


def load_prompt(name: str, version: str) -> dict[str, Any]:
    """Load prompts/<name>/<version>.yaml (e.g. extract + v1 → extract/v1.yaml)."""
    path = PROMPTS_ROOT / name / f"{version}.yaml"
    if not path.is_file():
        raise FileNotFoundError(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"prompt file must be a mapping: {path}")
    for key in ("name", "version", "system", "user_template", "model", "temperature"):
        if key not in data:
            raise KeyError(f"missing {key} in {path}")
    return data


def render_user(prompt: dict[str, Any], **vars: str) -> str:
    text = prompt["user_template"]
    for key, value in vars.items():
        text = text.replace("{{" + key + "}}", value)
    return text