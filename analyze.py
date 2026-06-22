"""
Future Stars Search Term Analyzer
Usage: python analyze.py <search_terms.csv> [--out output.csv]
"""

import csv
import sys
import argparse
from pathlib import Path
import re
from rules import (BRAND_TERMS, COMPETITORS, COMPETITORS_EXACT, COMPETITOR_NAMES,
                   CAMP_QUALIFIERS, BAD_INTENT_SIGNALS, BAD_INTENT_EXCEPTIONS,
                   FALSE_BRAND_TERMS, NEAR_BRAND_REVIEW, PORTLAND_GOOD_GEO, PORTLAND_BAD_GEO)


def contains_any(text, terms):
    t = text.lower()
    return next((term for term in terms if term in t), None)


def matches_competitor_with_qualifier(text):
    """Match competitor name + camp qualifier anywhere in the term."""
    t = text.lower()
    has_qualifier = any(q in t for q in CAMP_QUALIFIERS)
    for name in COMPETITOR_NAMES:
        if name in t:
            # Specific enough phrases don't need a qualifier
            if len(name.split()) >= 3 or name in ("camps r us", "buckleycamp"):
                return name
            # Short names need a camp qualifier alongside them
            if has_qualifier:
                return name
    return None


def contains_any_exact(text, terms):
    """Match whole-word phrases to avoid substring false positives."""
    t = text.lower()
    for term in terms:
        pattern = r'\b' + re.escape(term) + r'\b'
        if re.search(pattern, t):
            return term
    return None


def analyze_term(term, campaign, already_excluded):
    term_lower = term.lower()
    camp_lower = campaign.lower()

    # Already handled - skip
    if already_excluded == "Excluded":
        return "ALREADY EXCLUDED", "Already added as negative"

    matched_brand = contains_any(term_lower, BRAND_TERMS)
    matched_false_brand = contains_any(term_lower, FALSE_BRAND_TERMS)
    matched_near_brand = contains_any(term_lower, NEAR_BRAND_REVIEW)
    matched_competitor = contains_any(term_lower, COMPETITORS) or contains_any_exact(term_lower, COMPETITORS_EXACT)
    raw_bad_intent = contains_any(term_lower, BAD_INTENT_SIGNALS)
    is_exception = contains_any(term_lower, BAD_INTENT_EXCEPTIONS)
    matched_bad_intent = raw_bad_intent if (raw_bad_intent and not is_exception) else None

    # ── BRANDED campaign ──────────────────────────────────────────────────────
    # Use "branded" but NOT "nonbranded" to avoid routing nonbranded campaigns here
    if "branded" in camp_lower and "nonbranded" not in camp_lower and "non-branded" not in camp_lower:
        if matched_brand:
            return "OK", f"Brand term matched: '{matched_brand}'"
        if matched_near_brand:
            return "REVIEW", f"Near-brand - has converted before, review: '{matched_near_brand}'"
        if matched_false_brand:
            return "ADD NEGATIVE", f"Looks like brand but is a different camp: '{matched_false_brand}'"
        if matched_competitor:
            return "ADD NEGATIVE", f"Competitor term in branded campaign: '{matched_competitor}'"
        return "ADD NEGATIVE", "No brand signal - not relevant for branded campaign"

    # ── COMPETITORS campaign ──────────────────────────────────────────────────
    if "competitor" in camp_lower:
        if matched_brand:
            return "ADD NEGATIVE", "Own brand showing in competitor campaign"
        fuzzy_match = matches_competitor_with_qualifier(term_lower)
        if fuzzy_match or matched_competitor:
            hit = fuzzy_match or matched_competitor
            return "OK", f"Competitor matched: '{hit}'"
        return "ADD NEGATIVE", "No competitor signal - not relevant for competitors campaign"

    # ── pMax Portland ─────────────────────────────────────────────────────────
    if "pmax" in camp_lower or "portland" in camp_lower:
        bad_geo = contains_any(term_lower, PORTLAND_BAD_GEO)
        if bad_geo:
            return "ADD NEGATIVE", f"NY/LI geography in Portland campaign: '{bad_geo}'"
        if matched_competitor:
            return "ADD NEGATIVE", f"Competitor term: '{matched_competitor}'"
        if matched_brand:
            return "ADD NEGATIVE", "Brand term in pMax - should go to branded campaign"
        if matched_bad_intent:
            return "ADD NEGATIVE", f"Wrong intent signal: '{matched_bad_intent}'"
        return "OK", "Appears relevant for Portland market"

    # ── NONBRANDED campaigns (Geo Priorities + Other Geos) ───────────────────
    if "nonbranded" in camp_lower or "non-branded" in camp_lower:
        if matched_brand:
            return "ADD NEGATIVE", "Brand term in nonbranded campaign - add as negative"
        if matched_competitor:
            return "ADD NEGATIVE", f"Competitor term in nonbranded campaign: '{matched_competitor}'"
        if matched_bad_intent:
            return "ADD NEGATIVE", f"Wrong intent signal: '{matched_bad_intent}'"
        return "OK", "Appears relevant"

    # ── Unknown campaign ──────────────────────────────────────────────────────
    return "REVIEW", "Unknown campaign type - manual review needed"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Search terms CSV from Google Ads")
    parser.add_argument("--out", default="analysis_output.csv", help="Output CSV path")
    args = parser.parse_args()

    rows_out = []
    counts = {"OK": 0, "ADD NEGATIVE": 0, "REVIEW": 0, "ALREADY EXCLUDED": 0}

    with open(args.input, encoding="utf-8-sig") as f:
        # Skip Google Ads title rows (report name + date range)
        f.readline()  # "Search terms report"
        f.readline()  # date range
        reader = csv.DictReader(f)
        for row in reader:
            term = row.get("Search term", "").strip()
            campaign = row.get("Campaign", "").strip()

            # Skip summary/total rows
            if not term or term.startswith("Total") or campaign.startswith("Total"):
                continue

            recommendation, reason = analyze_term(
                term, campaign, row.get("Added/Excluded", "")
            )
            counts[recommendation] = counts.get(recommendation, 0) + 1

            rows_out.append({
                "Search term": term,
                "Campaign": campaign,
                "Ad group": row.get("Ad group", ""),
                "Match type": row.get("Match type", ""),
                "Added/Excluded": row.get("Added/Excluded", ""),
                "Clicks": row.get("Clicks", ""),
                "Impr.": row.get("Impr.", ""),
                "Cost": row.get("Cost", ""),
                "Conversions": row.get("Conversions", ""),
                "RECOMMENDATION": recommendation,
                "REASON": reason,
            })

    # Sort: ADD NEGATIVE first, then REVIEW, then OK
    order = {"ADD NEGATIVE": 0, "REVIEW": 1, "OK": 2, "ALREADY EXCLUDED": 3}
    rows_out.sort(key=lambda r: order.get(r["RECOMMENDATION"], 9))

    fieldnames = [
        "Search term", "Campaign", "Ad group", "Match type", "Added/Excluded",
        "Clicks", "Impr.", "Cost", "Conversions", "RECOMMENDATION", "REASON"
    ]

    with open(args.out, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)

    print(f"\nAnalysis complete → {args.out}")
    print(f"  Total terms analyzed : {sum(counts.values())}")
    for label in ["ADD NEGATIVE", "REVIEW", "OK", "ALREADY EXCLUDED"]:
        print(f"  {label:20} : {counts.get(label, 0)}")


if __name__ == "__main__":
    main()
