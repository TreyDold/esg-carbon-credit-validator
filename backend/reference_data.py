"""
Reference data for the carbon credit transaction generator and validator.

These values are based on real carbon market structure (registries, project
methodologies, GWP conversion factors) so that synthetic data carries
realistic texture. Company names and transaction-level data are fully
synthetic.
"""

# Real carbon credit registries (voluntary market)
REGISTRIES = ["Verra", "Gold Standard", "ACR", "CAR", "Puro.earth"]

# Real project types / methodologies, mapped to which registries actually
# issue credits under them. This mapping is what the "registry/methodology
# mismatch" validator checks against.
PROJECT_TYPE_REGISTRY_MAP = {
    "REDD+ (VM0048)": ["Verra"],
    "Afforestation/Reforestation (VM0047)": ["Verra"],
    "Landfill Methane Capture": ["Verra", "ACR", "CAR"],
    "Improved Forest Management": ["ACR", "CAR", "Verra"],
    "Direct Air Capture": ["Puro.earth", "Gold Standard"],
    "Biochar": ["Puro.earth"],
    "Cookstove Distribution": ["Gold Standard", "Verra"],
}

PROJECT_TYPES = list(PROJECT_TYPE_REGISTRY_MAP.keys())

# Gas types and their 100-year Global Warming Potential (GWP100), AR6 values.
# CO2 is the reference gas (GWP = 1). A credit's quantity should be reported
# in CO2-equivalent terms using these factors.
GWP_FACTORS = {
    "CO2": 1,
    "CH4": 27,   # methane, AR6 fossil value (~27-30 depending on source/non-fossil)
    "N2O": 273,  # nitrous oxide, AR6 value
}

# Valid units. tCO2e is the only "correct" unit for a properly converted
# credit; tCO2 and short_ton are real units that appear in source data but
# require conversion before they're comparable to tCO2e claims.
UNITS = ["tCO2e", "tCO2", "short_ton"]

# Conversion factors to metric tons (used by the unit-conversion validator)
UNIT_TO_METRIC_TON = {
    "tCO2e": 1.0,
    "tCO2": 1.0,        # same magnitude, but NOT gas-equivalent-adjusted
    "short_ton": 0.907185,
}

# Synthetic company names (buyers / claimants) - no real companies
COMPANIES = [
    "Northwind Foods Inc.",
    "Aria Logistics Group",
    "Brightline Materials Co.",
    "Cobalt Ridge Manufacturing",
    "Verdant Grain Cooperative",
    "Halsey Industrial Partners",
    "Solace Apparel Holdings",
    "Tidewater Shipping Corp.",
]

# Plausible vintage year range for generated credits
VINTAGE_YEAR_RANGE = (2018, 2025)

# Reporting/claim years we're generating transactions for
CLAIM_YEAR_RANGE = (2023, 2026)
