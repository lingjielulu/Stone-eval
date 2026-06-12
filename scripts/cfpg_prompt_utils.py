"""Utilities for loading editable CFPG prompt templates."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PromptTemplate:
    key: str
    version: str
    system: str
    user: str


PROMPT_BLOCK_RE = re.compile(
    r"<!--\s*prompt:(?P<key>[a-zA-Z0-9_]+)\s+version:(?P<version>[a-zA-Z0-9_.-]+)\s*-->\s*"
    r"```system\n(?P<system>.*?)\n```\s*"
    r"```user\n(?P<user>.*?)\n```\s*"
    r"<!--\s*/prompt\s*-->",
    re.S,
)
PLACEHOLDER_RE = re.compile(r"\{\{([a-zA-Z0-9_]+)\}\}")


def load_prompt_templates(path: Path) -> dict[str, PromptTemplate]:
    text = path.read_text(encoding="utf-8")
    templates: dict[str, PromptTemplate] = {}
    for match in PROMPT_BLOCK_RE.finditer(text):
        template = PromptTemplate(
            key=match.group("key"),
            version=match.group("version"),
            system=match.group("system").strip(),
            user=match.group("user").strip(),
        )
        templates[template.key] = template
    if not templates:
        raise ValueError(f"No prompt templates found in {path}")
    return templates


def render_template(text: str, values: dict[str, object]) -> str:
    rendered = text
    for key, value in values.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", str(value))
    missing = sorted(set(PLACEHOLDER_RE.findall(rendered)))
    if missing:
        raise ValueError(f"Missing prompt values: {', '.join(missing)}")
    return rendered


def render_messages(
    template: PromptTemplate,
    values: dict[str, object],
) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": render_template(template.system, values)},
        {"role": "user", "content": render_template(template.user, values)},
    ]
