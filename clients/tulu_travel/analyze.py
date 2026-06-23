"""
Tulu Travel Search Term Analyzer
Usage: python analyze.py <search_terms.csv> [--keywords keywords.csv] [--out output.csv]
"""

import csv
import argparse
import re
import sys
import os
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from rules import (BRAND_TERMS, COMPETITORS, DIY_RESEARCH_SIGNALS, BUDGET_SIGNALS,
                   ACCOMMODATION_SIGNALS, EXCURSION_SIGNALS, FISHING_SIGNALS, SPANISH_SIGNALS,
                   TOUR_REVIEW_TERMS)

AG_STOP_WORDS = {"packages", "package", "travel", "costa", "rica", "trip", "trips",
                 "vacation", "vacations", "tours", "tour", "to", "in", "the", "a",
                 "and", "for", "of", "with", "&", "deals", "deal", "best", "all",
                 "visit", "go", "book", "booking"}

AG_SYNONYMS = {
    "romantic": "honeymoon",
    "couples": "honeymoon",
    "luxe": "luxury",
    "high end": "luxury",
    "high-end": "luxury",
    "all inclusive": "all-inclusive",
    "all-inclusive": "all-inclusive",
    "agent": "agency",
    "planner": "planning",
}

# Generic Costa Rica travel terms OK in any ad group
GENERIC_TRAVEL_TERMS = [
    "costa rica vacation", "costa rica trip", "costa rica travel",
    "costa rica package", "costa rica packages", "costa rica holiday",
    "visit costa rica", "go to costa rica", "travel to costa rica",
    "costa rica tour", "costa rica tours", "costa rica trips",
    "costa rica all inclusive", "all inclusive costa rica",
    "costa rica family", "family costa rica",
    "costa rica honeymoon", "honeymoon costa rica",
    "costa rica luxury", "luxury costa rica",
    "costa rica adventure", "adventure costa rica",
    "best vacation packages", "best packages", "best costa rica packages",
]


def contains_any(text, terms):
    t = text.lower()
    return next((term for term in terms if term in t), None)


def load_keywords(path):
    ag_themes = defaultdict(set)
    with open(path, encoding='utf-8-sig') as f:
        f.readline()
        f.readline()
        reader = csv.DictReader(f)
        for row in reader:
            camp = row.get('Campaign', '').strip().strip('"')
            ag = row.get('Ad group', '').strip().strip('"')
            kw = row.get('Keyword', '').strip().strip('"').lower()
            if not camp or camp.startswith('Total') or not ag or ag == '--' or not kw:
                continue
            # Extract tokens from the actual keyword text, not the ad group name
            kw_clean = re.sub(r'[^a-z ]', ' ', kw)
            tokens = set(kw_clean.split()) - AG_STOP_WORDS
            ag_themes[(camp, ag)].update(tokens)
    return ag_themes


def ad_group_matches_term(term_lower, ag_tokens):
    if not ag_tokens:
        return True
    # Expand term with synonyms
    expanded = term_lower
    for slang, canonical in AG_SYNONYMS.items():
        if slang in term_lower:
            expanded += ' ' + canonical
    return any(token in expanded for token in ag_tokens)


def analyze_term(term, campaign, ad_group, already_excluded, ag_themes, converted_terms=None):
    term_lower = term.lower()
    camp_lower = campaign.lower()

    if already_excluded == 'Excluded':
        return 'ALREADY EXCLUDED', 'Already added as negative', ''

    # Converted terms always win - proved themselves regardless of any rule
    if converted_terms and term.lower() in converted_terms:
        return 'OK', 'Has converted - protected from negation', ''

    matched_brand       = contains_any(term_lower, BRAND_TERMS)
    matched_competitor  = contains_any(term_lower, COMPETITORS)
    matched_diy         = contains_any(term_lower, DIY_RESEARCH_SIGNALS)
    matched_budget      = contains_any(term_lower, BUDGET_SIGNALS)
    matched_accom       = contains_any(term_lower, ACCOMMODATION_SIGNALS)
    matched_excursion   = contains_any(term_lower, EXCURSION_SIGNALS)
    matched_fishing     = contains_any(term_lower, FISHING_SIGNALS)
    matched_spanish     = contains_any(term_lower, SPANISH_SIGNALS)

    # ── BRAND campaign ────────────────────────────────────────────────────────
    if 'brand' in camp_lower:
        if matched_brand:
            return 'OK', f"Brand term: '{matched_brand}'", ''
        if matched_competitor:
            return 'ADD NEGATIVE', f"Competitor in brand campaign: '{matched_competitor}'", 'CAMPAIGN'
        return 'REVIEW', 'Non-brand term in brand campaign - check', ''

    # ── MAIN search campaign ──────────────────────────────────────────────────
    if matched_brand:
        return 'ADD NEGATIVE', 'Brand term in non-brand campaign', 'CAMPAIGN'
    if matched_competitor:
        return 'ADD NEGATIVE', f"Competitor term: '{matched_competitor}'", 'CAMPAIGN'
    if matched_spanish:
        return 'ADD NEGATIVE', f"Spanish-language search - targets US English: '{matched_spanish}'", 'CAMPAIGN'
    if matched_budget:
        return 'ADD NEGATIVE', f"Budget/cheap intent - not Tulu market: '{matched_budget}'", 'CAMPAIGN'
    if matched_diy:
        return 'ADD NEGATIVE', f"DIY research intent - low buying signal: '{matched_diy}'", 'CAMPAIGN'
    if matched_accom:
        return 'ADD NEGATIVE', f"Accommodation-only search - not a package buyer: '{matched_accom}'", 'CAMPAIGN'
    if matched_excursion:
        return 'ADD NEGATIVE', f"Short excursion intent - not multi-day package: '{matched_excursion}'", 'CAMPAIGN'
    if matched_fishing:
        return 'ADD NEGATIVE', f"Fishing-specific - separate niche: '{matched_fishing}'", 'CAMPAIGN'

    # Generic tour terms - could be buyers, keep for manual review
    if contains_any(term_lower, TOUR_REVIEW_TERMS):
        return 'REVIEW', 'Generic tour search - could be buyer, review manually', ''

    # Ad group theme check
    is_generic = contains_any(term_lower, GENERIC_TRAVEL_TERMS)
    ag_tokens = ag_themes.get((campaign, ad_group), set())
    if ag_tokens and not is_generic and not ad_group_matches_term(term_lower, ag_tokens):
        return 'ADD NEGATIVE', f"Off-theme for ad group '{ad_group}'", 'AD GROUP'

    return 'OK', 'Appears relevant - luxury package buyer intent', ''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='Search terms CSV from Google Ads')
    parser.add_argument('--keywords', default=None, help='Keywords CSV for ad group theme matching')
    parser.add_argument('--out', default='analysis_output.csv', help='Output CSV path')
    args = parser.parse_args()

    ag_themes = {}
    if args.keywords:
        ag_themes = load_keywords(args.keywords)
        print(f"Loaded {len(ag_themes)} ad groups from keyword file")
        # Debug: show tokens per ad group
        for (camp, ag), tokens in sorted(ag_themes.items()):
            print(f"  {ag:30} -> {tokens}")

    # First pass — collect all terms that have ever converted
    converted_terms = set()
    with open(args.input, encoding='utf-8-sig') as f:
        f.readline(); f.readline()
        for row in csv.DictReader(f):
            term = row.get('Search term', '').strip()
            camp = row.get('Campaign', '').strip()
            if not term or term.lower().startswith('total') or camp.lower().startswith('total'):
                continue
            try:
                convs = float(row.get('Conversions', '0') or 0)
            except:
                convs = 0
            if convs > 0:
                converted_terms.add(term.lower())

    if converted_terms:
        print(f"Converted terms (protected): {len(converted_terms)}")
        for t in sorted(converted_terms):
            print(f"  + {t}")

    rows_out = []
    counts = {'OK': 0, 'ADD NEGATIVE': 0, 'REVIEW': 0, 'ALREADY EXCLUDED': 0}

    with open(args.input, encoding='utf-8-sig') as f:
        f.readline()
        f.readline()
        reader = csv.DictReader(f)
        for row in reader:
            term = row.get('Search term', '').strip()
            campaign = row.get('Campaign', '').strip()
            ad_group = row.get('Ad group', '').strip()
            if not term or term.startswith('Total') or campaign.startswith('Total'):
                continue
            recommendation, reason, level = analyze_term(
                term, campaign, ad_group, row.get('Added/Excluded', ''), ag_themes, converted_terms
            )
            counts[recommendation] = counts.get(recommendation, 0) + 1
            rows_out.append({
                'Search term': term,
                'Campaign': campaign,
                'Ad group': ad_group,
                'Match type': row.get('Match type', ''),
                'Added/Excluded': row.get('Added/Excluded', ''),
                'Clicks': row.get('Clicks', ''),
                'Impr.': row.get('Impr.', ''),
                'Cost': row.get('Cost', ''),
                'Conversions': row.get('Conversions', ''),
                'RECOMMENDATION': recommendation,
                'NEG LEVEL': level,
                'REASON': reason,
            })

    order = {'ADD NEGATIVE': 0, 'REVIEW': 1, 'OK': 2, 'ALREADY EXCLUDED': 3}
    rows_out.sort(key=lambda r: order.get(r['RECOMMENDATION'], 9))

    fieldnames = ['Search term', 'Campaign', 'Ad group', 'Match type', 'Added/Excluded',
                  'Clicks', 'Impr.', 'Cost', 'Conversions', 'RECOMMENDATION', 'NEG LEVEL', 'REASON']

    with open(args.out, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)

    neg_rows = [r for r in rows_out if r['RECOMMENDATION'] == 'ADD NEGATIVE']
    upload_path = args.out.replace('.csv', '_upload.csv')
    seen_upload = set()
    with open(upload_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['Campaign', 'Ad group', 'Keyword', 'Type', 'Keyword match type'])
        writer.writeheader()
        for r in neg_rows:
            kw = r['Search term'].encode('ascii', 'ignore').decode('ascii').strip()
            ag = r['Ad group'] if r['NEG LEVEL'] == 'AD GROUP' else ''
            dedup_key = (r['Campaign'], ag, kw.lower())
            if not kw or dedup_key in seen_upload:
                continue
            seen_upload.add(dedup_key)
            writer.writerow({
                'Campaign': r['Campaign'],
                'Ad group': ag,
                'Keyword': kw,
                'Type': 'Negative' if r['NEG LEVEL'] == 'AD GROUP' else 'Campaign negative',
                'Keyword match type': 'Exact',
            })

    print(f"\nAnalysis complete -> {args.out}")
    print(f"Upload file    -> {upload_path}")
    print(f"  Total analyzed   : {sum(counts.values())}")
    for label in ['ADD NEGATIVE', 'REVIEW', 'OK', 'ALREADY EXCLUDED']:
        print(f"  {label:20} : {counts.get(label, 0)}")


if __name__ == '__main__':
    main()
