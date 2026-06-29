"""
Campaign rules and keyword lists for Future Stars search term analysis.
Client: Future Stars Summer Camps (fscamps.com) — youth sports day camps, Long Island NY + Portland ME.

Key judgment calls:
- BAD_INTENT_EXCEPTIONS: "purchase" excluded from buy/shop signals because "SUNY Purchase" is a
  college that legitimately runs camps. Adding "purchase" as a signal caused false positives.
- COMPETITORS_EXACT ["camp w"]: Uses word-boundary regex matching instead of substring, because
  "camp w" substring-matched "westchester" and similar words — moved out of COMPETITORS list.
- COMPETITOR_NAMES: Short/ambiguous names (buckley, hofstra, oasis, etc.) require a CAMP_QUALIFIER
  word alongside them. "Hofstra" alone could be the university; "hofstra camp" is a competitor.
  Long phrases (3+ words, or known full names like "camps r us") match without a qualifier.
- FALSE_BRAND_TERMS: Terms that look like Future Stars branding but aren't (e.g. "future all stars",
  "future soccer stars") — negate from branded campaign.
- NEAR_BRAND_REVIEW: "rising stars" variants have converted before, so keep as REVIEW not negative.
- PORTLAND_BAD_GEO: pMax Portland campaign should stay in ME. LI/NY geography terms are negated
  at campaign level since those searches should go to the LI-targeted nonbranded campaigns.
- AG_STOP_WORDS: Strip noise words from keyword tokens so ad group theme matching isn't diluted
  by words like "camp", "summer", "kids" that appear in every ad group.
- AG_SYNONYMS: Sport slang mapped to canonical names so "lax camp" matches Lacrosse Camps ad group.
- Converted terms are always protected from negation regardless of any rule.
"""

BRAND_TERMS = [
    "future stars", "future star", "fscamps", "fscamp", "fs camps", "fs summer camp",
    "future stars camps", "future stars camp", "future stars summer camp",
    "future stars summer camps", "futurestars", "fscamps.com",
]

# Near-brand terms that are NOT Future Stars — negate from branded campaign
FALSE_BRAND_TERMS = [
    "future all stars", "future soccer stars", "fugstars",
]

# Near-brand terms to keep as REVIEW (converted at least once)
NEAR_BRAND_REVIEW = [
    "rising stars summer camp", "rising stars camp",
]

# Camp-related qualifier words — a competitor name must appear alongside one of these
CAMP_QUALIFIERS = [
    "camp", "camps", "summer", "day camp", "summer camp", "summer camps",
    "day camps", "program", "programs", "academy",
]

# Competitor name tokens — must appear WITH a camp qualifier to be a valid match
COMPETITOR_NAMES = [
    "buckley", "buckleycamp",
    "driftwood",
    "hofstra",
    "kenwal",
    "luhi",
    "oasis",
    "pierce",
    "shibley",
    "woodbury",
    "long island sports hub", "li sports hub",  # specific enough — no qualifier needed
    "sports hub long island", "the hub syosset", "sports hub",  # variants of LI Sports Hub
    "camps r us", "camp r us", "campsrus", "camprus", "camps rus", "camp rus",  # misspellings
    "camp w day camp",                           # full phrase — no qualifier needed
]

# Fallback exact-match list for short/ambiguous names needing full phrase
COMPETITORS_EXACT = [
    "camp w",
]

# Legacy list kept for nonbranded campaign checks (full phrases only)
COMPETITORS = [
    "long island sports hub", "li sports hub",
    "hofstra camp", "hofstra summer camp", "hofstra summer camps",
    "oasis summer camp", "oasis day camp", "oasis camp",
    "driftwood camp", "driftwood day camp",
    "camp w day camp",
    "shibley summer camp", "shibley day camp",
    "kenwal day camp", "kenwal camp",
    "pierce day camp", "pierce summer camp",
    "luhi summer camp", "luhi camp", "luhi summer camps",
    "camps r us", "camps r us long island",
    "buckley camp", "buckleycamp", "buckleycamp.com",
    "woodbury summer camp", "woodbury day camp",
]

# Generic camp terms that are OK in any ad group regardless of sport theme
GENERIC_CAMP_TERMS = [
    "summer camp", "day camp", "summer camps", "day camps",
    "camp near me", "camps near me", "kids camp", "kids camps",
    "camp for kids", "camps for kids", "youth camp", "youth camps",
    "rec camp", "recreation camp", "sport camp", "sports camp",
    "sports camps", "summer program", "summer programs",
]

# Known false positives — terms that contain bad-intent words but are actually OK
BAD_INTENT_EXCEPTIONS = [
    "suny purchase", "purchase college", "purchase camp", "purchase day camp",
    "purchase sports", "summer workshops",
]

# Terms that suggest wrong intent for nonbranded campaigns
BAD_INTENT_SIGNALS = [
    # drills / coaching content
    "drills", "how to", "tips for", "tutorial", "technique",
    "training plan", "workout", "fitness plan",
    # equipment / gear
    "equipment", "gear", "cleats", "uniform", "jersey", "ball size",
    "what size", "best ball", "buy", "shop",
    # "purchase" excluded — too many false positives with "SUNY Purchase"
    # adult / recreational leagues
    "adult league", "adult soccer", "adult basketball", "adult baseball",
    "men's league", "women's league", "recreational league",
    # informational / non-camp
    "rules of", "history of", "wikipedia",
    # sleepaway / overnight (Future Stars is day camp)
    "sleepaway", "overnight camp", "sleep away",
    # jobs
    "jobs", "hiring", "employment", "career", "counselor job",
]

# Geography signals — pMax Portland should stay in ME/Portland area
PORTLAND_GOOD_GEO = ["portland", "maine", "me "]
PORTLAND_BAD_GEO = [
    "long island", "li ", " ny", "new york", "nassau", "suffolk",
    "farmingdale", "westbury", "garden city", "hicksville", "massapequa",
    "commack", "smithtown", "hauppauge", "melville", "syosset",
]
