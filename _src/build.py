#!/usr/bin/env python3
"""Build diegomotion.net static site: _src/ (templates + content) -> repo root (GitHub Pages deploy root).
Run: python3 _src/build.py
"""
import json, os, re, shutil, datetime, html as H
from jinja2 import Environment, FileSystemLoader, select_autoescape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = ROOT
CONTENT = json.load(open(os.path.join(HERE, "content.json")))
ASSETS = json.load(open(os.path.join(HERE, "content", "assets.json")))
EXTRACTED = json.load(open(os.path.join(HERE, "content", "pages.json")))
VIDEOS = json.load(open(os.path.join(HERE, "videos.json")))
BASE_URL = CONTENT["site"]["url"]

env = Environment(loader=FileSystemLoader(os.path.join(HERE, "templates")), autoescape=select_autoescape(["html"]), trim_blocks=True, lstrip_blocks=True)

def asset(url):
    """Map a Squarespace image URL to local asset entry (or None)."""
    if not url: return None
    u = url.split("?")[0]
    if u.startswith("//"): u = "https:" + u
    for cand in (u, u.replace("https://", "http://", 1), u.replace("http://", "https://", 1)):
        if cand in ASSETS: return ASSETS[cand]
    return None

def clean_html(s):
    """Tidy extracted rich text: fix stray <b> tags, map legacy links."""
    if not s: return ""
    s = re.sub(r'<b>(<b>)*', '<br>', s)
    s = s.replace('href="/about-1"', 'href="/bio/"')
    s = re.sub(r'href="(/[a-z0-9-]+(?:/[a-z0-9-]+)?)"', lambda m: f'href="{m.group(1)}/"' if not m.group(1).endswith("/") else m.group(0), s)
    s = s.replace("&nbsp;", " ")
    return s

env.filters["asset"] = asset
env.filters["clean"] = clean_html

def video(key):
    v = dict(VIDEOS[key]); v["key"] = key
    return v
env.globals["video"] = video
env.globals["now_year"] = datetime.date.today().year
env.globals["r2"] = os.environ.get("R2_PUBLIC") or CONTENT["site"].get("r2_public") or ""
env.globals["vidname"] = {v["id"]: k for k, v in json.load(open(os.path.join(HERE, "content", "video_manifest.json"))).items()}

def write(path, html):
    out = os.path.join(SITE, path.strip("/"), "index.html") if not path.endswith(".html") else os.path.join(SITE, path.strip("/"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w").write(html)

def render(template, path, **ctx):
    t = env.get_template(template)
    canonical = BASE_URL + (path if path.endswith("/") or path == "/" else path + "/")
    html = t.render(site=CONTENT["site"], nav=CONTENT["nav"], footer=CONTENT["footer"], canonical=canonical, path=path, **ctx)
    write(path, html)
    return canonical

pages_out = []

# ---- Home
home = CONTENT["home"]
pages_out.append(render("home.html", "/", page=home, title=home["title"], description=home["description"], og_image=home["og_image"]))

# ---- Simple pages (sections rendered generically from the extracted model)
for slug, meta in CONTENT["pages"].items():
    ex = EXTRACTED[meta["source"]]
    pages_out.append(render("page.html", meta["path"], page=meta, sections=ex["sections"], title=meta["title"], description=meta["description"], og_image=meta.get("og_image")))

# ---- Portfolio collections + items
for coll in CONTENT["portfolio"]:
    ex = EXTRACTED[coll["source"]]
    items = []
    for it in ex["portfolio"]:
        slug = it["href"].rstrip("/").split("/")[-1]
        item_ex = EXTRACTED[coll["source"] + "__" + slug]
        items.append({"slug": slug, "title": it["title"], "thumb": it["src"], "path": f"{coll['path']}{slug}/", "sections": item_ex["sections"], "page_title": item_ex["title"]})
    pages_out.append(render("portfolio.html", coll["path"], coll=coll, items=items, title=coll["title"], description=coll["description"]))
    for i, it in enumerate(items):
        prev_item = items[i - 1] if i > 0 else None
        next_item = items[i + 1] if i < len(items) - 1 else None
        pages_out.append(render("portfolio_item.html", it["path"], coll=coll, item=it, prev_item=prev_item, next_item=next_item,
                                title=f"{it['title']} — {coll['title']}", description=coll["item_description"].format(title=it["title"])))

# ---- 404, robots, sitemap, CNAME, .nojekyll
render("404.html", "/404.html", title="Page not found", description="")
open(os.path.join(SITE, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n")
today = datetime.date.today().isoformat()
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in pages_out:
    sm.append(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>")
sm.append("</urlset>")
open(os.path.join(SITE, "sitemap.xml"), "w").write("\n".join(sm) + "\n")
open(os.path.join(SITE, ".nojekyll"), "w").write("")
open(os.path.join(SITE, "CNAME"), "w").write("diegomotion.net\n")

# static files
for d in ("css", "js", "fonts"):
    src = os.path.join(HERE, "static", d); dst = os.path.join(SITE, "assets", d)
    if os.path.isdir(src):
        if os.path.isdir(dst): shutil.rmtree(dst)
        shutil.copytree(src, dst)
print(f"built {len(pages_out)} pages -> {SITE}")
