# -*- coding: utf-8 -*-
import json, re, random, urllib.request, urllib.parse

ARTICLES_FILE = "articles.json"
TARGET_WORDS = 500   # 每篇目标词数
MIN_WORDS = 200      # 低于此词数的文章不入库（也会清理掉旧的短文）
MAX_KEEP = 400       # 库最多保留篇数
UA = "TOEFLStudyApp/1.0 (educational study project)"

GEO, PALEO, CLIM = "Geology & Earth Science", "Paleontology & Evolution", "Climate History"
ASTRO, BIO, ENV = "Astronomy & Space Science", "Biology & Ecology", "Environmental Science"
ANTHRO, NEURO, HIST = "Anthropology & Archaeology", "Neuroscience & Psychology", "History & Civilization"

ACADEMIC_TOPICS = [
    ("Plate_tectonics",GEO),("Subduction",GEO),("Mid-ocean_ridge",GEO),("Earthquake",GEO),("Volcano",GEO),
    ("Igneous_rock",GEO),("Sedimentary_rock",GEO),("Metamorphic_rock",GEO),("Mineral",GEO),("Erosion",GEO),
    ("Weathering",GEO),("Soil",GEO),("Groundwater",GEO),("Geothermal_power",GEO),("Paleomagnetism",GEO),
    ("Geologic_time_scale",GEO),("Stratum",GEO),
    ("Fossil",PALEO),("Dinosaur",PALEO),("Trilobite",PALEO),("Ammonite",PALEO),("Evolution",PALEO),
    ("Natural_selection",PALEO),("Speciation",PALEO),("Mass_extinction",PALEO),
    ("Permian-Triassic_extinction_event",PALEO),("Cretaceous-Paleogene_extinction_event",PALEO),
    ("Burgess_Shale",PALEO),("Neanderthal",PALEO),("Homo_habilis",PALEO),("Tiktaalik",PALEO),
    ("Darwin's_finches",PALEO),("Evolution_of_the_eye",PALEO),("Evolution_of_cetaceans",PALEO),
    ("Stone_Age",PALEO),
    ("Ice_age",CLIM),("Little_Ice_Age",CLIM),("Global_warming",CLIM),("Greenhouse_effect",CLIM),
    ("El_Niño",CLIM),("Monsoon",CLIM),("Drought",CLIM),("Desertification",CLIM),("Sea_level_rise",CLIM),
    ("Gulf_Stream",CLIM),("Maunder_Minimum",CLIM),("Dendrochronology",CLIM),("Paleoclimatology",CLIM),
    ("Milankovitch_cycles",CLIM),("Year_Without_a_Summer",CLIM),
    ("Solar_System",ASTRO),("Sun",ASTRO),("Moon",ASTRO),("Mars",ASTRO),("Atmosphere_of_Mars",ASTRO),
    ("Jupiter",ASTRO),("Great_Red_Spot",ASTRO),("Asteroid",ASTRO),("Comet",ASTRO),("Meteorite",ASTRO),
    ("Impact_event",ASTRO),("Black_hole",ASTRO),("Supernova",ASTRO),("Nebula",ASTRO),("Galaxy",ASTRO),
    ("Milky_Way",ASTRO),("Exoplanet",ASTRO),("Hubble_Space_Telescope",ASTRO),("Solar_eclipse",ASTRO),("Aurora",ASTRO),
    ("Photosynthesis",BIO),("DNA",BIO),("Bacteria",BIO),("Virus",BIO),("Fungus",BIO),("Pollination",BIO),
    ("Seed_dispersal",BIO),("Symbiosis",BIO),("Mitochondrion",BIO),("Chloroplast",BIO),("Circadian_rhythm",BIO),
    ("Hibernation",BIO),("Camouflage",BIO),("Mimicry",BIO),("Bioluminescence",BIO),("Echolocation",BIO),
    ("Bat",BIO),("Whale",BIO),("Beaver",BIO),("Western_honey_bee",BIO),("Bird_migration",BIO),("Insect",BIO),
    ("Coral_reef",BIO),("Ecological_succession",BIO),("Food_web",BIO),("Ecosystem",BIO),("Biodiversity",BIO),
    ("Invasive_species",BIO),("Nitrogen_cycle",BIO),("Carbon_cycle",BIO),("Water_cycle",BIO),("Wetland",BIO),
    ("Mangrove",BIO),("Tropical_rainforest",BIO),("Tundra",BIO),("Permafrost",BIO),("Savanna",BIO),("Overfishing",BIO),
    ("Coral_bleaching",ENV),("Ocean_acidification",ENV),("Deforestation",ENV),("Urban_heat_island",ENV),
    ("Maya_civilization",ANTHRO),("Aztec",ANTHRO),("Inca_Empire",ANTHRO),("Ancient_Egypt",ANTHRO),
    ("Mesopotamia",ANTHRO),("Indus_Valley_Civilisation",ANTHRO),("Stonehenge",ANTHRO),("Cahokia",ANTHRO),
    ("Chaco_Canyon",ANTHRO),("Nazca_Lines",ANTHRO),("Easter_Island",ANTHRO),("Silk_Road",ANTHRO),
    ("Cuneiform",ANTHRO),("Writing_system",ANTHRO),("Viking_Age",ANTHRO),("Clovis_culture",ANTHRO),
    ("Bering_land_bridge",ANTHRO),("Cave_painting",ANTHRO),("Göbekli_Tepe",ANTHRO),("Domestication",ANTHRO),
    ("Domestication_of_the_horse",ANTHRO),
    ("Memory",NEURO),("Sleep",NEURO),("Brain",NEURO),("Neuron",NEURO),("Neuroplasticity",NEURO),
    ("Classical_conditioning",NEURO),("Placebo",NEURO),("Amnesia",NEURO),("Dream",NEURO),
    ("Lateralization_of_brain_function",NEURO),("Visual_cortex",NEURO),
    ("Industrial_Revolution",HIST),("Printing_press",HIST),("History_of_agriculture",HIST),("Irrigation",HIST),
    ("Aqueduct",HIST),("Great_Wall_of_China",HIST),("Columbian_Exchange",HIST),("Money",HIST),
    ("Origin_of_language",HIST),("Proto-Indo-European_language",HIST),
]

GLOSSARY = {
    "tectonic":"板块构造的","crust":"地壳","mantle":"地幔","sediment":"沉积物","fossil":"化石",
    "extinction":"灭绝","glacier":"冰川","climate":"气候","atmosphere":"大气层","ecosystem":"生态系统",
    "evolution":"演化","adaptation":"适应","photosynthesis":"光合作用","oxygen":"氧气","carbon":"碳",
    "radiation":"辐射","archaeology":"考古学","settlement":"定居点","arid":"干旱的","erosion":"侵蚀",
    "isotope":"同位素","carbonate":"碳酸盐","precipitation":"降水","biodiversity":"生物多样性",
    "predator":"捕食者","habitat":"栖息地","volcanic":"火山的","species":"物种","nutrient":"营养物质"
}

def norm(s):
    return re.sub(r"\s+", "_", (s or "").strip()).lower()

def extract_terms(text):
    terms, low = [], text.lower()
    for term, cn in GLOSSARY.items():
        if re.search(r"\b" + term + r"\b", low):
            terms.append([term, cn])
            if len(terms) >= 6:
                break
    return terms or [["evidence","证据"],["hypothesis","假说"]]

def api_extract(title):
    api = ("https://en.wikipedia.org/w/api.php?action=query&prop=extracts"
           "&explaintext=1&redirects=1&format=json&titles=" + urllib.parse.quote(title))
    req = urllib.request.Request(api, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    pages = data.get("query", {}).get("pages", {})
    if not pages:
        return None, ""
    page = list(pages.values())[0]
    return page.get("title", title), page.get("extract", "")

def build_article(title, cat):
    real_title, extract = api_extract(title)
    if not extract:
        return None
    paras, total = [], 0
    for p in extract.split("\n"):
        p = re.sub(r"\s+", " ", p).strip()
        if not p or p.startswith("="):
            continue
        if len(p.split()) < 15:
            continue
        paras.append(p)
        total += len(p.split())
        if total >= TARGET_WORDS:
            break
    if total < MIN_WORDS:
        return None
    text = " ".join(paras)
    return {"title": real_title, "cat": cat, "terms": extract_terms(text), "paras": paras}

def random_title():
    req = urllib.request.Request(
        "https://en.wikipedia.org/api/rest_v1/page/random/summary",
        headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("title")

def main():
    try:
        with open(ARTICLES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = []
    seen = set(norm(a.get("title")) for a in data)

    art = None
    # 1) 优先抓还没用过的托福经典学术主题
    unused = [t for t in ACADEMIC_TOPICS if norm(t[0]) not in seen]
    random.shuffle(unused)
    for topic, cat in unused[:5]:
        try:
            art = build_article(topic, cat)
        except Exception as e:
            print("抓取失败", topic, e)
        if art:
            break
    # 2) 经典主题全部用完后，从维基随机条目里抽（够长才入库，永不枯竭）
    if not art:
        for _ in range(6):
            try:
                t = random_title()
                if t and norm(t) not in seen:
                    art = build_article(t, "General Academic Reading")
            except Exception as e:
                print("随机抓取失败", e)
            if art:
                break

    # 清理过短老文章 + 去重
    cleaned, seen2 = [], set()
    for a in data:
        wc = len(" ".join(a.get("paras", [])).split())
        k = norm(a.get("title"))
        if wc >= MIN_WORDS and k not in seen2:
            seen2.add(k)
            cleaned.append(a)

    if art:
        cleaned.insert(0, art)
        print("✅ 今日新文章：%s（约 %d 词）" % (art["title"], len(" ".join(art["paras"]).split())))
    else:
        print("今日未获取到新文章（网络波动），库存文章不受影响。")

    cleaned = cleaned[:MAX_KEEP]
    with open(ARTICLES_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)
    print("文章库现共 %d 篇" % len(cleaned))

if __name__ == "__main__":
    main()
