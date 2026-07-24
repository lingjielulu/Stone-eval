"""Validate YAML annotations for the foreshadowing/causality benchmark."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml


REQUIRED_TOP_LEVEL = {
    "metadata",
    "annotation_guide",
    "events",
    "causal_edges",
    "foreshadowing_units",
    "characters",
}
REQUIRED_METADATA = {
    "story_id",
    "title",
    "author",
    "language",
    "source_text_path",
    "source_url",
    "copyright_status",
    "genre",
    "length_level",
    "structure_type",
}
REQUIRED_EVENT = {
    "event_id",
    "story_id",
    "chapter_or_section",
    "text_span",
    "summary",
    "participants",
    "location",
    "time",
    "event_type",
    "certainty",
    "narrative_reality_level",
}
REQUIRED_EDGE = {
    "edge_id",
    "story_id",
    "source_event_id",
    "target_event_id",
    "relation_type",
    "strength",
    "evidence_text_span",
    "explanation",
}
REQUIRED_FORESHADOWING = {
    "foreshadowing_id",
    "story_id",
    "foreshadowing_text_span",
    "foreshadowing_summary",
    "foreshadowing_type",
    "trigger_event_id",
    "payoff_event_id",
    "payoff_text_span",
    "payoff_summary",
    "payoff_type",
    "confidence",
    "explanation",
}
REQUIRED_CHARACTER = {
    "character_id",
    "story_id",
    "name",
    "role",
    "stable_traits",
    "current_motivation_by_event",
}


def missing(record: dict[str, Any], required: set[str]) -> list[str]:
    return sorted(key for key in required if key not in record or record[key] in (None, ""))


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return [f"{path}: top-level document is not a mapping"]

    for key in missing(data, REQUIRED_TOP_LEVEL):
        errors.append(f"{path}: missing top-level field {key}")
    if errors:
        return errors

    metadata = data["metadata"]
    for key in missing(metadata, REQUIRED_METADATA):
        errors.append(f"{path}: metadata missing {key}")
    story_id = metadata.get("story_id")

    event_ids: set[str] = set()
    for idx, event in enumerate(data.get("events", []), start=1):
        for key in missing(event, REQUIRED_EVENT):
            errors.append(f"{path}: events[{idx}] missing {key}")
        event_id = event.get("event_id")
        if event_id in event_ids:
            errors.append(f"{path}: duplicate event_id {event_id}")
        event_ids.add(event_id)
        if event.get("story_id") != story_id:
            errors.append(f"{path}: event {event_id} story_id does not match metadata")

    edge_ids: set[str] = set()
    for idx, edge in enumerate(data.get("causal_edges", []), start=1):
        for key in missing(edge, REQUIRED_EDGE):
            errors.append(f"{path}: causal_edges[{idx}] missing {key}")
        edge_id = edge.get("edge_id")
        if edge_id in edge_ids:
            errors.append(f"{path}: duplicate edge_id {edge_id}")
        edge_ids.add(edge_id)
        if edge.get("story_id") != story_id:
            errors.append(f"{path}: edge {edge_id} story_id does not match metadata")
        for ref_key in ("source_event_id", "target_event_id"):
            if edge.get(ref_key) not in event_ids:
                errors.append(f"{path}: edge {edge_id} references unknown {ref_key}={edge.get(ref_key)}")

    foreshadowing_ids: set[str] = set()
    for idx, unit in enumerate(data.get("foreshadowing_units", []), start=1):
        for key in missing(unit, REQUIRED_FORESHADOWING):
            errors.append(f"{path}: foreshadowing_units[{idx}] missing {key}")
        unit_id = unit.get("foreshadowing_id")
        if unit_id in foreshadowing_ids:
            errors.append(f"{path}: duplicate foreshadowing_id {unit_id}")
        foreshadowing_ids.add(unit_id)
        if unit.get("story_id") != story_id:
            errors.append(f"{path}: foreshadowing {unit_id} story_id does not match metadata")
        for ref_key in ("trigger_event_id", "payoff_event_id"):
            if unit.get(ref_key) not in event_ids:
                errors.append(f"{path}: foreshadowing {unit_id} references unknown {ref_key}={unit.get(ref_key)}")

    character_ids: set[str] = set()
    for idx, character in enumerate(data.get("characters", []), start=1):
        for key in missing(character, REQUIRED_CHARACTER):
            errors.append(f"{path}: characters[{idx}] missing {key}")
        character_id = character.get("character_id")
        if character_id in character_ids:
            errors.append(f"{path}: duplicate character_id {character_id}")
        character_ids.add(character_id)
        if character.get("story_id") != story_id:
            errors.append(f"{path}: character {character_id} story_id does not match metadata")
        for state in character.get("current_motivation_by_event", []):
            if state.get("event_id") not in event_ids:
                errors.append(f"{path}: character {character_id} references unknown event_id={state.get('event_id')}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--annotations-dir", default="foreshadow/short_stories/dataset/annotations")
    args = parser.parse_args()

    files = sorted(Path(args.annotations_dir).glob("*.yaml"))
    if not files:
        print("ERROR: no annotation YAML files found")
        return 1

    all_errors: list[str] = []
    for path in files:
        all_errors.extend(validate_file(path))

    if all_errors:
        print("Validation failed:")
        for error in all_errors:
            print(f"- {error}")
        return 1

    print(f"Validation passed: {len(files)} annotation file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
