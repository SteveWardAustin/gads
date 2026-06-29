"""
Campaign rules for Tulu Travel — Costa Rica luxury travel packages.
Target: US buyers seeking high-end, guided, multi-day Costa Rica trips.

Key judgment calls:
- BUDGET_SIGNALS: Tulu sells premium packages ($5k+). Any cheap/discount intent is wrong market.
- EXCURSION_SIGNALS: Day trips and half-day tours are not Tulu's product. Multi-day packages only.
- ACCOMMODATION_SIGNALS: Someone searching hotels/airbnb/hostels is self-planning, not buying a package.
- SPANISH_SIGNALS: Account targets US English speakers. Spanish searches are a different audience.
- FISHING_SIGNALS: Fishing is a separate niche with its own operators. Not Tulu's offering.
- TOUR_REVIEW_TERMS: "costa rica private tours", "costa rica expeditions", "tours in costa rica" —
  generic enough that they could be package buyers. Keep as REVIEW rather than negate.
- Converted terms are always protected from negation regardless of any rule — they proved themselves.
- Ad group theme matching uses keyword TEXT tokens (not ad group name) to determine theme,
  so "Travel Agent & Agency" ad group themes come from the actual keywords in that group.
- GENERIC_TRAVEL_TERMS get a free pass on ad group theme matching — broad terms are fine anywhere.
"""

BRAND_TERMS = [
    "tulu travel", "tulutravel", "tulu costa rica",
]

COMPETITORS = [
    "kensington tours", "kensingtontours",
    "vacations costa rica", "vacationscostarica",
    "expedia",
    "enter costa rica", "entercostarica",
    "travel local", "travellocal",
    "costarica.org",
    "riu ", "riu resort", "riu hotel",
    # Other known competitors from negative list
    "aaa travel", "aaa costa rica", "aaa tours",
    "costco travel", "costco vacation",
    "abercrombie and kent",
    "adventures by disney",
    "intrepid travel",
    "g adventures",
    "nayara", "tabacon", "westin costa rica",
    "club med",
]

# DIY / research intent — person is planning themselves, not buying a package
DIY_RESEARCH_SIGNALS = [
    "itinerary", "things to do", "what to do", "places to visit",
    "best places", "where to go", "how to", "travel guide", "guide to",
    "tips for", "tourist", "must see", "must do", "top things",
    "top places", "best things", "free things", "what is", "where is",
    "when to go", "best time to visit", "weather in", "climate in",
    "map of", "cost of", "how much does", "is it safe",
    "travel tips", "things you need", "what to pack", "packing list",
    "self guided", "self-guided", "on your own", "rent a car",
    "driving in", "bus in", "getting around",
]

# Budget / cheap intent — not Tulu's market
BUDGET_SIGNALS = [
    "cheap", "cheapest", "affordable", "budget", "low cost", "low-cost",
    "inexpensive", "discount", "deal", "deals", "bargain",
    "free", "on a budget", "save money", "best price",
]

# Accommodation-only searches — not buying a package
ACCOMMODATION_SIGNALS = [
    "airbnb", "air bnb", "air b&b", "air b and b",
    "hostel", "hostels",
    "hotel only", "just hotel", "hotels in",
    "where to stay", "best hotels", "best resorts",
    "vrbo", "booking.com", "hotels.com",
]

# Short excursion intent — not multi-day packages
EXCURSION_SIGNALS = [
    "day trip", "day tour", "day trips", "day tours",
    "half day", "half-day", "excursion", "excursions",
    "one day", "1 day", "single day",
]

# Generic tour terms that could be buyers - keep as REVIEW
TOUR_REVIEW_TERMS = [
    "costa rica private tours",
    "costa rica expeditions",
    "tours in costa rica",
]

# Fishing-specific (separate niche, not main luxury package offering)
FISHING_SIGNALS = [
    "fishing", "sport fishing", "deep sea fishing", "fly fishing",
    "marlin", "fishing charter", "fishing trip",
]

# Spanish-language searches — account targets US English speakers
SPANISH_SIGNALS = [
    "todo incluido", "vuelos", "hoteles en", "paquetes", "viaje",
    "vacaciones", "precio", "barato",
]
