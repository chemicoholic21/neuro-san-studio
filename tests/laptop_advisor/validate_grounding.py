# Copyright © 2025-2026
#
# Validation for the Laptop Advisor network.
#
# This deliberately tests the DETERMINISTIC data layer (laptop_data), not the
# LLM. That is the point of a grounded network: the facts are decided by data,
# not by the model, so they can be validated exactly and repeatably — with no
# API key, no model, and no running server.
#
# Run:  python tests/laptop_advisor/validate_grounding.py
# Exit code 0 = all checks passed, 1 = a check failed.

import sys

from coded_tools.laptop_advisor import laptop_data

PASS, FAIL = "PASS", "FAIL"
_results = []


def check(name, condition, detail=""):
    _results.append((name, bool(condition), detail))


def run():
    laptops = laptop_data.load_laptops()
    reviews = laptop_data.load_reviews()
    policies = laptop_data.load_policies()

    # 1. Data loads and is non-empty.
    check("catalog loads", len(laptops) == 10, f"{len(laptops)} rows")

    # 2. Referential integrity: every laptop has a review, every reviewed id exists.
    catalog_ids = {r["id"] for r in laptops}
    check("every laptop has a review", catalog_ids <= set(reviews), catalog_ids - set(reviews))
    check("no orphan reviews", set(reviews) <= catalog_ids, set(reviews) - catalog_ids)

    # 3. Referential integrity: every laptop brand has a policy.
    brands = {r["brand"] for r in laptops}
    check("every brand has a policy", brands <= set(policies), brands - set(policies))

    # 4. Budget filter never returns anything over budget (grounding constraint).
    under_1000 = laptop_data.filter_laptops(max_price=1000)
    check("budget filter respects max_price", all(r["price_usd"] <= 1000 for r in under_1000),
          [r["name"] for r in under_1000])

    # 5. Use-case filter only returns tagged rows.
    gaming = laptop_data.filter_laptops(use_case="gaming")
    check("use_case filter returns only tagged rows",
          all("gaming" in r["use_case_tags"] for r in gaming),
          [r["name"] for r in gaming])

    # 6. Combined constraints (the core "one agent can't juggle this" scenario):
    #    portable programming laptop, <= $1200, >= 16GB RAM, <= 1.4 kg.
    combo = laptop_data.filter_laptops(max_price=1200, min_ram_gb=16, use_case="programming", max_weight_kg=1.4)
    combo_names = [r["name"] for r in combo]
    check("combined filter is correct", combo_names == ["AeroBook 14"], combo_names)

    # 7. Single lookups resolve by both id and name, case-insensitively.
    by_id = laptop_data.get_laptop("l07")
    by_name = laptop_data.get_laptop("fruit air 13")
    check("lookup by id == lookup by name", by_id == by_name and by_id is not None,
          by_id["name"] if by_id else None)

    # 8. Reviews are returned verbatim from data (spot-check a known value).
    r7 = laptop_data.get_reviews("Fruit Air 13")
    check("review rating is grounded", r7 and r7["rating"] == 4.7, r7["rating"] if r7 else None)

    # 9. Policy facts are returned verbatim (Cardinal has the 3-year warranty).
    pol = laptop_data.get_policy("Cardinal")
    check("policy warranty is grounded", pol and pol["warranty_months"] == 36,
          pol["warranty_months"] if pol else None)

    # 10. Unknown items fail closed (return None), so the agent can say "not in data"
    #     instead of hallucinating.
    check("unknown laptop returns None", laptop_data.get_laptop("Nonexistent 99") is None)
    check("unknown brand returns None", laptop_data.get_policy("NoSuchBrand") is None)

    # ---- report ----
    failed = 0
    for name, ok, detail in _results:
        tag = PASS if ok else FAIL
        line = f"[{tag}] {name}"
        if not ok and detail != "":
            line += f"  -> got: {detail}"
        print(line)
        if not ok:
            failed += 1

    print("-" * 48)
    print(f"{len(_results) - failed}/{len(_results)} checks passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run())
