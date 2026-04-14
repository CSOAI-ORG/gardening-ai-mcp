"""
Gardening AI MCP Server - Horticulture Intelligence
Built by MEOK AI Labs | https://meok.ai

Plant identification, watering schedules, soil analysis,
companion planting, and pest diagnosis.
"""


import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import time
from datetime import datetime, timezone
from typing import Optional

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "gardening-ai")

# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------
_RATE_LIMITS = {"free": {"requests_per_hour": 60}, "pro": {"requests_per_hour": 5000}}
_request_log: list[float] = []
_tier = "free"


def _check_rate_limit() -> bool:
    now = time.time()
    _request_log[:] = [t for t in _request_log if now - t < 3600]
    if len(_request_log) >= _RATE_LIMITS[_tier]["requests_per_hour"]:
        return False
    _request_log.append(now)
    return True


# ---------------------------------------------------------------------------
# Plant database
# ---------------------------------------------------------------------------
_PLANTS: dict[str, dict] = {
    "tomato": {
        "name": "Tomato", "scientific": "Solanum lycopersicum", "type": "vegetable", "family": "Solanaceae",
        "sun": "full_sun", "water_needs": "moderate", "hardiness_zone": (3, 11),
        "soil_ph": (6.0, 6.8), "soil_type": "loamy", "spacing_cm": 60,
        "days_to_harvest": (60, 85), "planting_depth_cm": 1.5,
        "companions": ["basil", "carrot", "parsley", "marigold"],
        "avoid_near": ["brassicas", "fennel", "walnut"],
        "common_pests": ["aphids", "tomato_hornworm", "whitefly"],
        "common_diseases": ["blight", "blossom_end_rot", "fusarium_wilt"],
        "watering_frequency_days": 2, "fertilizer": "balanced 10-10-10 every 2 weeks",
    },
    "basil": {
        "name": "Basil", "scientific": "Ocimum basilicum", "type": "herb", "family": "Lamiaceae",
        "sun": "full_sun", "water_needs": "moderate", "hardiness_zone": (4, 10),
        "soil_ph": (6.0, 7.0), "soil_type": "well_drained", "spacing_cm": 25,
        "days_to_harvest": (50, 75), "planting_depth_cm": 0.5,
        "companions": ["tomato", "pepper", "oregano"],
        "avoid_near": ["sage", "rue"],
        "common_pests": ["aphids", "japanese_beetles", "slugs"],
        "common_diseases": ["downy_mildew", "fusarium_wilt"],
        "watering_frequency_days": 2, "fertilizer": "light, half-strength liquid every 4 weeks",
    },
    "rose": {
        "name": "Rose", "scientific": "Rosa spp.", "type": "ornamental", "family": "Rosaceae",
        "sun": "full_sun", "water_needs": "moderate_high", "hardiness_zone": (3, 10),
        "soil_ph": (6.0, 6.5), "soil_type": "loamy_clay", "spacing_cm": 90,
        "days_to_harvest": None, "planting_depth_cm": None,
        "companions": ["lavender", "garlic", "geranium", "marigold"],
        "avoid_near": ["other_roses_too_close"],
        "common_pests": ["aphids", "japanese_beetles", "spider_mites", "thrips"],
        "common_diseases": ["black_spot", "powdery_mildew", "rust"],
        "watering_frequency_days": 3, "fertilizer": "rose-specific feed monthly during growing season",
    },
    "carrot": {
        "name": "Carrot", "scientific": "Daucus carota", "type": "vegetable", "family": "Apiaceae",
        "sun": "full_sun", "water_needs": "moderate", "hardiness_zone": (3, 10),
        "soil_ph": (6.0, 6.8), "soil_type": "sandy_loam", "spacing_cm": 5,
        "days_to_harvest": (70, 80), "planting_depth_cm": 0.5,
        "companions": ["tomato", "lettuce", "onion", "rosemary"],
        "avoid_near": ["dill", "parsnip"],
        "common_pests": ["carrot_fly", "aphids", "wireworms"],
        "common_diseases": ["leaf_blight", "cavity_spot"],
        "watering_frequency_days": 3, "fertilizer": "low nitrogen, high potassium",
    },
    "lavender": {
        "name": "Lavender", "scientific": "Lavandula angustifolia", "type": "herb", "family": "Lamiaceae",
        "sun": "full_sun", "water_needs": "low", "hardiness_zone": (5, 9),
        "soil_ph": (6.5, 8.0), "soil_type": "sandy_well_drained", "spacing_cm": 45,
        "days_to_harvest": None, "planting_depth_cm": None,
        "companions": ["rose", "echinacea", "yarrow"],
        "avoid_near": ["mint"],
        "common_pests": ["whitefly", "spittlebugs"],
        "common_diseases": ["root_rot", "leaf_spot"],
        "watering_frequency_days": 7, "fertilizer": "minimal - light compost in spring",
    },
    "pepper": {
        "name": "Pepper", "scientific": "Capsicum annuum", "type": "vegetable", "family": "Solanaceae",
        "sun": "full_sun", "water_needs": "moderate", "hardiness_zone": (4, 11),
        "soil_ph": (6.0, 6.8), "soil_type": "loamy", "spacing_cm": 45,
        "days_to_harvest": (60, 90), "planting_depth_cm": 1.0,
        "companions": ["basil", "tomato", "carrot", "onion"],
        "avoid_near": ["fennel", "kohlrabi"],
        "common_pests": ["aphids", "pepper_weevil", "hornworm"],
        "common_diseases": ["blossom_end_rot", "bacterial_spot", "mosaic_virus"],
        "watering_frequency_days": 2, "fertilizer": "balanced, higher phosphorus at flowering",
    },
    "lettuce": {
        "name": "Lettuce", "scientific": "Lactuca sativa", "type": "vegetable", "family": "Asteraceae",
        "sun": "partial_shade", "water_needs": "high", "hardiness_zone": (2, 11),
        "soil_ph": (6.0, 7.0), "soil_type": "loamy", "spacing_cm": 25,
        "days_to_harvest": (30, 60), "planting_depth_cm": 0.5,
        "companions": ["carrot", "radish", "strawberry", "chives"],
        "avoid_near": ["celery", "parsley"],
        "common_pests": ["slugs", "aphids", "caterpillars"],
        "common_diseases": ["downy_mildew", "tip_burn", "bottom_rot"],
        "watering_frequency_days": 1, "fertilizer": "nitrogen-rich liquid every 2 weeks",
    },
}

_PESTS: dict[str, dict] = {
    "aphids": {"name": "Aphids", "type": "insect", "damage": "Suck sap, cause curled/yellowed leaves, transmit viruses", "organic_treatments": ["neem oil spray", "ladybugs (biological control)", "strong water spray", "insecticidal soap"], "chemical_treatments": ["pyrethrin", "imidacloprid"], "prevention": "Encourage beneficial insects, avoid over-fertilizing with nitrogen"},
    "slugs": {"name": "Slugs & Snails", "type": "mollusc", "damage": "Irregular holes in leaves, slime trails", "organic_treatments": ["beer traps", "copper tape barriers", "diatomaceous earth", "hand picking at night"], "chemical_treatments": ["ferric phosphate pellets"], "prevention": "Remove hiding spots, water in morning not evening"},
    "whitefly": {"name": "Whitefly", "type": "insect", "damage": "Yellowing leaves, sticky honeydew, sooty mold", "organic_treatments": ["yellow sticky traps", "neem oil", "insecticidal soap", "encarsia formosa (parasitic wasp)"], "chemical_treatments": ["pyrethrin"], "prevention": "Inspect new plants, maintain air circulation"},
    "spider_mites": {"name": "Spider Mites", "type": "arachnid", "damage": "Stippled/bronzed leaves, fine webbing", "organic_treatments": ["strong water spray", "neem oil", "predatory mites"], "chemical_treatments": ["miticide"], "prevention": "Keep humidity up, avoid dusty conditions"},
    "caterpillars": {"name": "Caterpillars", "type": "insect", "damage": "Large holes in leaves, defoliation", "organic_treatments": ["BT (Bacillus thuringiensis)", "hand picking", "row covers", "neem oil"], "chemical_treatments": ["spinosad"], "prevention": "Check undersides of leaves for eggs, encourage birds"},
    "japanese_beetles": {"name": "Japanese Beetles", "type": "insect", "damage": "Skeletonized leaves, damaged flowers", "organic_treatments": ["hand picking into soapy water", "neem oil", "milky spore for grubs"], "chemical_treatments": ["carbaryl"], "prevention": "Treat lawn for grubs, avoid traps near garden"},
}

_SOIL_TYPES = {
    "sandy": {"drainage": "excellent", "nutrient_retention": "poor", "workability": "easy", "amendments": ["compost", "peat_moss", "vermiculite"], "best_for": ["carrots", "lavender", "herbs"]},
    "clay": {"drainage": "poor", "nutrient_retention": "excellent", "workability": "difficult", "amendments": ["gypsum", "compost", "sand", "perlite"], "best_for": ["roses", "asters", "ornamental_grasses"]},
    "loam": {"drainage": "good", "nutrient_retention": "good", "workability": "easy", "amendments": ["compost_annually"], "best_for": ["tomatoes", "peppers", "most_vegetables"]},
    "silt": {"drainage": "moderate", "nutrient_retention": "good", "workability": "moderate", "amendments": ["compost", "coarse_sand"], "best_for": ["lettuce", "onions", "most_crops"]},
    "chalky": {"drainage": "good", "nutrient_retention": "moderate", "workability": "moderate", "amendments": ["sulphur_to_lower_ph", "compost"], "best_for": ["lavender", "spinach", "beets"]},
}


@mcp.tool()
def identify_plant(
    characteristics: dict, api_key: str = "") -> dict:
    """Identify a plant from its characteristics and get care info.

    Args:
        characteristics: Dict with optional keys: type (vegetable|herb|ornamental),
                        family, sun_preference, leaf_description, flower_color,
                        height_cm, fragrant (bool), edible (bool).
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if not _check_rate_limit():
        return {"error": "Rate limit exceeded. Upgrade to pro tier."}

    scores: list[tuple[str, float, dict]] = []

    for plant_id, plant in _PLANTS.items():
        score = 0.0
        max_score = 0.0

        if "type" in characteristics:
            max_score += 3
            if characteristics["type"] == plant["type"]:
                score += 3

        if "family" in characteristics:
            max_score += 2
            if characteristics["family"].lower() == plant["family"].lower():
                score += 2

        if "sun_preference" in characteristics:
            max_score += 2
            if characteristics["sun_preference"] == plant["sun"]:
                score += 2

        if "edible" in characteristics:
            max_score += 1
            is_edible = plant["type"] in ("vegetable", "herb")
            if characteristics["edible"] == is_edible:
                score += 1

        pct = round((score / max_score) * 100) if max_score > 0 else 0
        scores.append((plant_id, pct, plant))

    scores.sort(key=lambda x: x[1], reverse=True)
    return {
        "input": characteristics,
        "matches": [{"plant": m[2]["name"], "confidence_pct": m[1], "profile": m[2]} for m in scores[:3]],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@mcp.tool()
def generate_watering_schedule(
    plants: list[str],
    climate: str = "temperate",
    season: str = "summer",
    container_grown: bool = False, api_key: str = "") -> dict:
    """Generate a watering schedule for your plants.

    Args:
        plants: List of plant names (e.g. ["tomato", "basil", "lavender"]).
        climate: arid | temperate | tropical | cool.
        season: spring | summer | autumn | winter.
        container_grown: Whether plants are in containers (need more frequent watering).
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if not _check_rate_limit():
        return {"error": "Rate limit exceeded. Upgrade to pro tier."}

    climate_mult = {"arid": 0.6, "temperate": 1.0, "tropical": 0.8, "cool": 1.5}
    season_mult = {"spring": 1.0, "summer": 0.7, "autumn": 1.3, "winter": 2.0}
    container_mult = 0.7 if container_grown else 1.0

    schedule = []
    for plant_name in plants:
        plant = _PLANTS.get(plant_name.lower())
        if not plant:
            schedule.append({"plant": plant_name, "error": "Not in database", "default_frequency_days": 3})
            continue

        base_days = plant["watering_frequency_days"]
        adjusted = round(base_days * climate_mult.get(climate, 1.0) * season_mult.get(season, 1.0) * container_mult, 1)
        adjusted = max(0.5, adjusted)

        schedule.append({
            "plant": plant["name"],
            "base_frequency_days": base_days,
            "adjusted_frequency_days": adjusted,
            "water_needs": plant["water_needs"],
            "tips": f"Water deeply at soil level, avoid wetting foliage. Best time: early morning.",
        })

    return {
        "conditions": {"climate": climate, "season": season, "container_grown": container_grown},
        "schedule": schedule,
        "general_tips": [
            "Water deeply and less frequently rather than shallow and often",
            "Check soil moisture 2-3cm deep before watering",
            "Mulch to retain moisture and suppress weeds",
            "Water at the base, not overhead, to prevent disease",
        ],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@mcp.tool()
def analyze_soil(
    soil_type: str,
    ph: float = 6.5,
    plants_planned: Optional[list[str]] = None, api_key: str = "") -> dict:
    """Analyze soil conditions and get amendment recommendations.

    Args:
        soil_type: sandy | clay | loam | silt | chalky.
        ph: Measured soil pH (1.0 - 14.0).
        plants_planned: Plants you intend to grow.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if not _check_rate_limit():
        return {"error": "Rate limit exceeded. Upgrade to pro tier."}

    soil = _SOIL_TYPES.get(soil_type)
    if not soil:
        return {"error": f"Unknown soil type: {soil_type}. Use sandy|clay|loam|silt|chalky."}

    ph_category = "strongly_acidic" if ph < 5.5 else "slightly_acidic" if ph < 6.5 else "neutral" if ph < 7.5 else "slightly_alkaline" if ph < 8.5 else "strongly_alkaline"

    plant_compatibility = []
    if plants_planned:
        for pname in plants_planned:
            plant = _PLANTS.get(pname.lower())
            if plant:
                ph_ok = plant["soil_ph"][0] <= ph <= plant["soil_ph"][1]
                soil_ok = soil_type.lower() in plant["soil_type"].lower() or plant["soil_type"] == "loamy"
                plant_compatibility.append({
                    "plant": plant["name"], "ph_suitable": ph_ok,
                    "soil_suitable": soil_ok, "ideal_ph_range": plant["soil_ph"],
                    "ideal_soil": plant["soil_type"],
                    "status": "ideal" if ph_ok and soil_ok else "needs_amendment" if not ph_ok else "workable",
                })

    amendments = list(soil["amendments"])
    if ph < 6.0:
        amendments.append("garden lime to raise pH")
    elif ph > 7.5:
        amendments.append("sulphur or iron sulphate to lower pH")

    return {
        "soil_type": soil_type, "ph": ph, "ph_category": ph_category,
        "soil_profile": soil,
        "amendments_recommended": amendments,
        "plant_compatibility": plant_compatibility,
        "general_advice": "Add 5-10cm of compost annually to improve any soil type.",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@mcp.tool()
def companion_planting(
    plants: list[str], api_key: str = "") -> dict:
    """Check companion planting compatibility for a group of plants.

    Args:
        plants: List of plant names to check together.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if not _check_rate_limit():
        return {"error": "Rate limit exceeded. Upgrade to pro tier."}

    good_pairs = []
    bad_pairs = []
    unknown = []

    for i, p1 in enumerate(plants):
        plant1 = _PLANTS.get(p1.lower())
        if not plant1:
            unknown.append(p1)
            continue

        for p2 in plants[i + 1:]:
            plant2 = _PLANTS.get(p2.lower())
            if not plant2:
                continue

            if p2.lower() in plant1.get("companions", []) or p1.lower() in plant2.get("companions", []):
                good_pairs.append({"pair": [plant1["name"], plant2["name"]], "relationship": "beneficial"})
            elif p2.lower() in [a.lower() for a in plant1.get("avoid_near", [])] or p1.lower() in [a.lower() for a in plant2.get("avoid_near", [])]:
                bad_pairs.append({"pair": [plant1["name"], plant2["name"]], "relationship": "antagonistic"})
            else:
                good_pairs.append({"pair": [plant1["name"], plant2["name"]], "relationship": "neutral"})

    return {
        "plants_checked": plants,
        "beneficial_pairs": [p for p in good_pairs if p["relationship"] == "beneficial"],
        "neutral_pairs": [p for p in good_pairs if p["relationship"] == "neutral"],
        "antagonistic_pairs": bad_pairs,
        "unknown_plants": unknown,
        "overall": "compatible" if not bad_pairs else "conflicts_found",
        "suggestion": "Separate antagonistic plants by at least 1 metre" if bad_pairs else "Good combination!",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@mcp.tool()
def diagnose_pest(
    symptoms: list[str],
    affected_plant: Optional[str] = None, api_key: str = "") -> dict:
    """Diagnose garden pests from observed symptoms and get treatment plans.

    Args:
        symptoms: Observed symptoms (e.g. holes_in_leaves, yellowing, sticky_residue, webbing).
        affected_plant: Name of affected plant (optional).
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if not _check_rate_limit():
        return {"error": "Rate limit exceeded. Upgrade to pro tier."}

    symptom_to_pest = {
        "holes_in_leaves": ["slugs", "caterpillars", "japanese_beetles"],
        "yellowing": ["aphids", "whitefly", "spider_mites"],
        "curled_leaves": ["aphids"],
        "sticky_residue": ["aphids", "whitefly"],
        "webbing": ["spider_mites"],
        "white_flies": ["whitefly"],
        "slime_trails": ["slugs"],
        "skeletonized_leaves": ["japanese_beetles"],
        "stippled_leaves": ["spider_mites"],
        "defoliation": ["caterpillars", "japanese_beetles"],
    }

    suspects: dict[str, int] = {}
    for sym in symptoms:
        key = sym.lower().replace(" ", "_")
        for pest_id in symptom_to_pest.get(key, []):
            suspects[pest_id] = suspects.get(pest_id, 0) + 1

    if affected_plant:
        plant = _PLANTS.get(affected_plant.lower())
        if plant:
            for pest_id in plant.get("common_pests", []):
                suspects[pest_id] = suspects.get(pest_id, 0) + 1

    ranked = sorted(suspects.items(), key=lambda x: x[1], reverse=True)

    diagnoses = []
    for pest_id, hits in ranked[:3]:
        pest = _PESTS.get(pest_id)
        if pest:
            diagnoses.append({
                "pest": pest["name"], "confidence": "high" if hits >= 2 else "moderate",
                "damage_description": pest["damage"],
                "organic_treatments": pest["organic_treatments"],
                "chemical_treatments": pest["chemical_treatments"],
                "prevention": pest["prevention"],
            })

    return {
        "symptoms_reported": symptoms,
        "affected_plant": affected_plant,
        "diagnoses": diagnoses,
        "recommendation": diagnoses[0]["organic_treatments"][0] if diagnoses else "Consult a local garden centre with photos",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    mcp.run()
