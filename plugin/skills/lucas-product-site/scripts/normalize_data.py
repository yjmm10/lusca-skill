#!/usr/bin/env python3
"""Validate product data and derive landing-page highlights.

Usage:
  python normalize_data.py INPUT.json --output highlights.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


class ValidationError(Exception):
    pass


def fail(message: str) -> None:
    raise ValidationError(message)


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"file not found: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")
    if not isinstance(data, dict):
        fail("root must be an object")
    return data


def require(obj: Any, key: str, where: str) -> Any:
    if not isinstance(obj, dict) or key not in obj:
        fail(f"missing required field '{where}.{key}'")
    return obj[key]


def check_localized(value: Any, where: str) -> None:
    if not isinstance(value, dict):
        fail(f"{where} must be an object with zh/en keys")
    for language in ("zh", "en"):
        if language not in value or not isinstance(value[language], str):
            fail(f"{where}.{language} must be a string")
        if not value[language].strip():
            fail(f"{where}.{language} is empty; add real text or an explicit example marker")


def check_date(value: Any, where: str) -> str:
    if not isinstance(value, str):
        fail(f"{where} must be a YYYY-MM-DD string")
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        fail(f"{where} is not a valid ISO date: {value}")
    return parsed.isoformat()


def validate(data: dict[str, Any]) -> None:
    if require(data, "schemaVersion", "$") != "1.0":
        fail("schemaVersion must be '1.0'")

    product = require(data, "product", "$")
    require(product, "name", "product")
    require(product, "slug", "product")
    check_localized(require(product, "tagline", "product"), "product.tagline")
    check_localized(require(product, "summary", "product"), "product.summary")

    author = require(data, "author", "$")
    require(author, "name", "author")
    check_localized(require(author, "role", "author"), "author.role")
    check_localized(require(author, "bio", "author"), "author.bio")

    metrics = require(data, "metrics", "$")
    if not isinstance(metrics, list) or not metrics:
        fail("metrics must be a non-empty array")
    metric_ids: set[str] = set()
    for index, metric in enumerate(metrics):
        where = f"metrics[{index}]"
        metric_id = str(require(metric, "id", where))
        if metric_id in metric_ids:
            fail(f"duplicate metric id: {metric_id}")
        metric_ids.add(metric_id)
        check_localized(require(metric, "label", where), f"{where}.label")
        value = require(metric, "value", where)
        if not isinstance(value, str) or not value.strip():
            fail(f"{where}.value must be a non-empty string")
        require(metric, "period", where)

    updates = require(data, "updates", "$")
    if not isinstance(updates, list):
        fail("updates must be an array")
    for index, update in enumerate(updates):
        where = f"updates[{index}]"
        require(update, "id", where)
        check_date(require(update, "date", where), f"{where}.date")
        check_localized(require(update, "title", where), f"{where}.title")
        check_localized(require(update, "summary", where), f"{where}.summary")

    features = require(data, "features", "$")
    if not isinstance(features, list):
        fail("features must be an array")
    for index, feature in enumerate(features):
        where = f"features[{index}]"
        require(feature, "id", where)
        check_localized(require(feature, "title", where), f"{where}.title")
        check_localized(require(feature, "description", where), f"{where}.description")

    check_localized(require(data, "disclaimer", "$"), "disclaimer")

    for optional_list in ("gallery", "faq"):
        if optional_list in data and not isinstance(data[optional_list], list):
            fail(f"{optional_list} must be an array when present")


def derive(data: dict[str, Any], latest_limit: int, metric_limit: int) -> dict[str, Any]:
    updates = sorted(data["updates"], key=lambda item: item["date"], reverse=True)
    metrics = sorted(
        data["metrics"],
        key=lambda item: (bool(item.get("highlight")), str(item.get("period", ""))),
        reverse=True,
    )
    features = sorted(
        data["features"],
        key=lambda item: bool(item.get("highlight")),
        reverse=True,
    )
    return {
        "schemaVersion": "1.0",
        "derivedFrom": "src/data/product.json",
        "product": {
            "name": data["product"]["name"],
            "slug": data["product"]["slug"],
            "tagline": data["product"]["tagline"],
            "summary": data["product"]["summary"],
        },
        "latest": updates[:latest_limit],
        "metrics": metrics[:metric_limit],
        "features": features[:6],
        "gallery": data.get("gallery", []),
        "faq": data.get("faq", []),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, help="Write derived highlights to this file")
    parser.add_argument("--latest", type=int, default=3)
    parser.add_argument("--metrics", type=int, default=6)
    args = parser.parse_args()

    try:
        data = load_json(args.input)
        validate(data)
        result = derive(data, args.latest, args.metrics)
        payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(payload, encoding="utf-8")
            print(f"validated {args.input}")
            print(f"wrote {args.output}")
        else:
            sys.stdout.write(payload)
        return 0
    except ValidationError as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
