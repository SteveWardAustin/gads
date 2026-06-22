"""
Campaign rules and keyword lists for Future Stars search term analysis.
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
    "camps r us",                                # specific enough — no qualifier needed
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
