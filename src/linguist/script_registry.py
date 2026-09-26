"""
Agent-Linguist: Script & Text Direction Routing Registry for All 70 Pan-Indic Languages
Maps ISO 639-3 codes to:
1. HarfBuzz Script Tag (e.g., 'Deva', 'Beng', 'Taml', 'Arab', 'Olck', 'Mtei', 'Tibt', 'Guru')
2. Text Flow Direction ('ltr' vs. 'rtl')
3. Resource Tier ('Tier_A', 'Tier_B', 'Tier_C', 'Tier_D')
4. Target Synthesis Quota
"""

from typing import Dict, Any, Optional


SCRIPT_REGISTRY: Dict[str, Dict[str, Any]] = {
    # -------------------------------------------------------------------------
    # TIER A: 11 SCHEDULED MAJOR LANGUAGES (1,000,000 samples)
    # -------------------------------------------------------------------------
    "hin": {"name": "Hindi", "script": "Deva", "direction": "ltr", "tier": "Tier_A", "quota": 1000000},
    "ben": {"name": "Bengali", "script": "Beng", "direction": "ltr", "tier": "Tier_A", "quota": 1000000},
    "tam": {"name": "Tamil", "script": "Taml", "direction": "ltr", "tier": "Tier_A", "quota": 1000000},
    "tel": {"name": "Telugu", "script": "Telu", "direction": "ltr", "tier": "Tier_A", "quota": 1000000},
    "mar": {"name": "Marathi", "script": "Deva", "direction": "ltr", "tier": "Tier_A", "quota": 1000000},
    "guj": {"name": "Gujarati", "script": "Gujr", "direction": "ltr", "tier": "Tier_A", "quota": 1000000},
    "kan": {"name": "Kannada", "script": "Knda", "direction": "ltr", "tier": "Tier_A", "quota": 1000000},
    "mal": {"name": "Malayalam", "script": "Mlym", "direction": "ltr", "tier": "Tier_A", "quota": 1000000},
    "ori": {"name": "Odia", "script": "Orya", "direction": "ltr", "tier": "Tier_A", "quota": 1000000},
    "pan": {"name": "Punjabi", "script": "Guru", "direction": "ltr", "tier": "Tier_A", "quota": 1000000},
    "urd": {"name": "Urdu", "script": "Arab", "direction": "rtl", "tier": "Tier_A", "quota": 1000000},

    # -------------------------------------------------------------------------
    # TIER B: 16 MID-RESOURCE SCHEDULED & MAJOR REGIONAL (250,000 - 500,000)
    # -------------------------------------------------------------------------
    "bho": {"name": "Bhojpuri", "script": "Deva", "direction": "ltr", "tier": "Tier_B", "quota": 500000},
    "asm": {"name": "Assamese", "script": "Beng", "direction": "ltr", "tier": "Tier_B", "quota": 500000},
    "mai": {"name": "Maithili", "script": "Deva", "direction": "ltr", "tier": "Tier_B", "quota": 400000},
    "nep": {"name": "Nepali", "script": "Deva", "direction": "ltr", "tier": "Tier_B", "quota": 500000},
    "san": {"name": "Sanskrit", "script": "Deva", "direction": "ltr", "tier": "Tier_B", "quota": 400000},
    "mwr": {"name": "Rajasthani / Marwari", "script": "Deva", "direction": "ltr", "tier": "Tier_B", "quota": 400000},
    "hne": {"name": "Chhattisgarhi", "script": "Deva", "direction": "ltr", "tier": "Tier_B", "quota": 400000},
    "mag": {"name": "Magahi", "script": "Deva", "direction": "ltr", "tier": "Tier_B", "quota": 350000},
    "awa": {"name": "Awadhi", "script": "Deva", "direction": "ltr", "tier": "Tier_B", "quota": 350000},
    "bgc": {"name": "Haryanvi", "script": "Deva", "direction": "ltr", "tier": "Tier_B", "quota": 300000},
    "kok": {"name": "Konkani", "script": "Deva", "direction": "ltr", "tier": "Tier_B", "quota": 300000},
    "kas": {"name": "Kashmiri", "script": "Arab", "direction": "rtl", "tier": "Tier_B", "quota": 300000},
    "snd": {"name": "Sindhi", "script": "Arab", "direction": "rtl", "tier": "Tier_B", "quota": 300000},
    "dgo": {"name": "Dogri", "script": "Deva", "direction": "ltr", "tier": "Tier_B", "quota": 250000},
    "brx": {"name": "Bodo", "script": "Deva", "direction": "ltr", "tier": "Tier_B", "quota": 250000},
    "tcy": {"name": "Tulu", "script": "Knda", "direction": "ltr", "tier": "Tier_B", "quota": 250000},

    # -------------------------------------------------------------------------
    # TIER C: 22 LOW-RESOURCE & INDIGENOUS SCRIPTS (100,000 - 200,000)
    # -------------------------------------------------------------------------
    "sat": {"name": "Santali", "script": "Olck", "direction": "ltr", "tier": "Tier_C", "quota": 200000},
    "mni": {"name": "Manipuri (Meitei)", "script": "Mtei", "direction": "ltr", "tier": "Tier_C", "quota": 200000},
    "kha": {"name": "Khasi", "script": "Latn", "direction": "ltr", "tier": "Tier_C", "quota": 200000},
    "lus": {"name": "Mizo", "script": "Latn", "direction": "ltr", "tier": "Tier_C", "quota": 200000},
    "grt": {"name": "Garo", "script": "Latn", "direction": "ltr", "tier": "Tier_C", "quota": 150000},
    "trp": {"name": "Kokborok", "script": "Beng", "direction": "ltr", "tier": "Tier_C", "quota": 150000},
    "gbm": {"name": "Garhwali", "script": "Deva", "direction": "ltr", "tier": "Tier_C", "quota": 150000},
    "kfy": {"name": "Kumaoni", "script": "Deva", "direction": "ltr", "tier": "Tier_C", "quota": 150000},
    "bns": {"name": "Bundeli", "script": "Deva", "direction": "ltr", "tier": "Tier_C", "quota": 150000},
    "anp": {"name": "Angika", "script": "Deva", "direction": "ltr", "tier": "Tier_C", "quota": 150000},
    "mup": {"name": "Malvi", "script": "Deva", "direction": "ltr", "tier": "Tier_C", "quota": 100000},
    "noe": {"name": "Nimadi", "script": "Deva", "direction": "ltr", "tier": "Tier_C", "quota": 100000},
    "bfy": {"name": "Bagheli", "script": "Deva", "direction": "ltr", "tier": "Tier_C", "quota": 100000},
    "gon": {"name": "Gondi", "script": "Deva", "direction": "ltr", "tier": "Tier_C", "quota": 100000},
    "kru": {"name": "Kurukh", "script": "Deva", "direction": "ltr", "tier": "Tier_C", "quota": 100000},
    "hoc": {"name": "Ho", "script": "Wara", "direction": "ltr", "tier": "Tier_C", "quota": 100000},
    "unr": {"name": "Mundari", "script": "Deva", "direction": "ltr", "tier": "Tier_C", "quota": 100000},
    "hlb": {"name": "Halbi", "script": "Deva", "direction": "ltr", "tier": "Tier_C", "quota": 100000},
    "sck": {"name": "Sadri", "script": "Deva", "direction": "ltr", "tier": "Tier_C", "quota": 100000},
    "spv": {"name": "Sambalpuri", "script": "Orya", "direction": "ltr", "tier": "Tier_C", "quota": 100000},
    "lbj": {"name": "Ladakhi / Bhoti", "script": "Tibt", "direction": "ltr", "tier": "Tier_C", "quota": 100000},
    "xnr": {"name": "Kangri", "script": "Deva", "direction": "ltr", "tier": "Tier_C", "quota": 100000},

    # -------------------------------------------------------------------------
    # TIER D: 21 ENDANGERED & MICRO-CORPORA (30,000 - 75,000)
    # -------------------------------------------------------------------------
    "lep": {"name": "Lepcha", "script": "Lepc", "direction": "ltr", "tier": "Tier_D", "quota": 50000},
    "kxu": {"name": "Kui", "script": "Orya", "direction": "ltr", "tier": "Tier_D", "quota": 60000},
    "srb": {"name": "Sora", "script": "Sora", "direction": "ltr", "tier": "Tier_D", "quota": 50000},
    "bhi": {"name": "Bhili / Bhilali", "script": "Deva", "direction": "ltr", "tier": "Tier_D", "quota": 75000},
    "scl": {"name": "Shina", "script": "Arab", "direction": "rtl", "tier": "Tier_D", "quota": 50000},
    "bft": {"name": "Balti", "script": "Tibt", "direction": "ltr", "tier": "Tier_D", "quota": 50000},
    "bsk": {"name": "Burushaski", "script": "Arab", "direction": "rtl", "tier": "Tier_D", "quota": 50000},
    "nll": {"name": "Nihali", "script": "Deva", "direction": "ltr", "tier": "Tier_D", "quota": 30000},
    "nnp": {"name": "Wancho", "script": "Wcho", "direction": "ltr", "tier": "Tier_D", "quota": 35000},
    "nst": {"name": "Tangsa", "script": "Tnsa", "direction": "ltr", "tier": "Tier_D", "quota": 35000},
    "adi": {"name": "Adi", "script": "Latn", "direction": "ltr", "tier": "Tier_D", "quota": 60000},
    "apt": {"name": "Apatani", "script": "Latn", "direction": "ltr", "tier": "Tier_D", "quota": 40000},
    "mhu": {"name": "Mishmi", "script": "Latn", "direction": "ltr", "tier": "Tier_D", "quota": 35000},
    "mjw": {"name": "Karbi", "script": "Latn", "direction": "ltr", "tier": "Tier_D", "quota": 60000},
    "dis": {"name": "Dimasa", "script": "Beng", "direction": "ltr", "tier": "Tier_D", "quota": 50000},
    "tax": {"name": "Tiwa", "script": "Latn", "direction": "ltr", "tier": "Tier_D", "quota": 40000},
    "rah": {"name": "Rabha", "script": "Beng", "direction": "ltr", "tier": "Tier_D", "quota": 50000},
    "nmc": {"name": "Konyak", "script": "Latn", "direction": "ltr", "tier": "Tier_D", "quota": 50000},
    "njo": {"name": "Ao Naga", "script": "Latn", "direction": "ltr", "tier": "Tier_D", "quota": 60000},
    "njh": {"name": "Lotha Naga", "script": "Latn", "direction": "ltr", "tier": "Tier_D", "quota": 50000},
    "njm": {"name": "Angami Naga", "script": "Latn", "direction": "ltr", "tier": "Tier_D", "quota": 50000},
}


def get_language_config(iso_code: str) -> Dict[str, Any]:
    """Retrieves script, direction, tier, and quota configuration for any of the 70 target languages."""
    if iso_code not in SCRIPT_REGISTRY:
        raise ValueError(f"Unknown language ISO-639-3 code: '{iso_code}'. Registered languages: {len(SCRIPT_REGISTRY)}")
    return SCRIPT_REGISTRY[iso_code]


def get_all_languages() -> Dict[str, Dict[str, Any]]:
    """Returns complete 70-language registry."""
    return SCRIPT_REGISTRY
