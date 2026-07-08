# Copyright © 2025-2026
#
# Deterministic data-access layer for the Laptop Advisor agent network.
#
# This module has NO dependency on neuro-san or any LLM. It is the single
# source of ground truth: every fact the agent network can state must come
# from one of these functions. Keeping this layer pure makes it trivial to
# unit-test the grounding logic without a model or a running server.

import csv
import json
import os
from typing import Any, Dict, List, Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# Numeric columns that should be parsed out of the CSV as numbers, not strings.
_INT_COLS = {"price_usd", "ram_gb", "storage_gb", "battery_wh"}
_FLOAT_COLS = {"screen_in", "weight_kg"}


def _coerce(row: Dict[str, str]) -> Dict[str, Any]:
    """Coerce raw CSV strings into typed values and split tag lists."""
    out: Dict[str, Any] = dict(row)
    for col in _INT_COLS:
        out[col] = int(row[col])
    for col in _FLOAT_COLS:
        out[col] = float(row[col])
    out["use_case_tags"] = [t.strip() for t in row["use_case_tags"].split(";") if t.strip()]
    return out


def load_laptops() -> List[Dict[str, Any]]:
    """Load the laptop catalog from the local CSV."""
    path = os.path.join(DATA_DIR, "laptops.csv")
    with open(path, newline="", encoding="utf-8") as f:
        return [_coerce(row) for row in csv.DictReader(f)]


def load_reviews() -> Dict[str, Any]:
    """Load the review dataset keyed by laptop id."""
    with open(os.path.join(DATA_DIR, "reviews.json"), encoding="utf-8") as f:
        return json.load(f)


def load_policies() -> Dict[str, Any]:
    """Load the brand warranty/return/support policy dataset."""
    with open(os.path.join(DATA_DIR, "policies.json"), encoding="utf-8") as f:
        return json.load(f)


def filter_laptops(
    max_price: Optional[float] = None,
    min_ram_gb: Optional[int] = None,
    use_case: Optional[str] = None,
    max_weight_kg: Optional[float] = None,
    os_name: Optional[str] = None,
    brand: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return catalog rows matching every provided constraint.

    All arguments are optional; None means "no constraint on this field".
    Results are sorted cheapest-first so ties are deterministic.
    """
    rows = load_laptops()
    results = []
    for r in rows:
        if max_price is not None and r["price_usd"] > max_price:
            continue
        if min_ram_gb is not None and r["ram_gb"] < min_ram_gb:
            continue
        if max_weight_kg is not None and r["weight_kg"] > max_weight_kg:
            continue
        if os_name is not None and r["os"].lower() != os_name.lower():
            continue
        if brand is not None and r["brand"].lower() != brand.lower():
            continue
        if use_case is not None and use_case.lower() not in [t.lower() for t in r["use_case_tags"]]:
            continue
        results.append(r)
    return sorted(results, key=lambda r: r["price_usd"])


def get_laptop(id_or_name: str) -> Optional[Dict[str, Any]]:
    """Look up a single laptop by exact id or (case-insensitive) name."""
    key = id_or_name.strip().lower()
    for r in load_laptops():
        if r["id"].lower() == key or r["name"].lower() == key:
            return r
    return None


def get_reviews(id_or_name: str) -> Optional[Dict[str, Any]]:
    """Return the review record for a laptop, resolved by id or name."""
    laptop = get_laptop(id_or_name)
    if laptop is None:
        return None
    review = load_reviews().get(laptop["id"])
    if review is None:
        return None
    return {"id": laptop["id"], "name": laptop["name"], **review}


def get_policy(brand: str) -> Optional[Dict[str, Any]]:
    """Return the warranty/return/support policy for a brand."""
    policy = load_policies().get(brand.strip().title())
    if policy is None:
        return None
    return {"brand": brand.strip().title(), **policy}
