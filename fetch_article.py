# -*- coding: utf-8 -*-
import json, re, urllib.request, xml.etree.ElementTree as ET
from html import unescape

ARTICLES_FILE = "articles.json"

# 多个权威学术科普 RSS 源（托福高频话题：地球科学、生物演化、天文考古）
FEEDS = [
    ("https://www.sciencedaily.com/rss/earth_climate.xml", "Earth & Climate Science"),
    ("https://www.sciencedaily.com/rss/plants_animals.xml", "Biology & Evolution"),
    ("https://theconversation.com/global/topics/science-31/articles.atom", "Academic Science"),
    ("https://science.nasa.gov/feed/", "Astronomy & Planetary Science")
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

def clean_html(raw):
    text = re.sub(r'<[^>]+>', ' ', raw or '')
    return unescape(text).strip()

def fetch_from_rss(feed_url, default_cat):
    req = urllib.request.Request(feed_url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as resp:
        content = resp.read()

    root = ET.fromstring(content)
    # 兼容 RSS 2.0 与 Atom 格式
    items = root.findall(".//item")
    if not items:
        # 尝试 Atom entry
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall(".//atom:entry", ns)
        if entries:
            e = entries[0]
            title = clean_html(e.findtext("atom:title", namespaces=ns))
            summary = clean_html(e.findtext("atom:summary", namespaces=ns) or e.findtext("atom:content", namespaces=ns))
            return title, summary, default_cat
        return None

    for item in items[:3]:
        title = clean_html(item.findtext("title"))
        desc = clean_html(item.findtext("description"))
        if title and desc and len(desc) > 80:
            return title, desc, default_cat
    return None

def split_into_paras(text):
    # 将文本按照长句与标点整理成 3-5 个段落，符合托福篇章结构
    sentences = re.split(r'(?<=[.!?])\s+', text)
    paras = []
    chunk = []
    cur_len = 0
    for s in sentences:
        chunk.append(s)
        cur_len += len(s.split())
        if cur_len >= 120:
            paras.append(" ".join(chunk))
            chunk = []
            cur_len = 0
    if chunk:
        paras.append(" ".join(chunk))
    return paras if len(paras) >= 2 else [text]

def extract_terms(text):
    # 托福学术核心高频词表
    academic_glossary = {
        "sediment": "沉积物", "tectonic": "地壳构造的", "crust": "地壳",
        "erosion": "侵蚀", "glacier": "冰川", "strata": "地层",
        "volcanic": "火山的", "ecosystem": "生态系统", "precipitation": "降水",
        "fossil": "化石", "atmosphere": "大气层", "isotope": "同位素",
        "carbonate": "碳酸盐", "methane": "甲烷", "subduction": "俯冲作用",
        "permeable": "可渗透的", "mantle": "地幔", "arid": "干旱的",
        "evolution": "演化", "adaptation": "适应", "biodiversity": "生物多样性",
        "predator": "捕食者", "photosynthesis": "光合作用", "habitat": "栖息地"
    }
    terms = []
    lower_txt = text.lower()
    for term, cn in academic_glossary.items():
        if re.search(r'\b' + term + r'\b', lower_txt):
            terms.append([term, cn])
            if len(terms) >= 5:
                break
    return terms or [["evidence", "证据"], ["hypothesis", "假说"]]

def main():
    fetched = None
    for feed_url, cat in FEEDS:
        try:
            print(f"正在尝试抓取源: {feed_url} ...")
            res = fetch_from_rss(feed_url, cat)
            if res:
                fetched = res
                print(f"抓取成功: {res[0][:40]}...")
                break
        except Exception as e:
            print(f"该源抓取跳过: {e}")
            continue

    if not fetched:
        print("所有源均未获取到新内容，保持原有文章库不变。")
        return

    title, content, cat = fetched
    paras = split_into_paras(content)
    terms = extract_terms(content)

    new_art = {
        "title": title,
        "cat": cat,
        "terms": terms,
        "paras": paras
    }

    try:
        with open(ARTICLES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = []

    existing_titles = set(a.get("title") for a in data)
    if new_art["title"] not in existing_titles:
        data.insert(0, new_art)
        with open(ARTICLES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 成功写入今日托福新文章: {new_art['title']}")
    else:
        print("今日文章已存在，无需重复写入。")

if __name__ == "__main__":
    main()
