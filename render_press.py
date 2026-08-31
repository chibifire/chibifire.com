#!/usr/bin/env python3
"""Render the presskit data.xml files into static HTML under build/press.

Content is preserved verbatim from the source data.xml — this is a move of the
old chibifire.com presskit into the chibifire visual language, not a rewrite.
"""
import html
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "build" / "press"

CSS = """
:root{--ground:#f7f5f2;--surface:#fff;--surface-2:#fbfaf8;--ink:#211c2b;--muted:#6f6a78;
--faint:#a09aa6;--border:#ebe6df;--border-strong:#ddd5ca;--brass:#9a7638;--ember:#d3521f;
--ember-ink:#b8420f;--ember-soft:#fbe9df;--radius:16px;--maxw:960px;
--shadow:0 1px 2px rgba(33,28,43,.04),0 6px 20px -12px rgba(33,28,43,.14);}
@media (prefers-color-scheme:dark){:root{--ground:#141019;--surface:#1e1925;--surface-2:#251f2f;
--ink:#ece7f1;--muted:#a49daf;--faint:#6f6879;--border:#2e2839;--border-strong:#3b3448;
--brass:#c8a460;--ember:#f06a3d;--ember-ink:#f06a3d;--ember-soft:#38231a;
--shadow:0 1px 2px rgba(0,0,0,.3),0 10px 30px -14px rgba(0,0,0,.6);}}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);
font-family:"Hanken Grotesk",system-ui,-apple-system,sans-serif;font-size:16px;line-height:1.6;
-webkit-font-smoothing:antialiased}
a{color:var(--ember-ink);text-decoration:none}a:hover{text-decoration:underline;text-underline-offset:3px}
.wrap{max-width:var(--maxw);margin:0 auto;padding:0 24px}
header.bar{position:sticky;top:0;z-index:9;background:color-mix(in srgb,var(--ground) 88%,transparent);
backdrop-filter:saturate(1.4) blur(12px);border-bottom:1px solid var(--border)}
.bar-in{display:flex;align-items:center;gap:12px;height:58px}
.mark{display:flex;align-items:center;gap:9px;font-weight:700;color:var(--ink)}
.mark .name b{color:var(--ember-ink)}
.bar .sep{color:var(--border-strong)}.bar .page{font-family:"Fraunces",Georgia,serif;font-size:16px}
.bar .spacer{flex:1}.bar a.back{color:var(--muted);font-size:14px;font-weight:600}
.hero{padding:48px 0 12px}
.hero .eyebrow{font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:var(--brass);
font-weight:600;margin:0 0 12px}
.hero h1{font-family:"Fraunces",Georgia,serif;font-weight:500;font-size:clamp(30px,5vw,44px);
line-height:1.05;letter-spacing:-.015em;margin:0;text-wrap:balance}
.hero .facts{display:flex;flex-wrap:wrap;gap:6px 20px;margin-top:18px;color:var(--muted);font-size:14px}
.hero .facts b{color:var(--ink);font-weight:600}
.lede{font-size:18px;color:var(--ink);max-width:66ch;margin:22px 0 0}
.section-label{font-family:"Fraunces",Georgia,serif;font-size:13px;letter-spacing:.02em;
color:var(--brass);text-transform:uppercase;margin:44px 0 16px;font-weight:600}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:18px;padding-bottom:12px}
@media (max-width:640px){.grid{grid-template-columns:1fr}}
.pcard{display:flex;flex-direction:column;background:var(--surface);border:1px solid var(--border);
border-radius:var(--radius);box-shadow:var(--shadow);overflow:hidden;transition:border-color .15s}
.pcard:hover{border-color:var(--brass)}
.pcard .thumb{aspect-ratio:16/9;background:var(--surface-2) center/cover no-repeat;border-bottom:1px solid var(--border)}
.pcard .body{padding:16px 18px 18px}
.pcard h3{font-family:"Fraunces",Georgia,serif;font-weight:500;font-size:19px;margin:0 0 6px;color:var(--ink)}
.pcard p{margin:0;color:var(--muted);font-size:14px}
.pcard .when{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:11.5px;color:var(--faint);
letter-spacing:.02em;margin-bottom:8px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);
box-shadow:var(--shadow);padding:22px 24px;margin-bottom:18px}
.feat{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:10px}
.feat li{display:flex;gap:12px;align-items:flex-start}
.feat li::before{content:"";flex:none;width:7px;height:7px;border-radius:2px;margin-top:9px;
background:var(--ember);transform:rotate(45deg)}
.kvs{display:flex;flex-direction:column;gap:0}
.kvs .r{display:flex;gap:14px;padding:10px 0;border-top:1px solid var(--border);font-size:14.5px}
.kvs .r:first-child{border-top:none}.kvs .r .k{color:var(--muted);min-width:130px;flex:none}
.credit{display:flex;justify-content:space-between;gap:14px;padding:9px 0;border-top:1px solid var(--border)}
.credit:first-child{border-top:none}.credit .role{color:var(--muted);font-size:14px}
figure{margin:0 0 18px}figure img,figure video{width:100%;border-radius:var(--radius);border:1px solid var(--border);display:block}
footer{border-top:1px solid var(--border);margin-top:40px;padding:24px 0 60px;color:var(--muted);font-size:13px}
footer .frow{display:flex;flex-wrap:wrap;gap:8px 18px;align-items:center}footer .spacer{flex:1}
footer a{color:var(--muted)}
:focus-visible{outline:2px solid var(--ember);outline-offset:2px}
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&'
         'family=Hanken+Grotesk:wght@400;500;600;700&'
         'family=JetBrains+Mono:wght@400;500&display=swap">')

FLAME = ('<svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true">'
         '<defs><linearGradient id="fg" x1="12" y1="2" x2="12" y2="23" gradientUnits="userSpaceOnUse">'
         '<stop offset="0" stop-color="#f4a13a"/><stop offset=".55" stop-color="#e26a2c"/>'
         '<stop offset="1" stop-color="#c93f1c"/></linearGradient></defs>'
         '<path fill="url(#fg)" d="M13.4 2.1c.3 3-1.2 4.6-2.8 6.1C8.8 10 6.9 11.8 6.9 14.8a6.1 6.1 0 0 0 12.2.3'
         'c0-2.3-1-3.9-1.9-5.2-.3.9-.9 1.6-1.8 1.9.6-2.2-.2-4.6-1.4-6.2-.5-.7-1.1-1.3-1.6-1.5z"/></svg>')


def esc(s):
    return html.escape((s or "").strip())


def text(node, tag):
    el = node.find(tag)
    return el.text.strip() if el is not None and el.text else ""


def page(title, body, back=True):
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<title>{esc(title)}</title>'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">{FONTS}'
            f'<style>{CSS}</style></head><body>'
            f'<header class="bar"><div class="wrap bar-in">'
            f'<span class="mark">{FLAME}<span class="name">chibi<b>fire</b></span></span>'
            f'<span class="sep">/</span><span class="page">Press</span><span class="spacer"></span>'
            + ('<a class="back" href="/press/">All work</a>' if back else '<a class="back" href="/">Home</a>')
            + f'</div></header>{body}</body></html>')


def slug(dirname):
    # dated dirs -> drop the leading date for a clean URL
    parts = dirname.split("-")
    if len(parts) >= 3 and parts[0].isdigit() and len(parts[0]) == 4:
        return "-".join(parts[3:]) or dirname
    return dirname


def project_dirs():
    for p in sorted(ROOT.iterdir(), reverse=True):
        if p.is_dir() and (p / "data.xml").exists() and p.name not in ("build",):
            yield p


def render_project(pdir):
    root = ET.parse(pdir / "data.xml").getroot()
    title = text(root, "title") or pdir.name
    website = text(root, "website")
    desc = text(root, "description")
    out = OUT / slug(pdir.name)
    out.mkdir(parents=True, exist_ok=True)

    # media
    media = ""
    imgdir = pdir / "images"
    copied = []
    if imgdir.is_dir():
        for f in sorted(imgdir.iterdir()):
            if f.is_file() and not f.name.startswith("."):
                shutil.copy(f, out / f.name)
                copied.append(f.name)
    for name in copied:
        low = name.lower()
        if low.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
            media += f'<figure><img src="{esc(name)}" alt="{esc(title)}"></figure>'
        elif low.endswith((".mp4", ".webm")):
            media += f'<figure><video controls src="{esc(name)}"></video></figure>'

    feats = root.find("features")
    feat_html = ""
    if feats is not None:
        items = "".join(f"<li>{esc(f.text)}</li>" for f in feats.findall("feature") if f.text)
        if items:
            feat_html = f'<div class="section-label">Features</div><div class="card"><ul class="feat">{items}</ul></div>'

    credits = root.find("credits")
    credit_html = ""
    if credits is not None:
        rows = ""
        for c in credits.findall("credit"):
            person = text(c, "person")
            role = text(c, "role")
            if person or role:
                rows += f'<div class="credit"><span>{esc(person)}</span><span class="role">{esc(role)}</span></div>'
        if rows:
            credit_html = f'<div class="section-label">Credits</div><div class="card">{rows}</div>'

    additionals = root.find("additionals")
    add_html = ""
    if additionals is not None:
        rows = ""
        for a in additionals.findall("additional"):
            name = text(a, "name")
            link = text(a, "link")
            val = f'<a href="{esc(link)}">{esc(link)}</a>' if link else ""
            rows += f'<div class="r"><span class="k">{esc(name)}</span><span>{val}</span></div>'
        if rows:
            add_html = f'<div class="section-label">Additional links</div><div class="card"><div class="kvs">{rows}</div></div>'

    socials = root.find("socials")
    soc_html = ""
    if socials is not None:
        rows = ""
        for s in socials.findall("social"):
            name = text(s, "name")
            link = text(s, "link")
            rows += f'<div class="r"><span class="k">{esc(name)}</span><span><a href="{esc(link)}">{esc(link)}</a></span></div>'
        if rows:
            soc_html = f'<div class="section-label">Links</div><div class="card"><div class="kvs">{rows}</div></div>'

    web_fact = f'<span><b>Website</b> <a href="{esc(website)}">{esc(website)}</a></span>' if website else ""
    body = (f'<main class="wrap"><section class="hero"><p class="eyebrow">Project</p>'
            f'<h1>{esc(title)}</h1><div class="facts">{web_fact}</div>'
            + (f'<p class="lede">{esc(desc)}</p>' if desc else "")
            + f'</section><section class="wrap" style="padding:24px 0 0">{media}{feat_html}{credit_html}{add_html}{soc_html}</section>'
            + footer() + '</main>')
    (out / "index.html").write_text(page(f"{title} — chibifire Press", body))
    return {"title": title, "slug": slug(pdir.name), "desc": desc, "dir": pdir.name,
            "thumb": next((n for n in copied if n.lower().startswith("header")), copied[0] if copied else None)}


def footer():
    return ('<footer class="wrap"><div class="frow">'
            f'<span class="mark">{FLAME}<span style="font-size:13px;color:var(--muted)">chibifire</span></span>'
            '<span>Press kit</span><span class="spacer"></span>'
            '<a href="/">Home</a><a href="https://account.chibifire.com">Account</a>'
            '<a href="mailto:ernest.lee@chibifire.com">Contact</a></div></footer>')


def render_index(projects):
    root = ET.parse(ROOT / "data.xml").getroot()
    title = text(root, "title")
    based = text(root, "based-in")
    founded = text(root, "founding-date")
    contact = text(root, "press-contact")
    desc = text(root, "description")

    histories = root.find("histories")
    hist_html = ""
    if histories is not None:
        rows = "".join(f'<div class="r"><span>{esc(text(h, "header") or (h.text or ""))}</span></div>'
                       for h in histories.findall("history"))
        if rows:
            hist_html = f'<div class="section-label">History</div><div class="card"><div class="kvs">{rows}</div></div>'

    socials = root.find("socials")
    soc_html = ""
    if socials is not None:
        rows = ""
        for s in socials.findall("social"):
            rows += f'<div class="r"><span class="k">{esc(text(s,"name"))}</span><span><a href="{esc(text(s,"link"))}">{esc(text(s,"link"))}</a></span></div>'
        soc_html = f'<div class="section-label">Links</div><div class="card"><div class="kvs">{rows}<div class="r"><span class="k">Press contact</span><span><a href="mailto:{esc(contact)}">{esc(contact)}</a></span></div></div></div>'

    cards = ""
    for p in projects:
        thumb = f'{p["slug"]}/{p["thumb"]}' if p["thumb"] else None
        style = f' style="background-image:url({thumb})"' if thumb else ""
        date = p["dir"].split("-")[:3]
        when = "-".join(date) if date[0].isdigit() and len(date[0]) == 4 else ""
        cards += (f'<a class="pcard" href="{p["slug"]}/"><div class="thumb"{style}></div>'
                  f'<div class="body">' + (f'<div class="when">{esc(when)}</div>' if when else "")
                  + f'<h3>{esc(p["title"])}</h3><p>{esc((p["desc"] or "")[:120])}</p></div></a>')

    body = (f'<main class="wrap"><section class="hero"><p class="eyebrow">Press kit</p>'
            f'<h1>{esc(title)}</h1>'
            f'<div class="facts"><span><b>Based in</b> {esc(based)}</span>'
            f'<span><b>Since</b> {esc(founded)}</span>'
            f'<span><b>Contact</b> <a href="mailto:{esc(contact)}">{esc(contact)}</a></span></div>'
            f'<p class="lede">{esc(desc)}</p></section>'
            f'<div class="section-label">Selected work</div><section class="grid">{cards}</section>'
            f'{hist_html}{soc_html}{footer()}</main>')
    (OUT / "index.html").write_text(page(f"{title} — Press", body, back=False))


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    projects = [render_project(d) for d in project_dirs()]
    render_index(projects)
    print(f"rendered {len(projects)} projects to {OUT}")


if __name__ == "__main__":
    main()
