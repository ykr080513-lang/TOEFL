# -*- coding: utf-8 -*-
import json, re, random, urllib.request, urllib.parse

ARTICLES_FILE = "articles.json"
TARGET_WORDS = 500   # 每篇文章目标词数（想读长一点可改成 800/1000）
MIN_WORDS = 200      # 低于这个词数的旧文章会被自动清理
MAX_KEEP = 365       # 文章库最多保留篇数

ACADEMIC_TOPICS = [
    ("Plate_tectonics", "Geology & Earth Science"),
    ("Cretaceous-Paleogene_extinction_event", "Paleontology & Evolution"),
    ("Glacial_period", "Climate History"),
    ("Atmosphere_of_Mars", "Astronomy & Planetary Science"),
    ("Maya_civilization", "Anthropology & Archaeology"),
    ("Photosynthesis", "Biology & Biochemistry"),
    ("Great_Oxidation_Event", "Geochemistry & Evolution"),
    ("Ocean_acidification", "Marine Biology & Ecology"),
    ("Continental_drift", "Geology & Geophysics"),
    ("Deep_sea_exploration", "Oceanography"),
    ("Domestication_of_the_horse", "Anthropology & History"),
    ("Permian-Triassic_extinction_event", "Paleontology"),
    ("Urban_heat_island", "Environmental Science"),
    ("Hydrothermal_vent", "Marine Biology"),
    ("Solar_wind", "Astronomy & Space Physics"),
    ("Little_Ice_Age", "Climate History"),
    ("La_Brea_Tar_Pits", "Paleontology & Archaeology"),
    ("Coral_bleaching", "Marine Biology & Ecology"),
]

GLOSSARY = {
    "tectonic": "板块构造的", "crust": "地壳", "mantle": "地幔",
    "sediment": "沉积物", "fossil": "化石", "extinction": "灭绝",
    "glacier": "冰川", "climate": "气候", "atmosphere": "大气层",
    "ecosystem": "生态系统", "evolution": "演化", "adaptation": "适应",
    "photosynthesis": "光合作用", "oxygen": "氧气", "carbon": "碳",
    "radiation": "辐射", "archaeology": "考古学", "settlement": "定居点",
    "arid": "干旱的", "erosion": "侵蚀", "isotope": "同位素",
    "carbonate": "碳酸盐", "precipitation": "降水", "biodiversity": "生物多样性",
    "predator": "捕食者", "habitat": "栖息地", "volcanic": "火山的"
}

def extract_terms(text):
    terms, low = [], text.lower()
    for term, cn in GLOSSARY.items():
        if re.search(r"\b" + term + r"\b", low):
            terms.append([term, cn])
            if len(terms) >= 6:
                break
    return terms or [["evidence", "证据"], ["hypothesis", "假说"]]

def fetch_full_article():
    topic, cat = random.choice(ACADEMIC_TOPICS)
    headers = {"User-Agent": "TOEFLStudyApp/1.0 (educational study project)"}
    api = ("https://en.wikipedia.org/w/api.php?action=query&prop=extracts"
           "&explaintext=1&redirects=1&format=json&titles="
           + urllib.parse.quote(topic))
    req = urllib.request.Request(api, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    pages = data.get("query", {}).get("pages", {})
    if not pages:
        return None
    page = list(pages.values())[0]
    title = page.get("title", topic.replace("_", " "))
    extract = page.get("extract", "")

    # 从完整正文里按段落累积，凑到 500 词左右为止（跳过标题行和碎句）
    paras, total = [], 0
    for p in extract.split("\n"):
        p = re.sub(r"\s+", " ", p).strip()
        if not p or p.startswith("="):
            continue
        w = len(p.split())
        if w < 15:
            continue
        paras.append(p)
        total += w
        if total >= TARGET_WORDS:
            break
    if total < MIN_WORDS:
        return None
    return {"title": title, "cat": cat, "terms": extract_terms(" ".join(paras)), "paras": paras}

def word_count(a):
    return len(" ".join(a.get("paras", [])).split())

def main():
    art = None
    for _ in range(5):          # 最多换 5 个主题尝试
        try:
            art = fetch_full_article()
        except Exception as e:
            print("抓取失败，换下一个主题：", e)
        if art:
            break

    try:
        with open(ARTICLES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = []

    # 顺手清理：删掉过短的老文章、去重
    seen, cleaned = set(), []
    for a in data:
        if word_count(a) >= MIN_WORDS and a.get("title") not in seen:
            seen.add(a.get("title"))
            cleaned.append(a)

    if art and art["title"] not in seen:
        cleaned.insert(0, art)
        print("✅ 新文章：%s（约 %d 词）" % (art["title"], word_count(art)))
    else:
        print("今日文章已存在或抓取失败，仅完成清理。")

    cleaned = cleaned[:MAX_KEEP]
    with open(ARTICLES_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)
    print("文章库现共 %d 篇，每篇 ≥ %d 词" % (len(cleaned), MIN_WORDS))

if __name__ == "__main__":
    main()
