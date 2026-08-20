"""Render docs/MANUAL.md into a single self-contained HTML page.

Images are inlined as data URIs because a published artifact runs under a strict
CSP that blocks every external host. Only the small subset of Markdown the
manual actually uses is supported -- headings, paragraphs, lists, tables, code
fences, blockquotes, rules, images, links and inline emphasis.
"""
import base64
import html
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "MANUAL.md")
OUT = os.path.join(HERE, "manual.html")


def data_uri(rel):
    path = os.path.join(HERE, rel)
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = os.path.splitext(rel)[1].lstrip(".").lower()
    return f"data:image/{'jpeg' if ext == 'jpg' else ext};base64,{b64}"


def slug(text):
    s = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    return re.sub(r"[\s_]+", "-", s)


def inline(text):
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", text)
    def link(m):
        label, href = m.group(1), m.group(2)
        if href.startswith("#"):
            return f'<a href="{href}">{label}</a>'
        return f'<a href="{href}" rel="noreferrer">{label}</a>'
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)
    return text


def convert(md):
    lines = md.split("\n")
    out, toc = [], []
    i = 0
    in_table = False

    def close_table():
        nonlocal in_table
        if in_table:
            out.append("</tbody></table></div>")
            in_table = False

    while i < len(lines):
        ln = lines[i]

        # fenced code
        if ln.startswith("```"):
            close_table()
            i += 1
            body = []
            while i < len(lines) and not lines[i].startswith("```"):
                body.append(html.escape(lines[i]))
                i += 1
            i += 1
            out.append("<pre><code>" + "\n".join(body) + "</code></pre>")
            continue

        # image on its own line
        m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", ln)
        if m:
            close_table()
            alt, src = m.group(1), m.group(2)
            cap = ""
            if i + 1 < len(lines) and lines[i + 1].startswith("*") and lines[i + 1].rstrip().endswith("*"):
                j = i + 1
                buf = []
                while j < len(lines) and lines[j].strip():
                    buf.append(lines[j])
                    j += 1
                raw = " ".join(buf).strip()
                if raw.startswith("*") and raw.endswith("*"):
                    cap = inline(raw[1:-1])
                    i = j - 1
            out.append(
                f'<figure><img src="{data_uri(src)}" alt="{html.escape(alt)}" loading="lazy">'
                + (f"<figcaption>{cap}</figcaption>" if cap else "")
                + "</figure>")
            i += 1
            continue

        # table
        if ln.startswith("|"):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            nxt = lines[i + 1] if i + 1 < len(lines) else ""
            if not in_table and re.match(r"^\|[\s:\-|]+\|?\s*$", nxt):
                aligns = []
                for spec in [c.strip() for c in nxt.strip().strip("|").split("|")]:
                    if spec.startswith(":") and spec.endswith(":"):
                        aligns.append("center")
                    elif spec.endswith(":"):
                        aligns.append("right")
                    else:
                        aligns.append("left")
                out.append('<div class="tw"><table><thead><tr>'
                           + "".join(f'<th style="text-align:{a}">{inline(c)}</th>'
                                     for c, a in zip(cells, aligns))
                           + "</tr></thead><tbody>")
                in_table = True
                out.append("<!--aligns:" + ",".join(aligns) + "-->")
                i += 2
                continue
            if in_table:
                aligns = re.search(r"<!--aligns:([^>]+)-->", "".join(out[-3:]))
                al = aligns.group(1).split(",") if aligns else ["left"] * len(cells)
                while len(al) < len(cells):
                    al.append("left")
                out.append("<tr>" + "".join(
                    f'<td style="text-align:{a}">{inline(c)}</td>'
                    for c, a in zip(cells, al)) + "</tr>")
                i += 1
                continue
        else:
            close_table()

        if ln.startswith("#"):
            close_table()
            lvl = len(ln) - len(ln.lstrip("#"))
            text = ln[lvl:].strip()
            sid = slug(text)
            if lvl == 1:
                out.append(f'<h1 id="{sid}">{inline(text)}</h1>')
            else:
                if lvl == 2:
                    toc.append((sid, text))
                out.append(f'<h{lvl} id="{sid}">{inline(text)}</h{lvl}>')
            i += 1
            continue

        if re.match(r"^(---|\*\*\*)\s*$", ln):
            close_table()
            out.append("<hr>")
            i += 1
            continue

        if ln.startswith(">"):
            close_table()
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(lines[i].lstrip("> ").rstrip())
                i += 1
            out.append("<blockquote><p>" + inline(" ".join(buf)) + "</p></blockquote>")
            continue

        if re.match(r"^\s*([-*]|\d+\.)\s+", ln):
            close_table()
            ordered = bool(re.match(r"^\s*\d+\.\s+", ln))
            tag = "ol" if ordered else "ul"
            items = []
            while i < len(lines) and re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]):
                item = re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[i])
                i += 1
                while (i < len(lines) and lines[i].startswith("   ")
                       and not re.match(r"^\s*([-*]|\d+\.)\s+", lines[i])):
                    item += " " + lines[i].strip()
                    i += 1
                items.append(f"<li>{inline(item)}</li>")
            out.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
            continue

        if not ln.strip():
            i += 1
            continue

        close_table()
        buf = [ln]
        i += 1
        while (i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", "|", ">", "```", "!["))
               and not re.match(r"^\s*([-*]|\d+\.)\s+", lines[i])
               and not re.match(r"^(---|\*\*\*)\s*$", lines[i])):
            buf.append(lines[i])
            i += 1
        text = " ".join(x.strip() for x in buf)
        cls = ' class="lede"' if text.startswith("*") and text.endswith("*") else ""
        if cls:
            text = text[1:-1]
        out.append(f"<p{cls}>{inline(text)}</p>")

    close_table()
    body = re.sub(r"<!--aligns:[^>]+-->", "", "\n".join(out))
    return body, toc


CSS = """
:root{
  --ground:#f6f5f2; --surface:#ffffff; --surface-2:#f0efeb;
  --ink:#191c22; --ink-2:#3b414d; --muted:#6a7180;
  --rule:#dedcd6; --rule-soft:#eae8e2;
  --accent:#a9701a; --accent-soft:#f3e6cd;
  --good:#1c6f39; --caution:#a8481a;
  --shadow:0 1px 2px rgba(20,22,28,.06),0 8px 24px rgba(20,22,28,.05);
  --sans:ui-sans-serif,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --serif:ui-serif,Charter,"Iowan Old Style",Georgia,"Times New Roman",serif;
  --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --ground:#0e1117; --surface:#151920; --surface-2:#1b202a;
    --ink:#e7e9ee; --ink-2:#c3c8d2; --muted:#8f97a6;
    --rule:#262c37; --rule-soft:#1e232d;
    --accent:#efc154; --accent-soft:#2a2515;
    --good:#63cf80; --caution:#ef9059;
    --shadow:0 1px 2px rgba(0,0,0,.4),0 10px 30px rgba(0,0,0,.35);
  }
}
:root[data-theme="dark"]{
  --ground:#0e1117; --surface:#151920; --surface-2:#1b202a;
  --ink:#e7e9ee; --ink-2:#c3c8d2; --muted:#8f97a6;
  --rule:#262c37; --rule-soft:#1e232d;
  --accent:#efc154; --accent-soft:#2a2515;
  --good:#63cf80; --caution:#ef9059;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 10px 30px rgba(0,0,0,.35);
}

*{box-sizing:border-box}
body{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:var(--serif); font-size:17px; line-height:1.68;
  -webkit-font-smoothing:antialiased;
}
.shell{display:grid; grid-template-columns:250px minmax(0,1fr); gap:0; max-width:1240px; margin:0 auto}

/* ── masthead ─────────────────────────────────────────────── */
.mast{grid-column:1/-1; padding:56px 40px 0}
.eyebrow{
  font-family:var(--mono); font-size:11px; letter-spacing:.16em; text-transform:uppercase;
  color:var(--muted); margin:0 0 14px;
}
.mast h1{
  font-family:var(--sans); font-weight:800; letter-spacing:-.025em;
  font-size:clamp(2.1rem,5vw,3.1rem); line-height:1.05; margin:0; text-wrap:balance;
}
.mast .sub{
  font-size:1.06rem; color:var(--ink-2); margin:14px 0 0; max-width:62ch; font-style:italic;
}
.hazard{
  height:6px; margin:34px 0 0; border-radius:1px;
  background:repeating-linear-gradient(115deg,
    var(--accent) 0 9px, transparent 9px 20px);
  opacity:.55;
}

/* ── sidebar ──────────────────────────────────────────────── */
nav.toc{
  padding:38px 22px 60px 40px; align-self:start;
  position:sticky; top:0; max-height:100vh; overflow-y:auto;
}
nav.toc h2{
  font-family:var(--mono); font-size:10.5px; letter-spacing:.16em; text-transform:uppercase;
  color:var(--muted); margin:0 0 14px; font-weight:600;
}
nav.toc ol{list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:2px}
nav.toc a{
  display:flex; gap:10px; align-items:baseline;
  font-family:var(--sans); font-size:13.5px; line-height:1.35;
  color:var(--ink-2); text-decoration:none; padding:6px 8px; border-radius:5px;
  border-left:2px solid transparent;
}
nav.toc a:hover{background:var(--surface-2); color:var(--ink)}
nav.toc a.here{border-left-color:var(--accent); color:var(--ink); background:var(--surface-2); font-weight:600}
nav.toc .n{font-family:var(--mono); font-size:11px; color:var(--muted); min-width:1.4em}

/* ── article ──────────────────────────────────────────────── */
article{padding:38px 40px 120px; min-width:0}
article > *{max-width:68ch}
article > .tw, article > figure, article > pre{max-width:none}

h2{
  font-family:var(--sans); font-weight:750; letter-spacing:-.018em;
  font-size:1.62rem; line-height:1.2; margin:64px 0 6px; text-wrap:balance;
  padding-top:16px; border-top:1px solid var(--rule);
}
h2:first-of-type{margin-top:8px}
h3{
  font-family:var(--sans); font-weight:700; letter-spacing:-.012em;
  font-size:1.16rem; margin:38px 0 4px; text-wrap:balance;
}
h4{font-family:var(--sans); font-weight:700; font-size:1rem; margin:26px 0 2px}
p{margin:14px 0}
p.lede{color:var(--muted); font-size:.94rem}
a{color:var(--accent); text-underline-offset:2px}
a:focus-visible,nav.toc a:focus-visible{outline:2px solid var(--accent); outline-offset:2px; border-radius:3px}
strong{font-weight:700}
ul,ol{margin:14px 0; padding-left:1.35em; display:flex; flex-direction:column; gap:6px}
li{padding-left:2px}
hr{border:0; border-top:1px solid var(--rule-soft); margin:44px 0}
blockquote{
  margin:22px 0; padding:14px 18px; border-left:3px solid var(--accent);
  background:var(--accent-soft); border-radius:0 6px 6px 0;
}
blockquote p{margin:0}
code{
  font-family:var(--mono); font-size:.86em; background:var(--surface-2);
  padding:.12em .38em; border-radius:4px; border:1px solid var(--rule-soft);
}
pre{
  background:var(--surface); border:1px solid var(--rule); border-radius:8px;
  padding:16px 18px; overflow-x:auto; margin:20px 0; box-shadow:var(--shadow);
}
pre code{background:none; border:0; padding:0; font-size:13px; line-height:1.6}

/* ── tables ───────────────────────────────────────────────── */
.tw{overflow-x:auto; margin:22px 0; border:1px solid var(--rule); border-radius:8px; background:var(--surface); box-shadow:var(--shadow)}
table{border-collapse:collapse; width:100%; font-family:var(--sans); font-size:13.5px; font-variant-numeric:tabular-nums}
th{
  font-family:var(--mono); font-size:10.5px; letter-spacing:.09em; text-transform:uppercase;
  color:var(--muted); font-weight:600; padding:11px 14px; white-space:nowrap;
  border-bottom:1px solid var(--rule); background:var(--surface-2);
}
td{padding:10px 14px; border-bottom:1px solid var(--rule-soft); color:var(--ink-2); vertical-align:top}
tbody tr:last-child td{border-bottom:0}
td code{font-size:.92em}
td strong{color:var(--ink)}

/* ── figures ──────────────────────────────────────────────── */
figure{margin:26px 0; max-width:900px}
figure img{
  display:block; width:100%; height:auto; border-radius:8px;
  border:1px solid var(--rule); box-shadow:var(--shadow); background:var(--surface-2);
}
figcaption{
  font-family:var(--sans); font-size:12.5px; line-height:1.5; color:var(--muted);
  margin-top:9px; max-width:64ch;
}

@media (max-width:920px){
  .shell{grid-template-columns:1fr}
  .mast{padding:36px 22px 0}
  nav.toc{position:static; max-height:none; padding:26px 22px 0; border-bottom:1px solid var(--rule)}
  nav.toc ol{display:grid; grid-template-columns:repeat(auto-fill,minmax(190px,1fr)); gap:2px}
  article{padding:26px 22px 90px}
  article > *{max-width:none}
}
@media (prefers-reduced-motion:reduce){*{animation:none!important; transition:none!important}}
"""

JS = """
const links=[...document.querySelectorAll('nav.toc a')];
const map=new Map(links.map(a=>[a.getAttribute('href').slice(1),a]));
const obs=new IntersectionObserver(es=>{
  es.forEach(e=>{
    if(e.isIntersecting){
      links.forEach(a=>a.classList.remove('here'));
      const a=map.get(e.target.id); if(a) a.classList.add('here');
    }
  });
},{rootMargin:'-10% 0px -80% 0px',threshold:0});
document.querySelectorAll('article h2[id]').forEach(h=>obs.observe(h));
"""


def build():
    md = open(SRC).read()
    # the markdown TOC list is replaced by the sidebar
    md = re.sub(r"## Contents\n\n(?:\d+\..*\n)+", "", md)
    body, toc = convert(md)

    items = []
    for n, (sid, text) in enumerate(toc, 1):
        label = re.sub(r"^\d+\.\s*", "", text)
        items.append(f'<li><a href="#{sid}"><span class="n">{n:02d}</span>'
                     f'<span>{html.escape(label)}</span></a></li>')

    # the h1 becomes the masthead
    body = re.sub(r'<h1 id="[^"]*">.*?</h1>', "", body, count=1, flags=re.S)
    body = body.replace(
        '<p class="lede">A factory-building game about digging things out of the ground, '
        'turning them into more valuable things, and living with the smoke.</p>', "", 1)
    body = re.sub(r"^\s*<hr>", "", body.strip(), count=1)

    page = f"""<title>Industrial Capitalist — User Manual</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>{CSS}</style>
<div class="shell">
  <header class="mast">
    <p class="eyebrow">Industrial Capitalist · User Manual</p>
    <h1>Dig it up. Refine it. Sell it. Live with the smoke.</h1>
    <p class="sub">Everything a new player needs: installing the game, wiring your first
    machine, reading a recipe, keeping the air breathable, and what to do when the
    factory stops.</p>
    <div class="hazard" role="presentation"></div>
  </header>
  <nav class="toc" aria-label="Contents">
    <h2>Contents</h2>
    <ol>{''.join(items)}</ol>
  </nav>
  <article>
{body}
  </article>
</div>
<script>{JS}</script>
"""
    with open(OUT, "w") as f:
        f.write(page)
    print(f"wrote {OUT}  ({len(page)/1024/1024:.2f} MB, {len(toc)} sections)")


if __name__ == "__main__":
    build()
