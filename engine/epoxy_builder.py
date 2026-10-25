import os
import json
import re
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone

# ==========================================
# ENVIRONMENT CONFIGURATION
# ==========================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
SITE_BASE_URL = os.environ.get("SITE_BASE_URL", "https://hanifsalman11.github.io/epoxy-gallon-index").rstrip("/")
INDEXNOW_KEY = os.environ.get("INDEXNOW_KEY", "c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8").strip()
CUSTOM_PROJECT = os.environ.get("CUSTOM_PROJECT", "").strip()
PAGES_PER_RUN = int(os.environ.get("PAGES_PER_RUN", "3"))

DOCS_DIR = "docs"
DATA_DIR = "data"
PUBLISHED_FILE = os.path.join(DATA_DIR, "published_projects.json")
MONETIZATION_FILE = os.path.join(DATA_DIR, "monetization.json")

# Format: (Project / Brand Name, Length Inches, Width Inches, Pour Depth Inches, Mix Ratio, Epoxy Formula Type)
SEED_PROJECTS = [
    ("Live-Edge River Dining Table (72x12x2.0 Inch Channel)", 72.0, 12.0, 2.00, "2:1 By Volume", "2:1 Deep-Pour Casting Epoxy"),
    ("Live-Edge River Coffee Table (48x10x1.75 Inch Channel)", 48.0, 10.0, 1.75, "2:1 By Volume", "2:1 Deep-Pour Casting Epoxy"),
    ("8-Foot Commercial Bar Top Flood Coat (96x24x0.125 Inch)", 96.0, 24.0, 0.125, "1:1 By Volume", "1:1 Self-Leveling Table-Top Epoxy"),
    ("Kitchen Island Countertop Flood Coat (84x36x0.125 Inch)", 84.0, 36.0, 0.125, "1:1 By Volume", "1:1 Heat-Resistant Countertop Epoxy"),
    ("TotalBoat ThickSet Deep Pour Epoxy Calculator", 60.0, 10.0, 1.50, "3:1 By Volume", "2:1 / 3:1 Deep-Pour Casting Epoxy"),
    ("TotalBoat TableTop 1:1 Epoxy Resin Calculator", 72.0, 30.0, 0.125, "1:1 By Volume", "1:1 Self-Leveling Table-Top Epoxy"),
    ("Superclear Liquid Glass 2.0 Deep Pour Epoxy Calculator", 72.0, 12.0, 2.00, "2:1 By Volume", "2:1 Deep-Pour Casting Epoxy"),
    ("Superclear Table Top 1:1 Bar & Counter Epoxy Calculator", 60.0, 30.0, 0.125, "1:1 By Volume", "1:1 Self-Leveling Table-Top Epoxy"),
    ("Stone Coat Countertops Epoxy Coverage Calculator", 96.0, 25.5, 0.125, "1:1 By Volume", "1:1 Heat-Resistant Countertop Epoxy"),
    ("MAS Epoxies Table Top Pro 1:1 Volume Calculator", 72.0, 32.0, 0.125, "1:1 By Volume", "1:1 Self-Leveling Table-Top Epoxy"),
    ("MAS Epoxies Deep Pour X 3-Inch Casting Calculator", 48.0, 10.0, 2.25, "2:1 By Volume", "2:1 Deep-Pour Casting Epoxy"),
    ("Promise Epoxy (Pro Marine) Table Top Resin Calculator", 72.0, 36.0, 0.125, "1:1 By Volume", "1:1 Self-Leveling Table-Top Epoxy"),
    ("Promise Epoxy Deep Pour 2-Inch River Table Calculator", 60.0, 11.0, 2.00, "2:1 By Volume", "2:1 Deep-Pour Casting Epoxy"),
    (" WiseBond Deep Pour 2:1 River Table Epoxy Calculator", 72.0, 12.0, 2.00, "2:1 By Volume", "2:1 Deep-Pour Casting Epoxy"),
    ("Ecopoxy FlowCast 2:1 Bio-Based Deep Pour Calculator", 84.0, 14.0, 1.75, "2:1 By Volume", "2:1 Deep-Pour Casting Epoxy"),
    ("System Three MirrorCast & RiverCast Epoxy Calculator", 60.0, 10.0, 1.50, "2:1 By Volume", "2:1 Deep-Pour Casting Epoxy"),
    ("FGCI SuperGlaze & Liquid Glass Deep Pour Calculator", 72.0, 12.0, 2.00, "2:1 By Volume", "2:1 Deep-Pour Casting Epoxy"),
    ("Let's Resin Deep Pour 2-to-4 Inch Casting Calculator", 24.0, 12.0, 2.00, "2:1 By Volume", "2:1 Deep-Pour Casting Epoxy"),
    ("Janchun / Nicpro Crystal Clear 1:1 Art & Charcuterie Board", 24.0, 14.0, 0.25, "1:1 By Volume", "1:1 Art & Board Casting Epoxy"),
    ("2-Car Garage Floor 100% Solids Metallic Epoxy (20x24 Ft)", 288.0, 240.0, 0.045, "2:1 By Volume", "100% Solids Cycloaliphatic Floor Epoxy"),
    ("1-Car Garage Workshop Floor Epoxy Coating (12x20 Ft)", 240.0, 144.0, 0.040, "2:1 By Volume", "100% Solids Garage Floor Epoxy"),
    ("3-Car Garage Floor Epoxy & Polyaspartic Topcoat (30x22 Ft)", 360.0, 264.0, 0.040, "2:1 By Volume", "100% Solids Garage Floor Epoxy"),
    ("Basement Concrete Recreation Room Metallic Floor (400 Sq Ft)", 240.0, 240.0, 0.045, "2:1 By Volume", "100% Solids Metallic Floor Epoxy"),
    ("10-Foot Conference River Table Deep Pour (120x16x2.25 In)", 120.0, 16.0, 2.25, "2:1 By Volume", "2:1 Deep-Pour Casting Epoxy"),
    ("Round Live-Edge Burl Cookie Table Mold (36-Inch Dia x 2 In)", 32.0, 32.0, 2.00, "2:1 By Volume", "2:1 Deep-Pour Casting Epoxy"),
    ("Walnut Charcuterie & Serving Board River Pour (20x6x1.0 In)", 20.0, 6.0, 1.00, "2:1 By Volume", "2:1 Deep-Pour Casting Epoxy"),
    ("L-Shaped Kitchen Countertop Resurfacing (55 Sq Ft)", 132.0, 60.0, 0.125, "1:1 By Volume", "1:1 Heat-Resistant Countertop Epoxy"),
    ("Penny Floor / Bottle Cap Bar Top Encapsulation (60x28x0.25 In)", 60.0, 28.0, 0.25, "1:1 By Volume", "1:1 Self-Leveling Table-Top Epoxy"),
    ("Deep floral Wedding Bouquet Preservation Block (10x10x4 In)", 10.0, 10.0, 4.00, "2:1 By Volume", "2:1 Deep-Pour Casting Epoxy"),
    ("Outdoor Marine Boat Deck & Transom Fiberglass Filleting", 96.0, 48.0, 0.125, "2:1 By Volume", "Marine-Grade Structural Laminating Epoxy")
]


def load_json(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARN] Could not parse {filepath}: {e}")
    return default


def save_json(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    return re.sub(r"[\s-]+", "-", text).strip("-")


def safe_float(val, default=48.0):
    try:
        cleaned = re.sub(r"[^0-9.]", "", str(val))
        return float(cleaned) if cleaned else float(default)
    except Exception:
        return float(default)


def build_amazon_url(search_keywords, mon_cfg):
    domain = mon_cfg.get("marketplace_domain", "www.amazon.com")
    tag = mon_cfg.get("amazon_associate_tag", "YOUR_AMAZON_TAG-20")
    encoded_q = urllib.parse.quote_plus(search_keywords)
    return f"https://{domain}/s?k={encoded_q}&tag={tag}"


def discover_google_epoxy_queries():
    """Mengambil kueri kalkulator volume epoksi & meja river table dari Google Autocomplete US."""
    discovered = []
    seeds = [
        "how much epoxy resin for ",
        "deep pour epoxy calculator for ",
        "totalboat epoxy ",
        "stone coat countertops "
    ]
    for seed in seeds:
        try:
            url = f"http://suggestqueries.google.com/complete/search?client=firefox&hl=en&gl=us&q={urllib.parse.quote(seed)}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for suggestion in data[1]:
                    cleaned = suggestion.lower()
                    for pref in seeds:
                        if "how much" in pref or "calculator" in pref:
                            cleaned = cleaned.replace(pref, "")
                    cleaned = re.sub(
                        r"\b(calculator|how much|gallons|ounces|volume|chart|reddit|for)\b",
                        "",
                        cleaned
                    ).strip()
                    if 5 <= len(cleaned) <= 42:
                        is_deep = "river" in cleaned or "deep" in cleaned or "2 inch" in cleaned
                        if is_deep:
                            discovered.append((cleaned.title(), 60.0, 12.0, 2.00, "2:1 By Volume", "2:1 Deep-Pour Casting Epoxy"))
                        else:
                            discovered.append((cleaned.title(), 72.0, 30.0, 0.125, "1:1 By Volume", "1:1 Self-Leveling Table-Top Epoxy"))
        except Exception as e:
            print(f"[WARN] Google Suggest notice: {e}")
    return discovered


def build_deterministic_epoxy_data(proj_tuple):
    """Mesin Fisika Volumetrik (231 in³/Gal) & Polimer Eksotermik (100% bebas gagal)."""
    proj_name, len_in, wid_in, depth_in, mix_ratio, formula_type = proj_tuple

    area_sqft = round((len_in * wid_in) / 144.0, 1)
    cubic_inches = round(len_in * wid_in * depth_in, 1)

    # 1 US Gallon = 231.0 cubic inches = 128 US Fluid Ounces = 3.7854 Liters
    raw_gallons = cubic_inches / 231.0
    # Tambahkan 10% safety/mixing-cup waste + seal coat buffer
    total_gallons = round(raw_gallons * 1.10, 2)
    total_quarts = round(total_gallons * 4.0, 1)
    total_fl_oz = int(round(total_gallons * 128.0))

    # Breakdown Part A (Resin) vs Part B (Hardener)
    if "2:1" in mix_ratio:
        part_a_oz = int(round(total_fl_oz * (2.0 / 3.0)))
        part_b_oz = total_fl_oz - part_a_oz
        exotherm_note = "Low-exotherm 2:1 cycloaliphatic hardener allows single pours from 1.5\" to 2.5\" thick (72-hour cure) without thermal cracking or yellowing."
    elif "3:1" in mix_ratio:
        part_a_oz = int(round(total_fl_oz * 0.75))
        part_b_oz = total_fl_oz - part_a_oz
        exotherm_note = "Ultra-slow 3:1 deep-casting hardener prevents runaway exothermic boiling in thick 2.0\"–3.5\" river channels."
    else:
        part_a_oz = int(round(total_fl_oz * 0.50))
        part_b_oz = total_fl_oz - part_a_oz
        exotherm_note = "High-viscosity 1:1 tabletop resin cures rapidly (16–24 hours) and MUST be poured at 1/8\" to 1/4\" maximum thickness per layer to prevent overheating."

    kit_gallons_buy = max(1, int(round(total_gallons + 0.45)))

    return {
        "project_name": proj_name,
        "formula_type": formula_type,
        "seo_title": f"{proj_name} Volume Calculator: Gallons, Quarts & Mix Ratio (2026)",
        "meta_description": f"Calculate exact epoxy resin volume ({total_gallons} Gallons / {total_fl_oz} fl oz w/ 10% buffer), {mix_ratio} Part A/B measurements, and pour depth limits for {proj_name}.",
        "specs": {
            "length_inches": len_in,
            "width_inches": wid_in,
            "pour_depth_inches": depth_in,
            "surface_area_sqft": area_sqft,
            "volume_cubic_inches": cubic_inches,
            "total_gallons_w_buffer": total_gallons,
            "total_quarts": total_quarts,
            "total_fl_oz": total_fl_oz,
            "part_a_resin_oz": part_a_oz,
            "part_b_hardener_oz": part_b_oz,
            "mix_ratio": mix_ratio,
            "recommended_kit_gallons": kit_gallons_buy
        },
        "polymer_verdict": f"Measuring {len_in}\" L × {wid_in}\" W ({area_sqft} sq. ft.) at a pour depth of {depth_in} inches, {proj_name} encompasses {cubic_inches:,} cubic inches of volume. Dividing by 231 in³/gallon and adding a mandatory 10% allowance for wood grain absorption, seal coating, and mixing-cup wall cling requires {total_gallons} US Gallons ({total_quarts} Quarts / {total_fl_oz:,} fl. oz.) of {formula_type}—split into {part_a_oz:,} fl. oz. Part A Resin and {part_b_oz:,} fl. oz. Part B Hardener ({mix_ratio}).",
        "hardware_bundle": [
            {
                "badge": f"{kit_gallons_buy}-Gal {mix_ratio.split()[0]} Epoxy Kit",
                "title": f"{kit_gallons_buy}-Gallon Crystal Clear UV-Resistant {formula_type} Kit",
                "price_range": "$79 - $389",
                "amazon_query": f"{kit_gallons_buy} Gallon {formula_type} Kit UV Resistant Crystal Clear",
                "epoxy_note": exotherm_note
            },
            {
                "badge": "No-Stick Silicone Mold & Tape",
                "title": "Reusable Heavy-Duty Seamless Silicone River Table Mold + Tuck Sheathing Tape & Mold Release Spray",
                "price_range": "$49 - $159",
                "amazon_query": "Heavy Duty Silicone River Table Mold Form Release Spray Tape",
                "epoxy_note": "Prevents catastrophic bottom-seam leaks during 48-to-72 hour slow deep-pour cures and releases cleanly without chiseling."
            },
            {
                "badge": "Mica Pigments & Mixing Kit",
                "title": "Metallic Mica Powder Pigment Set + Graduated 5-Quart Mixing Buckets & Low-Shear Helix Drill Mixer",
                "price_range": "$26 - $64",
                "amazon_query": "Mica Powder Pigment Set Epoxy Resin Helix Drill Mixer Graduated Buckets",
                "epoxy_note": f"Graduated ounce markings ensure dead-accurate {part_a_oz} oz : {part_b_oz} oz ({mix_ratio}) stoichiometric polymer cross-linking."
            },
            {
                "badge": "Bubble Torch & Finish Polish",
                "title": "Butane/Propane Micro Bubble Torch, Heat Gun & 3-Step Epoxy Polishing Compound Kit",
                "price_range": "$44 - $129",
                "amazon_query": "Epoxy Resin Bubble Torch Heat Gun Polishing Compound Kit",
                "epoxy_note": "Lowers surface tension to pop micro-bubbles 15 minutes after pouring and buffs sanded edges to a 3,000-grit glass shine."
            }
        ],
        "pouring_checklist": [
            "Brush on a thin 1:1 Seal Coat (3.5 fl. oz. per sq. ft.) over all raw live-edge wood bark and porous end-grain 6–12 hours before your main pour; unsealed wood releases trapped air bubbles for days.",
            f"Never pour 1:1 Table-Top epoxy deeper than 1/4 inch! For pours between 0.5\" and 2.5\" ({depth_in}\" target), strictly use a slow-curing 2:1 or 3:1 Deep-Pour formula in a 68°F–72°F room to prevent exothermic boiling and cracking.",
            "Use the 'Double-Potting' method: mix Part A and Part B thoroughly for 4 full minutes with a low-RPM helix paddle, then pour into a second clean bucket and mix for 1 more minute so zero unmixed resin from the bucket walls enters your project.",
            "Pass a propane torch or heat gun 4–6 inches above the surface in a sweeping motion at 15, 30, and 45 minutes post-pour to break surface tension and release rising micro-bubbles."
        ],
        "faqs": [
            {
                "q": f"How many gallons of epoxy resin do I need for {proj_name}?",
                "a": f"Using the volumetric formula (Length × Width × Depth ÷ 231), {len_in}\" × {wid_in}\" × {depth_in}\" equals {round(raw_gallons, 2)} net gallons. Adding a 10% buffer for seal coating and mixing-cup residue gives {total_gallons} US Gallons ({total_quarts} Quarts or {total_fl_oz:,} fluid ounces)."
            },
            {
                "q": f"What happens if I pour {formula_type} too thick in one layer?",
                "a": f"Epoxy cures via an exothermic (heat-generating) chemical reaction. Exceeding the rated pour depth traps heat in the center of the mass, causing thermal runaway (>200°F), severe amber yellowing, shrinkage cracks, and wave distortions."
            },
            {
                "q": f"How much mica powder or liquid pigment should I add per gallon of epoxy?",
                "a": f"For a translucent ghost-tint river effect, add 1 to 2 grams (1/2 teaspoon) of mica powder per gallon. For a fully opaque metallic swirl across {total_gallons} gallons, mix 15 to 25 grams (1 to 2 tablespoons) of mica powder per gallon into Part A before adding Part B."
            }
        ]
    }


def generate_epoxy_data(proj_tuple):
    """Memanggil Gemini 2.5 Flash API; jika gagal otomatis memakai Deterministic Volumetric Engine."""
    if not GEMINI_API_KEY:
        return build_deterministic_epoxy_data(proj_tuple)

    proj_name, len_in, wid_in, depth_in, mix_ratio, formula_type = proj_tuple
    area_sqft = round((len_in * wid_in) / 144.0, 1)
    cubic_in = round(len_in * wid_in * depth_in, 1)
    tot_gal = round((cubic_in / 231.0) * 1.10, 2)
    tot_qt = round(tot_gal * 4.0, 1)
    tot_oz = int(round(tot_gal * 128.0))
    part_a = int(round(tot_oz * (2.0 / 3.0))) if "2:1" in mix_ratio else int(round(tot_oz * 0.5))
    part_b = tot_oz - part_a
    kit_buy = max(1, int(round(tot_gal + 0.45)))

    prompt = f"""
You are a Senior Polymer Chemist & Master Live-Edge Epoxy Furniture Maker. Create an accurate 2026 epoxy resin volume (Gallons, Quarts, Fluid Ounces), mix ratio, and exothermic pour depth guide for: "{proj_name}".
Baseline reference specs: Dimensions={len_in}\" L x {wid_in}\" W x {depth_in}\" Depth ({area_sqft} sq ft, {cubic_in} cu in), Total w/ 10% Waste={tot_gal} Gallons ({tot_qt} Quarts / {tot_oz} fl oz), Mix Ratio={mix_ratio} ({part_a} oz Part A : {part_b} oz Part B), Formula={formula_type}.
Return ONLY a valid JSON object matching this exact schema:
{{
  "project_name": "{proj_name}",
  "formula_type": "{formula_type}",
  "seo_title": "{proj_name} Volume Calculator: Gallons, Quarts & Mix Ratio (2026)",
  "meta_description": "Calculate exact epoxy resin gallons, quarts, fluid ounces, Part A/B mix ratios, and exothermic pour depth limits for {proj_name}.",
  "specs": {{
    "length_inches": {len_in},
    "width_inches": {wid_in},
    "pour_depth_inches": {depth_in},
    "surface_area_sqft": {area_sqft},
    "volume_cubic_inches": {cubic_in},
    "total_gallons_w_buffer": {tot_gal},
    "total_quarts": {tot_qt},
    "total_fl_oz": {tot_oz},
    "part_a_resin_oz": {part_a},
    "part_b_hardener_oz": {part_b},
    "mix_ratio": "{mix_ratio}",
    "recommended_kit_gallons": {kit_buy}
  }},
  "polymer_verdict": "3-sentence technical summary stating cubic inches, exact US gallons and fluid ounces (with 10% waste/seal coat buffer), Part A/B fluid ounces, and exothermic depth limits.",
  "hardware_bundle": [
    {{
      "badge": "Matched Epoxy Resin Kit",
      "title": "Exact Gallon UV-Resistant {formula_type} Kit recommendation",
      "price_range": "$79 - $389",
      "amazon_query": "{kit_buy} Gallon {formula_type} Kit Crystal Clear",
      "epoxy_note": "1-sentence viscosity and exothermic cure note"
    }},
    {{
      "badge": "Leak-Proof Mold & Release",
      "title": "Heavy-Duty Seamless Silicone River Table Mold + Sheathing Tape & Release Spray",
      "price_range": "$49 - $159",
      "amazon_query": "Silicone River Table Mold Form Release Spray",
      "epoxy_note": "1-sentence demolding and leak prevention note"
    }},
    {{
      "badge": "Pigments & Mixing Buckets",
      "title": "Metallic Mica Powder Pigment Set + Graduated Mixing Buckets & Helix Drill Paddle",
      "price_range": "$26 - $64",
      "amazon_query": "Mica Powder Pigment Set Epoxy Helix Drill Mixer",
      "epoxy_note": "1-sentence stoichiometric ratio accuracy note"
    }},
    {{
      "badge": "Torch & Polishing Kit",
      "title": "Propane Micro Bubble Torch, Heat Gun & Epoxy Polishing Compound Kit",
      "price_range": "$44 - $129",
      "amazon_query": "Epoxy Resin Bubble Torch Polishing Compound Kit",
      "epoxy_note": "1-sentence bubble degassing and optical clarity note"
    }}
  ],
  "pouring_checklist": [
    "Step 1 regarding raw wood live-edge seal coat to stop outgassing bubbles",
    "Step 2 regarding 68F-72F ambient temperature and max pour thickness",
    "Step 3 regarding 4-minute mixing and double-potting bucket transfer",
    "Step 4 regarding torch sweeps at 15, 30, and 45 minutes post-pour"
  ],
  "faqs": [
    {{"q": "How many gallons of epoxy do I need for {proj_name}?", "a": "Exact cubic inches divided by 231 plus 10% buffer in Gallons, Quarts, and Fluid Ounces."}},
    {{"q": "Should I use 1:1 Table Top or 2:1 Deep Pour epoxy for {proj_name}?", "a": "Direct polymer chemistry explanation based on pour thickness."}},
    {{"q": "How do I prevent bubbles and yellowing in {proj_name}?", "a": "Direct technical answer on seal coats, HALS UV stabilizers, and exothermic heat."}}
  ]
}}
"""

    for model_id in ["gemini-2.5-flash", "gemini-2.0-flash"]:
        try:
            endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={GEMINI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.2,
                    "responseMimeType": "application/json"
                }
            }
            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=35) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                raw_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
                raw_text = re.sub(r"\s*```$", "", raw_text)
                parsed = json.loads(raw_text)
                if "specs" in parsed and "hardware_bundle" in parsed:
                    return parsed
        except Exception as e:
            print(f"[WARN] Gemini ({model_id}) notice for '{proj_name}': {e}")

    return build_deterministic_epoxy_data(proj_tuple)


def build_epoxy_html_page(data, slug, mon_cfg):
    proj_name = data.get("project_name", "Epoxy Resin Project")
    formula_type = data.get("formula_type", "2:1 Deep-Pour Casting Epoxy")
    sp = data.get("specs", {})
    len_in = round(safe_float(sp.get("length_inches", 72.0), 72.0), 1)
    wid_in = round(safe_float(sp.get("width_inches", 12.0), 12.0), 1)
    depth_in = round(safe_float(sp.get("pour_depth_inches", 2.0), 2.0), 3)
    area_sqft = round(safe_float(sp.get("surface_area_sqft", 6.0), 6.0), 1)
    tot_gal = round(safe_float(sp.get("total_gallons_w_buffer", 8.2), 8.2), 2)
    tot_qt = round(safe_float(sp.get("total_quarts", tot_gal * 4), 32.8), 1)
    tot_oz = int(safe_float(sp.get("total_fl_oz", int(tot_gal * 128)), 1050))
    part_a = int(safe_float(sp.get("part_a_resin_oz", int(tot_oz * 0.67)), 700))
    part_b = int(safe_float(sp.get("part_b_hardener_oz", tot_oz - part_a), 350))
    mix_ratio = sp.get("mix_ratio", "2:1 By Volume")

    header_cta = mon_cfg.get("header_cta", {})
    header_cta_url = build_amazon_url(header_cta.get("search_query", "Deep+Pour+Epoxy+Resin+Kit+Crystal+Clear"), mon_cfg)

    schema_graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "SoftwareApplication",
                "name": f"{proj_name} Epoxy Resin Gallon & Mix Ratio Calculator",
                "applicationCategory": "UtilitiesApplication",
                "operatingSystem": "Web Browser",
                "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": f.get("q", ""),
                        "acceptedAnswer": {"@type": "Answer", "text": f.get("a", "")}
                    } for f in data.get("faqs", [])
                ]
            }
        ]
    }

    bundle_html = ""
    for item in data.get("hardware_bundle", []):
        amz_url = build_amazon_url(item.get("amazon_query", item.get("title", "Deep Pour Epoxy Resin Kit")), mon_cfg)
        bundle_html += f"""
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col justify-between hover:border-purple-500/60 transition">
          <div>
            <div class="flex items-center justify-between gap-2 mb-2">
              <span class="text-xs font-bold uppercase tracking-wider bg-purple-500/10 text-purple-400 border border-purple-500/20 px-2.5 py-0.5 rounded">{item.get('badge', 'Epoxy Gear')}</span>
              <span class="text-sm font-bold text-emerald-400">{item.get('price_range', '$49+')}</span>
            </div>
            <h3 class="text-base font-bold text-white mt-2">{item.get('title', '')}</h3>
            <p class="text-xs text-slate-400 mt-2 leading-relaxed">🧪 {item.get('epoxy_note', '')}</p>
          </div>
          <a href="{amz_url}" target="_blank" rel="nofollow sponsored" class="mt-5 block text-center bg-purple-500 hover:bg-purple-400 text-white font-extrabold py-2.5 px-4 rounded-lg text-sm transition shadow-lg">
            Check Price on Amazon →
          </a>
        </div>"""

    # Build Pour Depth vs Volume Reference Matrix Table
    depth_tiers = [
        ("1/16 Inch (0.0625\") Seal Coat", 0.0625, "1:1 Table-Top Epoxy", "4.0 fl oz / sq ft"),
        ("1/8 Inch (0.125\") Self-Leveling Flood Coat", 0.125, "1:1 Table-Top Epoxy", "8.0 fl oz / sq ft"),
        ("1/4 Inch (0.250\") Heavy Bar-Top Pour", 0.250, "1:1 Table-Top Max", "16.0 fl oz / sq ft"),
        ("1.0 Inch (1.000\") Shallow River / Board", 1.000, "2:1 Deep-Pour Epoxy", "0.50 Gal / sq ft"),
        ("1.5 Inch (1.500\") Standard River Table", 1.500, "2:1 Deep-Pour Epoxy", "0.75 Gal / sq ft"),
        ("2.0 Inch (2.000\") Thick Slab River Table", 2.000, "2:1 / 3:1 Deep-Pour", "1.00 Gal / sq ft")
    ]
    matrix_rows_html = ""
    for d_label, d_val, f_rec, cov_rate in depth_tiers:
        calc_g = round(((len_in * wid_in * d_val) / 231.0) * 1.10, 2)
        calc_oz = int(round(calc_g * 128.0))
        matrix_rows_html += f"""
        <tr class="border-b border-slate-800 hover:bg-slate-800/40">
          <td class="py-3 px-4 font-bold text-white">{d_label}</td>
          <td class="py-3 px-4 font-bold text-purple-400">{calc_g} Gal ({calc_oz:,} fl oz)</td>
          <td class="py-3 px-4 text-emerald-400 font-semibold">{f_rec}</td>
          <td class="py-3 px-4 text-xs text-slate-300">{cov_rate} (+10% Buffer)</td>
        </tr>"""

    checklist_html = ""
    for idx, step_text in enumerate(data.get("pouring_checklist", []), start=1):
        checklist_html += f"""
        <label class="flex items-start gap-3.5 bg-slate-900 border border-slate-800 rounded-xl p-4 cursor-pointer hover:border-slate-700 transition">
          <input type="checkbox" class="mt-1 w-5 h-5 accent-purple-500 rounded cursor-pointer epoxy-check">
          <span class="text-sm text-slate-200 leading-relaxed"><strong>Pour Step {idx}:</strong> {step_text}</span>
        </label>"""

    faqs_html = "".join([
        f"<div class='bg-slate-900 border border-slate-800 rounded-xl p-5'><h3 class='font-bold text-white text-base mb-2'>{f.get('q', '')}</h3><p class='text-sm text-slate-300 leading-relaxed'>{f.get('a', '')}</p></div>"
        for f in data.get("faqs", [])
    ])

    canonical_url = f"{SITE_BASE_URL}/{slug}.html"
    amz_domain = mon_cfg.get("marketplace_domain", "www.amazon.com")
    amz_tag = mon_cfg.get("amazon_associate_tag", "YOUR_AMAZON_TAG-20")

    html = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{data.get('seo_title', proj_name)}</title>
  <meta name="description" content="{data.get('meta_description', '')}">
  <link rel="canonical" href="{canonical_url}">
  <meta property="og:title" content="{data.get('seo_title', proj_name)}">
  <meta property="og:description" content="{data.get('meta_description', '')}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{canonical_url}">
  <script src="https://cdn.tailwindcss.com"></script>
  <script type="application/ld+json">{json.dumps(schema_graph)}</script>
</head>
<body class="bg-slate-950 text-slate-100 antialiased min-h-screen flex flex-col">
  <header class="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-30">
    <div class="max-w-5xl mx-auto px-4 py-3.5 flex items-center justify-between">
      <a href="index.html" class="text-lg font-black tracking-tight text-white flex items-center gap-2">
        <span class="bg-purple-500 text-white px-2 py-0.5 rounded font-black">EPOXY</span>GallonIndex
      </a>
      <a href="{header_cta_url}" target="_blank" rel="nofollow sponsored" class="text-xs sm:text-sm bg-purple-500 hover:bg-purple-400 text-white font-extrabold px-3.5 py-2 rounded-lg transition">
        {header_cta.get('cta_text', 'Shop Deep-Pour & Table-Top Epoxy →')}
      </a>
    </div>
  </header>

  <main class="max-w-5xl mx-auto px-4 py-10 flex-1 w-full">
    <div class="mb-8">
      <div class="flex flex-wrap items-center gap-2.5 mb-3">
        <span class="text-xs font-extrabold uppercase tracking-widest bg-purple-500 text-white px-3 py-1 rounded-full">{tot_gal} Gallons ({tot_oz:,} Fl Oz)</span>
        <span class="text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-3 py-1 rounded-full">{formula_type} ({mix_ratio})</span>
        <span class="text-xs font-semibold bg-slate-800 text-slate-300 px-3 py-1 rounded-full">Pour: {len_in}" L × {wid_in}" W × {depth_in}" D</span>
      </div>
      <h1 class="text-3xl sm:text-4xl font-black text-white leading-tight">{data.get('seo_title', proj_name)}</h1>
      <div class="mt-4 bg-slate-900 border-l-4 border-purple-500 p-4 rounded-r-xl text-sm text-slate-200 leading-relaxed">
        <strong>Polymer Chemistry & Volumetric Verdict:</strong> {data.get('polymer_verdict', '')}
      </div>
    </div>

    <!-- INTERACTIVE EPOXY GALLON, QUART, FLUID OUNCE & MIX RATIO CALCULATOR -->
    <section class="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 mb-12 shadow-2xl">
      <h2 class="text-xl font-extrabold text-white mb-2">Interactive {proj_name} Gallon & Mix Ratio Calculator</h2>
      <p class="text-xs text-slate-400 mb-6">Adjust your pour length, average river/table width, pour thickness, and resin mix ratio to compute exact US Gallons, Quarts, Fluid Ounces, and Part A/B measurements.</p>

      <div class="grid md:grid-cols-2 gap-8 items-center">
        <div class="space-y-5">
          <div>
            <div class="flex justify-between text-sm font-medium mb-1.5">
              <label for="lenSlider" class="text-slate-300">Pour Length (Inches)</label>
              <span class="text-purple-400 font-bold"><span id="lenVal">{len_in}</span>" ({round(len_in/12, 1)} ft)</span>
            </div>
            <input id="lenSlider" type="range" min="12" max="144" step="2" value="{min(144, int(len_in))}" class="w-full accent-purple-500 cursor-pointer">
          </div>

          <div>
            <div class="flex justify-between text-sm font-medium mb-1.5">
              <label for="widSlider" class="text-slate-300">Average River Channel or Table Width (Inches)</label>
              <span class="text-purple-400 font-bold"><span id="widVal">{wid_in}</span>"</span>
            </div>
            <input id="widSlider" type="range" min="2" max="60" step="1" value="{min(60, int(wid_in))}" class="w-full accent-purple-500 cursor-pointer">
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label for="depthSelect" class="block text-xs font-medium text-slate-400 mb-1">Target Pour Thickness</label>
              <select id="depthSelect" class="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-purple-500">
                <option value="0.0625">1/16" (0.063") Wood Seal Coat</option>
                <option value="0.125" {"selected" if depth_in <= 0.15 else ""}>1/8" (0.125") Table-Top Flood Coat</option>
                <option value="0.25">1/4" (0.250") Heavy Bar Top</option>
                <option value="1.00">1.0" Shallow River Channel</option>
                <option value="1.50" {"selected" if 0.5 < depth_in <= 1.6 else ""}>1.5" Standard River Table</option>
                <option value="2.00" {"selected" if 1.6 < depth_in <= 2.1 else ""}>2.0" Deep Pour River Slab</option>
                <option value="3.00" {"selected" if depth_in > 2.1 else ""}>3.0" Ultra-Deep Casting</option>
              </select>
            </div>
            <div>
              <label for="ratioSelect" class="block text-xs font-medium text-slate-400 mb-1">Epoxy Mix Ratio & Buffer</label>
              <select id="ratioSelect" class="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-purple-500">
                <option value="1:1" {"selected" if "1:1" in mix_ratio else ""}>1:1 Table-Top (+10% Buffer)</option>
                <option value="2:1" {"selected" if "2:1" in mix_ratio else ""}>2:1 Deep-Pour (+10% Buffer)</option>
                <option value="3:1" {"selected" if "3:1" in mix_ratio else ""}>3:1 ThickSet (+10% Buffer)</option>
              </select>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="bg-slate-950 border border-purple-500/30 rounded-xl p-4">
            <span class="text-xs uppercase text-purple-400 font-bold">Total Epoxy Needed</span>
            <div class="text-2xl sm:text-3xl font-black text-white mt-1"><span id="galOut">{tot_gal}</span> <span class="text-sm font-normal text-slate-400">Gal</span></div>
            <p id="ozOut" class="text-xs text-purple-400 font-semibold mt-1">{tot_qt} Quarts ({tot_oz:,} fl oz)</p>
          </div>

          <div class="bg-slate-950 border border-emerald-500/30 rounded-xl p-4">
            <span class="text-xs uppercase text-emerald-400 font-bold">Part A / Part B Split</span>
            <div id="splitOut" class="text-lg sm:text-xl font-black text-emerald-400 mt-1">{part_a} oz A : {part_b} oz B</div>
            <p id="exoStatusOut" class="text-xs text-slate-300 font-semibold mt-1">✅ Safe Exothermic Depth</p>
          </div>
        </div>
      </div>

      <div class="mt-6 bg-purple-950/40 border border-purple-500/30 rounded-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div id="epoxyAdviceBanner" class="text-sm text-purple-100 font-medium"></div>
        <a id="dynamicEpoxyBtn" href="{header_cta_url}" target="_blank" rel="nofollow sponsored" class="shrink-0 bg-purple-500 hover:bg-purple-400 text-white font-extrabold px-4 py-2.5 rounded-lg text-xs uppercase tracking-wider transition">
          Shop Matched Epoxy Kit on Amazon →
        </a>
      </div>
    </section>

    <!-- 4-CARD HARDWARE BUNDLE -->
    <section class="mb-12">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-2xl font-extrabold text-white">Complete {proj_name} Resin, Mold & Finishing Bundle</h2>
        <span class="text-xs text-slate-400">UV-Stabilized HALS & Zero-VOC Rated</span>
      </div>
      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">{bundle_html}</div>
    </section>

    <!-- POUR DEPTH & COVERAGE MATRIX TABLE -->
    <section class="mb-12">
      <h2 class="text-2xl font-extrabold text-white mb-4">{proj_name} Volume by Pour Thickness ({len_in}" × {wid_in}" Area)</h2>
      <div class="overflow-x-auto bg-slate-900 border border-slate-800 rounded-xl">
        <table class="w-full text-left border-collapse text-sm">
          <thead>
            <tr class="border-b border-slate-800 bg-slate-950/60 text-slate-400 uppercase text-xs">
              <th class="py-3.5 px-4">Pour Layer / Depth</th>
              <th class="py-3.5 px-4 text-purple-400">Required Volume (+10% Waste)</th>
              <th class="py-3.5 px-4 text-emerald-400">Required Epoxy Formula</th>
              <th class="py-3.5 px-4">Coverage Benchmark</th>
            </tr>
          </thead>
          <tbody>{matrix_rows_html}</tbody>
        </table>
      </div>
    </section>

    <!-- POURING CHECKLIST -->
    <section class="mb-12">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-2xl font-extrabold text-white">Bubble-Free Seal Coat, Mixing & Exothermic Control Checklist</h2>
        <span id="epoxyBadge" class="text-xs font-bold bg-slate-800 text-purple-400 px-3 py-1 rounded-full">0 / 4 Completed</span>
      </div>
      <div class="space-y-3">{checklist_html}</div>
    </section>

    <!-- FAQ -->
    <section class="mb-12">
      <h2 class="text-2xl font-extrabold text-white mb-5">Frequently Asked Questions ({proj_name})</h2>
      <div class="space-y-4">{faqs_html}</div>
    </section>
  </main>

  <footer class="border-t border-slate-800 py-8 text-center text-xs text-slate-500 px-4">
    <p>© {datetime.now(timezone.utc).year} EpoxyGallonIndex. Independent Polymer Volume & Woodworking Finishing Database. As an Amazon Associate, we earn from qualifying purchases.</p>
  </footer>

  <script>
    const amzDomain = "{amz_domain}";
    const amzTag = "{amz_tag}";

    const lenSlider = document.getElementById('lenSlider');
    const widSlider = document.getElementById('widSlider');
    const depthSelect = document.getElementById('depthSelect');
    const ratioSelect = document.getElementById('ratioSelect');
    const lenVal = document.getElementById('lenVal');
    const widVal = document.getElementById('widVal');
    const galOut = document.getElementById('galOut');
    const ozOut = document.getElementById('ozOut');
    const splitOut = document.getElementById('splitOut');
    const exoStatusOut = document.getElementById('exoStatusOut');
    const epoxyAdviceBanner = document.getElementById('epoxyAdviceBanner');
    const dynamicEpoxyBtn = document.getElementById('dynamicEpoxyBtn');

    function recalculateEpoxy() {{
      const lIn = parseFloat(lenSlider.value);
      const wIn = parseFloat(widSlider.value);
      const dIn = parseFloat(depthSelect.value);
      const ratio = ratioSelect.value;

      lenVal.textContent = lIn;
      widVal.textContent = wIn;

      const cubicIn = lIn * wIn * dIn;
      const totGal = (cubicIn / 231.0) * 1.10;
      const totQt = totGal * 4.0;
      const totOz = Math.round(totGal * 128.0);

      let ozA = Math.round(totOz * 0.5);
      let ozB = totOz - ozA;
      if (ratio === '2:1') {{
        ozA = Math.round(totOz * (2.0 / 3.0));
        ozB = totOz - ozA;
      }} else if (ratio === '3:1') {{
        ozA = Math.round(totOz * 0.75);
        ozB = totOz - ozA;
      }}

      galOut.textContent = totGal.toFixed(2);
      ozOut.textContent = `${{totQt.toFixed(1)}} Quarts (${{totOz.toLocaleString()}} fl oz)`;
      splitOut.textContent = `${{ozA.toLocaleString()}} oz A : ${{ozB.toLocaleString()}} oz B`;

      if (dIn > 0.25 && ratio === '1:1') {{
        exoStatusOut.textContent = "⚠️ Exotherm Risk! Switch to 2:1 Deep Pour";
        exoStatusOut.className = "text-xs text-amber-400 font-bold mt-1";
      }} else {{
        exoStatusOut.textContent = `✅ Safe Pour Depth (${{ratio}} Formula)`;
        exoStatusOut.className = "text-xs text-emerald-400 font-semibold mt-1";
      }}

      const buyGals = Math.max(1, Math.ceil(totGal));
      const formulaSearch = dIn >= 0.5 ? "Deep+Pour+Epoxy+Resin+Kit+2:1+River+Table" : "Table+Top+Epoxy+Resin+Kit+1:1+Crystal+Clear";
      const formulaName = dIn >= 0.5 ? "2:1 Deep-Pour Casting Epoxy" : "1:1 Self-Leveling Table-Top Epoxy";

      epoxyAdviceBanner.innerHTML = `🧪 <strong>Order Spec:</strong> You need <strong>${{totGal.toFixed(2)}} US Gallons (${{totOz.toLocaleString()}} fl. oz.)</strong> including a 10% seal-coat & cup-waste buffer. Order at least <strong>${{buyGals}} Gallon(s) of ${{formulaName}}</strong>.`;
      dynamicEpoxyBtn.href = `https://${{amzDomain}}/s?k=${{buyGals}}+Gallon+${{formulaSearch}}&tag=${{amzTag}}`;
    }}

    lenSlider.addEventListener('input', recalculateEpoxy);
    widSlider.addEventListener('input', recalculateEpoxy);
    depthSelect.addEventListener('change', recalculateEpoxy);
    ratioSelect.addEventListener('change', recalculateEpoxy);
    recalculateEpoxy();

    const checks = document.querySelectorAll('.epoxy-check');
    const badge = document.getElementById('epoxyBadge');
    checks.forEach(ch => {{
      ch.addEventListener('change', () => {{
        const done = Array.from(checks).filter(c => c.checked).length;
        badge.textContent = `${{done}} / ${{checks.length}} Completed`;
      }});
    }});
  </script>
</body>
</html>"""

    os.makedirs(DOCS_DIR, exist_ok=True)
    with open(os.path.join(DOCS_DIR, f"{slug}.html"), "w", encoding="utf-8") as f:
        f.write(html)


def rebuild_portal_sitemap_and_rss(published, mon_cfg):
    header_cta = mon_cfg.get("header_cta", {})
    header_cta_url = build_amazon_url(header_cta.get("search_query", "Deep+Pour+Epoxy+Resin+Kit+Crystal+Clear"), mon_cfg)

    cards_html = ""
    for item in reversed(published):
        cards_html += f"""
        <a href="{item['slug']}.html" class="block bg-slate-900 border border-slate-800 hover:border-purple-500/60 rounded-xl p-5 transition group">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-black uppercase bg-purple-500 text-white px-2.5 py-0.5 rounded">{item.get('gallons', 2.5)} Gal ({item.get('fl_oz', 320):,} oz)</span>
            <span class="text-xs text-slate-400">{item.get('mix_ratio', '2:1 By Volume')}</span>
          </div>
          <h2 class="text-base font-bold text-white group-hover:text-purple-400 transition">{item['project_name']}</h2>
          <p class="text-xs text-slate-400 mt-2 line-clamp-2">{item['description']}</p>
          <span class="inline-block mt-4 text-xs font-extrabold text-purple-400">Calculate Gallons, Ounces & Mix Ratio →</span>
        </a>"""

    index_html = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>EpoxyGallonIndex — Epoxy Resin Volume (Gallons/Ounces), River Table & Countertop Calculator (2026)</title>
  <meta name="description" content="Calculate exact deep-pour river table, bar top flood coat, and garage floor epoxy volume in US Gallons, Quarts, and Fluid Ounces for TotalBoat, Superclear, Stone Coat, MAS, and Promise Epoxy.">
  <link rel="canonical" href="{SITE_BASE_URL}/">
  <link rel="alternate" type="application/rss+xml" title="EpoxyGallonIndex RSS Feed" href="{SITE_BASE_URL}/rss.xml">
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col">
  <header class="border-b border-slate-800 bg-slate-900/80 sticky top-0 z-30 backdrop-blur">
    <div class="max-w-5xl mx-auto px-4 py-3.5 flex items-center justify-between">
      <div class="text-lg font-black text-white flex items-center gap-2">
        <span class="bg-purple-500 text-white px-2 py-0.5 rounded font-black">EPOXY</span>GallonIndex
      </div>
      <a href="{header_cta_url}" target="_blank" rel="nofollow sponsored" class="text-xs sm:text-sm bg-purple-500 hover:bg-purple-400 text-white font-extrabold px-3.5 py-2 rounded-lg transition">
        {header_cta.get('cta_text', 'Shop Deep-Pour & Table-Top Epoxy →')}
      </a>
    </div>
  </header>

  <main class="max-w-5xl mx-auto px-4 py-12 flex-1 w-full">
    <div class="text-center max-w-2xl mx-auto mb-10">
      <h1 class="text-3xl sm:text-5xl font-black text-white tracking-tight">Epoxy Resin Gallon, River Table & Countertop Volume Database</h1>
      <p class="text-slate-400 mt-3 text-base sm:text-lg">Select your woodworking project or epoxy brand below to calculate exact US Gallons, Quarts, Fluid Ounces, Part A/B mix ratios, and exothermic pour depth limits.</p>
      <div class="mt-6">
        <input id="filterInput" type="text" placeholder="Search project or brand (e.g. River Table, Bar Top, TotalBoat, Superclear, Stone Coat, Garage Floor...)" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3.5 text-sm text-white focus:outline-none focus:border-purple-500">
      </div>
    </div>

    <div id="epoxyGrid" class="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">{cards_html}</div>
  </main>

  <footer class="border-t border-slate-800 py-8 text-center text-xs text-slate-500">
    <p>© {datetime.now(timezone.utc).year} EpoxyGallonIndex. As an Amazon Associate, we earn from qualifying purchases.</p>
  </footer>

  <script>
    const filterInput = document.getElementById('filterInput');
    const cards = Array.from(document.getElementById('epoxyGrid').children);
    filterInput.addEventListener('input', (e) => {{
      const q = e.target.value.toLowerCase();
      cards.forEach(c => {{
        c.style.display = c.textContent.toLowerCase().includes(q) ? 'block' : 'none';
      }});
    }});
  </script>
</body>
</html>"""

    os.makedirs(DOCS_DIR, exist_ok=True)
    with open(os.path.join(DOCS_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    urls_xml = f"""  <url>
    <loc>{SITE_BASE_URL}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>\n"""

    for item in published:
        urls_xml += f"""  <url>
    <loc>{SITE_BASE_URL}/{item['slug']}.html</loc>
    <lastmod>{item.get('date', today)}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>\n"""

    with open(os.path.join(DOCS_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(f"""<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls_xml}</urlset>""")

    rss_items = ""
    for item in list(reversed(published))[:30]:
        rss_items += f"""    <item>
      <title>{item['title']}</title>
      <link>{SITE_BASE_URL}/{item['slug']}.html</link>
      <guid>{SITE_BASE_URL}/{item['slug']}.html</guid>
      <description>{item['description']}</description>
    </item>\n"""

    rss_xml = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>EpoxyGallonIndex River Table & Countertop Epoxy Database</title>
    <link>{SITE_BASE_URL}/</link>
    <description>Interactive Epoxy Resin Volume (Gallons/Quarts/Ounces) & Mix Ratio Calculators</description>
    <atom:link href="{SITE_BASE_URL}/rss.xml" rel="self" type="application/rss+xml" />
    <atom:link href="https://pubsubhubbub.appspot.com/" rel="hub" />
{rss_items}  </channel>
</rss>"""

    with open(os.path.join(DOCS_DIR, "rss.xml"), "w", encoding="utf-8") as f:
        f.write(rss_xml)

    with open(os.path.join(DOCS_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {SITE_BASE_URL}/sitemap.xml\n")

    with open(os.path.join(DOCS_DIR, f"{INDEXNOW_KEY}.txt"), "w", encoding="utf-8") as f:
        f.write(INDEXNOW_KEY)


def notify_search_engines(new_urls):
    if not SITE_BASE_URL or not new_urls:
        return
    parsed_host = urllib.parse.urlparse(SITE_BASE_URL).netloc
    payload = {
        "host": parsed_host,
        "key": INDEXNOW_KEY,
        "keyLocation": f"{SITE_BASE_URL}/{INDEXNOW_KEY}.txt",
        "urlList": new_urls
    }
    try:
        req = urllib.request.Request(
            "https://api.indexnow.org/indexnow",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"[INDEXNOW] Pushed {len(new_urls)} URLs (HTTP {resp.status})")
    except Exception as e:
        print(f"[WARN] IndexNow ping notice: {e}")

    try:
        hub_data = urllib.parse.urlencode({
            "hub.mode": "publish",
            "hub.url": f"{SITE_BASE_URL}/rss.xml"
        }).encode("utf-8")
        req_hub = urllib.request.Request(
            "https://pubsubhubbub.appspot.com/",
            data=hub_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST"
        )
        with urllib.request.urlopen(req_hub, timeout=15) as resp_hub:
            print(f"[WEBSUB] Google PubSubHubbub ping status: {resp_hub.status}")
    except Exception as e:
        print(f"[WARN] WebSub ping notice: {e}")


def main():
    published = load_json(PUBLISHED_FILE, [])
    mon_cfg = load_json(MONETIZATION_FILE, {})
    published_slugs = {item["slug"] for item in published}

    candidates = []
    if CUSTOM_PROJECT:
        candidates.append((CUSTOM_PROJECT.strip(), 72.0, 12.0, 2.00, "2:1 By Volume", "2:1 Deep-Pour Casting Epoxy"))
    candidates.extend(SEED_PROJECTS)
    candidates.extend(discover_google_epoxy_queries())

    new_urls = []
    count = 0

    for proj_tuple in candidates:
        if count >= PAGES_PER_RUN:
            break
        p_name = proj_tuple[0]
        slug = slugify(f"{p_name}-epoxy-gallon-calculator")
        if slug in published_slugs:
            continue

        print(f"[ENGINE] Generating epoxy gallon & mix ratio calculator for: {p_name}...")
        try:
            data = generate_epoxy_data(proj_tuple)
            build_epoxy_html_page(data, slug, mon_cfg)
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            sp = data.get("specs", {})

            published.append({
                "project_name": data.get("project_name", p_name),
                "slug": slug,
                "title": data.get("seo_title", f"{p_name} Epoxy Calculator"),
                "description": data.get("meta_description", ""),
                "gallons": round(safe_float(sp.get("total_gallons_w_buffer", 4.5), 4.5), 2),
                "fl_oz": int(safe_float(sp.get("total_fl_oz", 576), 576)),
                "mix_ratio": sp.get("mix_ratio", proj_tuple[4]),
                "date": today
            })
            published_slugs.add(slug)
            if SITE_BASE_URL:
                new_urls.append(f"{SITE_BASE_URL}/{slug}.html")
            count += 1
            time.sleep(2)
        except Exception as e:
            print(f"[ERROR] Failed building {p_name}: {e}")

    save_json(PUBLISHED_FILE, published)
    rebuild_portal_sitemap_and_rss(published, mon_cfg)
    if new_urls and SITE_BASE_URL:
        new_urls.append(f"{SITE_BASE_URL}/")
        notify_search_engines(new_urls)
    print(f"[DONE] Published {count} new epoxy resin gallon calculator pages.")


if __name__ == "__main__":
    main()
