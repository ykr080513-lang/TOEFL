# -*- coding: utf-8 -*-
import json, re, urllib.request, xml.etree.ElementTree as ET
from html import unescape

ARTICLES_FILE = "articles.json"
FEED_URL = "https://phys.org/rss-feed/earth-news/earth-sciences/"  # 地球科学/地质，最经典的托福高频话题

def clean_html(raw):
    text = re.sub(r'<[^>]+>', ' ', raw or '')
    return unescape(text).strip()

def fetch_daily():
    req = urllib.request.Request(FEED_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        xml_data = resp.read()

    root = ET.fromstring(xml_data)
    items = root.findall(".//item")
    if not items:
        return None

    # 获取最新一篇真实学术新闻
    item = items[0]
    title = clean_html(item.findtext("title"))
    link = item.findtext("link")
    desc = clean_html(item.findtext("description"))

    # 抓取正文
    req_page = urllib.request.Request(link, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req_page, timeout=15) as resp:
        page_html = resp.read().decode('utf-8', errors='ignore')

    # 提取文章正文段落
    p_matches = re.findall(r'<p[^>]*>(.*?)</p>', page_html, re.S)
    paras = []
    for p in p_matches:
        txt = clean_html(p)
        # 过滤广告与版权声明短句，保留实质段落
        if len(txt) > 80 and not any(k in txt.lower() for k in ["copyright", "cookie", "subscribe", "terms of use", "journal reference"]):
            paras.append(txt)

    if len(paras) < 3:
        paras = [desc] if desc else ["Content could not be retrieved."]

    # 识别常见的托福核心学科专业术语（示例释义表）
    academic_glossary = {
        "sediment": "沉积物", "tectonic": "地壳构造的", "crust": "地壳",
        "erosion": "侵蚀", "glacier": "冰川", "strata": "地层",
        "volcanic": "火山的", "ecosystem": "生态系统", "precipitation": "降水",
        "fossil": "化石", "atmosphere": "大气层", "isotope": "同位素",
        "carbonate": "碳酸盐", "methane": "甲烷", "subduction": "俯冲作用",
        "permeable": "可渗透的", "mantle": "地幔", "arid": "干旱的"
    }

    full_text = " ".join(paras).lower()
    terms = []
    for term, cn in academic_glossary.items():
        if re.search(r'\b' + term + r'\b', full_text):
            terms.append([term, cn])
            if len(terms) >= 5:
                break

    return {
        "title": title,
        "cat": "Earth & Environmental Sciences",
        "terms": terms if terms else [["research", "研究"], ["evidence", "证据"]],
        "paras": paras[:8]  # 控制在 800 - 1000 词左右的学术阅读量
    }

if __name__ == "__main__":
    new_art = fetch_daily()
    if not new_art:
        print("未抓取到内容")
        exit(0)

    try:
        with open(ARTICLES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = []

    # 避免重复加入相同文章
    existing_titles = set(a.get("title") for a in data)
    if new_art["title"] not in existing_titles:
        data.insert(0, new_art) # 最新文章置顶
        with open(ARTICLES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"成功更新今日最新托福阅读：{new_art['title']}")
    else:
        print("今日文章已存在，无需重复写入。")
