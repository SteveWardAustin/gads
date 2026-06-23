"""
Future Stars Search Term Analyzer
Usage: python analyze.py <search_terms.csv> [--keywords keywords.csv] [--out output.csv]
"""

import csv
import argparse
import re
from collections import defaultdict
from rules import (BRAND_TERMS, COMPETITORS, COMPETITORS_EXACT, COMPETITOR_NAMES,
                   CAMP_QUALIFIERS, BAD_INTENT_SIGNALS, BAD_INTENT_EXCEPTIONS,
                   FALSE_BRAND_TERMS, NEAR_BRAND_REVIEW, PORTLAND_GOOD_GEO, PORTLAND_BAD_GEO,
                   GENERIC_CAMP_TERMS)

# Words that don't define an ad group's theme (stripped when extracting theme tokens)
AG_STOP_WORDS = {"camps", "camp", "sports", "sport", "summer", "day", "youth", "kids", "li"}

# Slang synonyms mapped to canonical sport words used in ad group names
AG_SYNONYMS = {
    "lax": "lacrosse",
    "hoops": "basketball",
    "bball": "basketball",
    "futbol": "soccer",
    "footy": "soccer",
    "gridiron": "football",
    "hardball": "baseball",
}


def load_keywords(path):
    """
    Build a dict: (campaign, ad_group) -> set of theme tokens extracted from the ad group name.
    We use the ad group NAME as the theme signal (e.g. "Basketball Camps" -> {"basketball"}).
    """
    ag_themes = defaultdict(set)
    with open(path, encoding="utf-8-sig") as f:
        f.readline()  # report title
        f.readline()  # date range
        reader = csv.DictReader(f)
        for row in reader:
            camp = row.get("Campaign", "").strip().strip('"')
            ag = row.get("Ad group", "").strip().strip('"')
            if not camp or camp.startswith("Total") or not ag or ag == "--":
                continue
            # Extract meaningful tokens from the ad group name
            tokens = set(re.sub(r"[^a-z ]", "", ag.lower()).split()) - AG_STOP_WORDS
            ag_themes[(camp, ag)].update(tokens)
    return ag_themes


def contains_any(text, terms):
    t = text.lower()
    return next((term for term in terms if term in t), None)


def matches_competitor_with_qualifier(text):
    """Match competitor name + camp qualifier anywhere in the term."""
    t = text.lower()
    has_qualifier = any(q in t for q in CAMP_QUALIFIERS)
    for name in COMPETITOR_NAMES:
        if name in t:
            if len(name.split()) >= 3 or name in ("camps r us", "buckleycamp"):
                return name
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


def ad_group_matches_term(term_lower, ag_tokens):
    """Return True if the search term contains at least one theme token from the ad group."""
    if not ag_tokens:
        return True  # no theme data, don't flag
    # Expand term with synonyms so e.g. "lax" matches "lacrosse" ad group token
    expanded = term_lower
    for slang, canonical in AG_SYNONYMS.items():
        if slang in term_lower.split():
            expanded += " " + canonical
    return any(token in expanded for token in ag_tokens)


def neg_level(reason_type, camp_lower, ad_group, ag_themes):
    """
    Determine where to add the negative keyword.
    ACCOUNT  - universally bad intent regardless of campaign
    CAMPAIGN - wrong for this campaign but potentially ok elsewhere
    AD GROUP - wrong for this ad group's theme but ok in the campaign
    """
    if reason_type == "bad_intent":
        return "ACCOUNT"
    if reason_type == "ad_group_mismatch":
        return "AD GROUP"
    return "CAMPAIGN"


def analyze_term(term, campaign, ad_group, already_excluded, ag_themes, converted_terms=None):
    term_lower = term.lower()
    camp_lower = campaign.lower()

    if already_excluded == "Excluded":
        return "ALREADY EXCLUDED", "Already added as negative", ""

    # Converted terms always win - proved themselves regardless of any rule
    if converted_terms and term.lower() in converted_terms:
        return "OK", "Has converted - protected from negation", ""

    matched_brand = contains_any(term_lower, BRAND_TERMS)
    matched_false_brand = contains_any(term_lower, FALSE_BRAND_TERMS)
    matched_near_brand = contains_any(term_lower, NEAR_BRAND_REVIEW)
    matched_competitor = contains_any(term_lower, COMPETITORS) or contains_any_exact(term_lower, COMPETITORS_EXACT)
    raw_bad_intent = contains_any(term_lower, BAD_INTENT_SIGNALS)
    is_exception = contains_any(term_lower, BAD_INTENT_EXCEPTIONS)
    matched_bad_intent = raw_bad_intent if (raw_bad_intent and not is_exception) else None

    # ── BRANDED campaign ──────────────────────────────────────────────────────
    if "branded" in camp_lower and "nonbranded" not in camp_lower and "non-branded" not in camp_lower:
        if matched_brand:
            return "OK", f"Brand term matched: '{matched_brand}'", ""
        if matched_near_brand:
            return "REVIEW", f"Near-brand - has converted before, review: '{matched_near_brand}'", ""
        if matched_false_brand:
            return "ADD NEGATIVE", f"Looks like brand but is a different camp: '{matched_false_brand}'", "CAMPAIGN"
        if matched_competitor:
            return "ADD NEGATIVE", f"Competitor term in branded campaign: '{matched_competitor}'", "CAMPAIGN"
        return "ADD NEGATIVE", "No brand signal - not relevant for branded campaign", "CAMPAIGN"

    # ── COMPETITORS campaign ──────────────────────────────────────────────────
    if "competitor" in camp_lower:
        if matched_brand:
            return "ADD NEGATIVE", "Own brand showing in competitor campaign", "CAMPAIGN"
        fuzzy_match = matches_competitor_with_qualifier(term_lower)
        if fuzzy_match or matched_competitor:
            hit = fuzzy_match or matched_competitor
            return "OK", f"Competitor matched: '{hit}'", ""
        return "ADD NEGATIVE", "No competitor signal - not relevant for competitors campaign", "CAMPAIGN"

    # ── pMax Portland ─────────────────────────────────────────────────────────
    if "pmax" in camp_lower or "portland" in camp_lower:
        bad_geo = contains_any(term_lower, PORTLAND_BAD_GEO)
        if bad_geo:
            return "ADD NEGATIVE", f"NY/LI geography in Portland campaign: '{bad_geo}'", "CAMPAIGN"
        if matched_competitor:
            return "ADD NEGATIVE", f"Competitor term: '{matched_competitor}'", "CAMPAIGN"
        if matched_brand:
            return "ADD NEGATIVE", "Brand term in pMax - should go to branded campaign", "CAMPAIGN"
        if matched_bad_intent:
            return "ADD NEGATIVE", f"Wrong intent signal: '{matched_bad_intent}'", "ACCOUNT"
        return "OK", "Appears relevant for Portland market", ""

    # ── NONBRANDED campaigns (Geo Priorities + Other Geos) ───────────────────
    if "nonbranded" in camp_lower or "non-branded" in camp_lower:
        if matched_brand:
            return "ADD NEGATIVE", "Brand term in nonbranded campaign - add as negative", "CAMPAIGN"
        if matched_competitor:
            return "ADD NEGATIVE", f"Competitor term in nonbranded campaign: '{matched_competitor}'", "CAMPAIGN"
        if matched_bad_intent:
            return "ADD NEGATIVE", f"Wrong intent signal: '{matched_bad_intent}'", "ACCOUNT"
        # Check ad group theme match — skip if it's a generic camp term (fine anywhere)
        is_generic = contains_any(term_lower, GENERIC_CAMP_TERMS)
        ag_tokens = ag_themes.get((campaign, ad_group), set())
        if ag_tokens and not is_generic and not ad_group_matches_term(term_lower, ag_tokens):
            return "ADD NEGATIVE", f"Off-theme for ad group '{ad_group}'", "AD GROUP"
        return "OK", "Appears relevant", ""

    # ── Unknown campaign ──────────────────────────────────────────────────────
    return "REVIEW", "Unknown campaign type - manual review needed", ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Search terms CSV from Google Ads")
    parser.add_argument("--keywords", default=None, help="Keywords CSV for ad group theme matching")
    parser.add_argument("--out", default="analysis_output.csv", help="Output CSV path")
    args = parser.parse_args()

    ag_themes = {}
    if args.keywords:
        ag_themes = load_keywords(args.keywords)
        print(f"Loaded {len(ag_themes)} ad groups from keyword file")

    # First pass — collect all terms that have ever converted
    converted_terms = set()
    with open(args.input, encoding="utf-8-sig") as f:
        f.readline()
        f.readline()
        for row in csv.DictReader(f):
            term = row.get("Search term", "").strip()
            camp = row.get("Campaign", "").strip()
            if not term or term.lower().startswith("total") or camp.lower().startswith("total"):
                continue
            try:
                convs = float(row.get("Conversions", "0") or 0)
            except:
                convs = 0
            if convs > 0:
                converted_terms.add(term.lower())

    if converted_terms:
        print(f"Converted terms (protected): {len(converted_terms)}")
        for t in sorted(converted_terms):
            print(f"  + {t}")

    rows_out = []
    counts = {"OK": 0, "ADD NEGATIVE": 0, "REVIEW": 0, "ALREADY EXCLUDED": 0}

    with open(args.input, encoding="utf-8-sig") as f:
        f.readline()  # report title
        f.readline()  # date range
        reader = csv.DictReader(f)
        for row in reader:
            term = row.get("Search term", "").strip()
            campaign = row.get("Campaign", "").strip()
            ad_group = row.get("Ad group", "").strip()

            if not term or term.startswith("Total") or campaign.startswith("Total"):
                continue

            recommendation, reason, level = analyze_term(
                term, campaign, ad_group, row.get("Added/Excluded", ""), ag_themes, converted_terms
            )
            counts[recommendation] = counts.get(recommendation, 0) + 1

            rows_out.append({
                "Search term": term,
                "Campaign": campaign,
                "Ad group": ad_group,
                "Match type": row.get("Match type", ""),
                "Added/Excluded": row.get("Added/Excluded", ""),
                "Clicks": row.get("Clicks", ""),
                "Impr.": row.get("Impr.", ""),
                "Cost": row.get("Cost", ""),
                "Conversions": row.get("Conversions", ""),
                "RECOMMENDATION": recommendation,
                "NEG LEVEL": level,
                "REASON": reason,
            })

    order = {"ADD NEGATIVE": 0, "REVIEW": 1, "OK": 2, "ALREADY EXCLUDED": 3}
    rows_out.sort(key=lambda r: order.get(r["RECOMMENDATION"], 9))

    fieldnames = [
        "Search term", "Campaign", "Ad group", "Match type", "Added/Excluded",
        "Clicks", "Impr.", "Cost", "Conversions", "RECOMMENDATION", "NEG LEVEL", "REASON"
    ]

    with open(args.out, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)

    neg_rows = [r for r in rows_out if r["RECOMMENDATION"] == "ADD NEGATIVE"]
    upload_path = args.out.replace(".csv", "_upload.csv")
    seen_upload = set()
    with open(upload_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["Campaign", "Ad group", "Keyword", "Type", "Keyword match type"])
        writer.writeheader()
        for r in neg_rows:
            kw = r["Search term"].encode("ascii", "ignore").decode("ascii").strip()
            ag = r["Ad group"] if r["NEG LEVEL"] == "AD GROUP" else ""
            dedup_key = (r["Campaign"], ag, kw.lower())
            if not kw or dedup_key in seen_upload:
                continue
            seen_upload.add(dedup_key)
            writer.writerow({
                "Campaign": r["Campaign"],
                "Ad group": ag,
                "Keyword": kw,
                "Type": "Negative" if r["NEG LEVEL"] == "AD GROUP" else "Campaign negative",
                "Keyword match type": "Exact",
            })

    print(f"\nAnalysis complete -> {args.out}")
    print(f"Upload file    -> {upload_path}")
    print(f"  Total analyzed   : {sum(counts.values())}")
    for label in ["ADD NEGATIVE", "REVIEW", "OK", "ALREADY EXCLUDED"]:
        print(f"  {label:20} : {counts.get(label, 0)}")


if __name__ == "__main__":
    main()
