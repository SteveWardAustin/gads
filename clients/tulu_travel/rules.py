"""
Campaign rules for Tulu Travel — Costa Rica luxury travel packages.
Target: US buyers seeking high-end, guided, multi-day Costa Rica trips.
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
