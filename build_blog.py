#!/usr/bin/env python3
"""Build blog pages from posts/*.md (needs pandoc).

Front matter per post:
---
title: ...
date: YYYY-MM-DD
tags: [Tag A, Tag B]
summary: one line
---
Run:  python3 build_blog.py
"""
import re, subprocess, html, pathlib
root = pathlib.Path(__file__).parent
tpl = (root / "index.html").read_text()

def page(body, active):
    s = re.sub(r"<main>.*?</main>", lambda m: "<main>\n" + body + "\n</main>", tpl, flags=re.S)
    s = s.replace(' class="active"', "")
    s = s.replace(f'<a href="{active}">', f'<a href="{active}" class="active">')
    return s

def meta(text):
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    d, body = {}, text
    if m:
        for line in m.group(1).splitlines():
            k, _, v = line.partition(":")
            d[k.strip()] = v.strip()
        body = m.group(2)
    d["tags"] = [t.strip() for t in d.get("tags", "").strip("[]").split(",") if t.strip()]
    return d, body

posts = []
for f in sorted((root / "posts").glob("*.md")):
    d, body = meta(f.read_text())
    slug = f.stem
    content = subprocess.run(["pandoc", "-f", "markdown", "-t", "html", "--mathml"],
                             input=body, capture_output=True, text=True, check=True).stdout
    tags = "".join(f'<a class="tag" href="blog.html#{html.escape(t)}">{html.escape(t)}</a>' for t in d["tags"])
    out = f'<article class="post"><h2>{html.escape(d.get("title", slug))}</h2><p class="meta">{d.get("date","")}</p><p class="tags">{tags}</p>{content}<p><a href="blog.html">← All posts</a></p></article>'
    (root / f"post-{slug}.html").write_text(page(out, "blog.html"))
    posts.append((d, slug))

posts.sort(key=lambda p: p[0].get("date", ""), reverse=True)
alltags = sorted({t for d, _ in posts for t in d["tags"]})
chips = '<button class="tag on" data-tag="">All</button>' + "".join(
    f'<button class="tag" data-tag="{html.escape(t)}">{html.escape(t)}</button>' for t in alltags)
items = ""
for d, slug in posts:
    tg = "".join(f'<span class="tag sm">{html.escape(t)}</span>' for t in d["tags"])
    items += (f'<li data-tags="{html.escape("|".join(d["tags"]))}"><span class="date">{d.get("date","")}</span>'
              f'<div><a class="ptitle" href="post-{slug}.html">{html.escape(d.get("title", slug))}</a>'
              f'<div class="authors">{html.escape(d.get("summary",""))}</div><div class="tags">{tg}</div></div></li>')
script = """<script>
const chips=[...document.querySelectorAll('button.tag')],items=[...document.querySelectorAll('.bloglist li')];
function show(t){chips.forEach(c=>c.classList.toggle('on',c.dataset.tag===t));
items.forEach(li=>li.style.display=(!t||li.dataset.tags.split('|').includes(t))?'':'none');}
chips.forEach(c=>c.onclick=()=>{location.hash=c.dataset.tag;show(c.dataset.tag)});
show(decodeURIComponent(location.hash.slice(1)));
</script>"""
(root / "blog.html").write_text(page(f'<h2>Blog</h2><div class="filters">{chips}</div><ul class="bloglist">{items}</ul>{script}', "blog.html"))
print(f"Built {len(posts)} post(s); tags: {alltags}")
