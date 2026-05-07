#!/usr/bin/env python3
"""Parse the scraped daslab.stanford.edu HTML and emit Jekyll collection markdown.

Reads from ../_scrape/, writes into ../_people/, ../_alumni/, ../_news/, ../_publications/.
"""
import os
import re
import sys
from pathlib import Path
from datetime import datetime

from bs4 import BeautifulSoup, NavigableString

ROOT = Path(__file__).resolve().parent.parent
SCRAPE = ROOT / "_scrape"

# /site_data/ppl_img/foo.jpg -> /assets/images/people/foo.jpg
def remap_url(u: str) -> str:
    if not u: return u
    return (u.replace("/site_data/ppl_img/", "/assets/images/people/")
             .replace("/site_data/news_img/", "/assets/images/news/")
             .replace("/site_data/pub_img/",  "/assets/images/publications/")
             .replace("/site_media/images/",  "/assets/images/site/"))

# Pub PDFs stay on AWS for now.
def remap_pdf(u: str) -> str:
    if not u: return u
    if u.startswith("/site_data/pub_pdf/"):
        return "https://daslab.stanford.edu" + u
    return u

def slugify(s: str) -> str:
    s = re.sub(r"[^\w\s-]", "", s.strip().lower())
    return re.sub(r"[\s_-]+", "-", s)[:80]

def yamlsafe(s: str) -> str:
    if s is None: return ""
    s = s.strip().replace("\r", "").replace("\n", " ")
    s = s.replace('"', '\\"')
    return s

def write_md(path: Path, fm: dict, body: str = ""):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["---"]
    for k, v in fm.items():
        if v is None or v == "": continue
        if isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                lines.append(f'  - "{yamlsafe(str(item))}"')
        elif isinstance(v, (int, float, bool)):
            lines.append(f"{k}: {v}")
        else:
            sv = str(v)
            if any(c in sv for c in ":#\"'\n") or sv.startswith("- "):
                lines.append(f'{k}: "{yamlsafe(sv)}"')
            else:
                lines.append(f"{k}: {sv}")
    lines.append("---")
    if body.strip():
        lines.append("")
        lines.append(body.strip())
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


# ---------- people / alumni ----------

def _is_pi(role: str) -> bool:
    return "principal investigator" in role.lower()


def _end_year(role: str):
    years = [int(y) for y in re.findall(r"\b(19\d{2}|20\d{2})\b", role)]
    return max(years) if years else None


def _last_name(name: str) -> str:
    """Use the last whitespace-separated token of `name`, lowercased,
    as a sort key. Strip any parenthetical (e.g. '(formerly Smith)')."""
    n = re.sub(r"\([^)]*\)", "", name).strip()
    return n.rsplit(None, 1)[-1].lower() if n else ""


def parse_people(html: str):
    """Emit a unified _people/ collection. Current members get
    status: current and a derived role_order; alumni get status: alumnus
    and (where parseable from the role string) end_year. Filenames are
    plain <slug>.md — sorting is done by frontmatter on the page."""
    soup = BeautifulSoup(html, "html.parser")
    people_dir = ROOT / "_people"
    if people_dir.exists():
        for f in people_dir.glob("*.md"): f.unlink()

    current_count = alum_count = 0

    for tr in soup.select("tr.current_member"):
        img = tr.find("img")
        photo = remap_url(img["src"]) if img and img.get("src") else ""
        name_el = tr.select_one("p.peopleH2")
        if not name_el: continue
        name = name_el.get_text(strip=True)
        role_el = tr.select_one("p.peopleTEXT")
        role = ""
        if role_el:
            txt = " ".join(role_el.get_text(" ", strip=True).split())
            txt = re.sub(r"\s+,", ",", txt)
            role = txt[:280]
        slug = slugify(name)
        fm = {
            "name": name,
            "role": role,
            "photo": photo,
            "status": "current",
            "last_name": _last_name(name),
        }
        if _is_pi(role):
            fm["pi"] = True
        write_md(people_dir / f"{slug}.md", fm)
        current_count += 1

    for past in soup.select("p.past_member"):
        name = past.get_text(strip=True)
        role = ""
        nxt = past.find_next("p", class_="peopleTEXT")
        if nxt:
            role = " ".join(nxt.get_text(" ", strip=True).split())
            role = re.sub(r"\s+,", ",", role)[:280]
        slug = slugify(name)
        target = people_dir / f"{slug}.md"
        if target.exists():
            target = people_dir / f"{slug}-alumni.md"
        fm = {"name": name, "role": role, "status": "alumnus", "last_name": _last_name(name)}
        ey = _end_year(role)
        if ey: fm["end_year"] = ey
        write_md(target, fm)
        alum_count += 1

    print(f"  people: {current_count} current, {alum_count} alumni (single _people/)")


# ---------- publications ----------

def parse_publications(html: str):
    """Each publication is a <p class="TEXT"> paragraph containing authors,
    year in parens, title in <u>, journal in <i>, then a span.yearTEXT with
    links. Featured pubs live in <table class="publicationFeatured"> with the
    same inner shape. We track the current year via the most recent .yearH2
    heading we've passed in document order."""
    soup = BeautifulSoup(html, "html.parser")
    pubs_dir = ROOT / "_publications"
    if pubs_dir.exists():
        for f in pubs_dir.glob("*.md"): f.unlink()

    # Walk all elements in document order; track current year and emit a
    # publication record per p.TEXT (skipping ones that are inside the page
    # header, e.g. the "Click here to find a Das Lab paper..." paragraph).
    current_year = None
    count = 0
    seen = set()

    for el in soup.find_all(["h2", "p", "div", "td"]):
        cls = el.get("class") or []
        if "yearH2" in cls:
            m = re.search(r"\d{4}", el.get_text(strip=True))
            if m: current_year = int(m.group(0))
            continue

        is_pub_para = (el.name == "p" and "TEXT" in cls and not (set(cls) & {"contactH1","contactH2","peopleTEXT","homeTEXT","BODY"}))
        is_pub_cell = (el.name == "td" and el.find_parent("table") is not None and any("publicationFeatured" in (p.get("class") or []) for p in el.find_parents("table")))
        if not (is_pub_para or is_pub_cell):
            continue
        if id(el) in seen: continue
        seen.add(id(el))

        # Title: <u> for normal pubs, <span class="contactH1"> for featured pubs
        title_el = el.find("u") or el.select_one("span.contactH1")
        if not title_el:
            continue

        title = " ".join(title_el.get_text(" ", strip=True).split()).strip(' "“”')

        featured = bool(el.find_parent("table", class_="publicationFeatured"))

        # Year: prefer (YYYY) in the paragraph text, fall back to current_year
        text = el.get_text(" ", strip=True)
        year = current_year
        m = re.search(r"\((\d{4})\)", text)
        if m: year = int(m.group(1))

        # Authors: text before the (YYYY) marker
        if m:
            authors = text[:m.start()].strip()
        else:
            authors = text.split('"')[0].strip()
        authors = " ".join(authors.split())
        # Tighten: single space before commas, normalise " ," -> ","
        authors = re.sub(r"\s+,", ",", authors)

        # Journal: <i> after the title
        journal = ""
        i_el = el.find("i")
        if i_el: journal = " ".join(i_el.get_text(" ", strip=True).split())

        # Links: collect all anchors with a meaningful label
        pdf_url = ""; doi_url = ""; links = []
        for a in el.find_all("a", href=True):
            href = a["href"]
            label = a.get_text(strip=True)
            if not label: continue
            llower = label.lower()
            # First Paper/PDF link populates pdf_url; first DOI link populates doi_url.
            if not pdf_url and ("/pub_pdf/" in href or href.endswith(".pdf") or llower in ("paper","pdf")):
                pdf_url = remap_pdf(href) if href.startswith("/") else href
                continue
            if not doi_url and ("doi.org" in href or "/doi/" in href or llower == "link"):
                doi_url = href
                continue
            # Anything else (Preprint, Server, Code, bioRxiv, etc.) goes into the
            # links array so it can be rendered alongside.
            links.append({"label": label, "url": href})

        # Thumb: img inside the same paragraph or its parent row.
        thumb = ""
        img = el.find("img")
        if not img:
            row = el.find_parent("tr")
            if row: img = row.find("img")
        if img and img.get("src"): thumb = remap_url(img["src"])

        slug_base = slugify(title)[:60] or f"pub-{count:03d}"
        count += 1
        slug = f"{year or 0}-{slug_base}"
        fm = {
            "title": title,
            "year": year or 0,
            "authors": authors[:1200],
            "journal": journal,
            "thumb": thumb,
            "pdf": pdf_url,
            "doi": doi_url,
            "featured": featured if featured else "",
            "order": count,
        }
        if links:
            # YAML-friendly inline serialisation handled in write_md via list path,
            # but each entry is a dict. Use a flatter shape: links_labels / links_urls
            # so write_md can serialise without a custom schema.
            fm["link_labels"] = [L["label"] for L in links]
            fm["link_urls"]   = [L["url"]   for L in links]
        write_md(pubs_dir / f"{count:04d}-{slug}.md", fm)

    print(f"  publications: {count}")


# ---------- news ----------

def parse_news(html: str):
    """News entries on the legacy site are <tr> rows in a single table; each
    row has a date, image thumbnail, title, body text. Extract them and emit
    one markdown post per entry."""
    soup = BeautifulSoup(html, "html.parser")
    news_dir = ROOT / "_news"
    if news_dir.exists():
        for f in news_dir.glob("*.md"): f.unlink()

    count = 0
    # Each entry is a <tr> that contains an image referencing /site_data/news_img/
    seen = set()
    for img in soup.select('img[src*="/site_data/news_img/"]'):
        row = img.find_parent("tr")
        if not row: continue
        if id(row) in seen: continue
        seen.add(id(row))

        # Cells: first td often has the date, image lives in image td, body in text td
        cells = row.find_all("td", recursive=False)
        text_blob = " ".join(row.get_text(" ", strip=True).split())

        # Find a date — looks like "Month YYYY" or "Mon DD, YYYY" or "MM/YYYY"
        date_str = None
        m = re.search(r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2},?\s+)?(\d{4})\b", text_blob, re.I)
        if m:
            month_name = m.group(1).title()
            year = int(m.group(3))
            day = m.group(2)
            day = int(re.sub(r"\D", "", day)) if day else 1
            try:
                date_str = datetime.strptime(f"{month_name} {day} {year}", "%B %d %Y").strftime("%Y-%m-%d")
            except ValueError:
                date_str = None
        if not date_str:
            m = re.search(r"\b(\d{4})\b", text_blob)
            year = int(m.group(1)) if m else 2020
            date_str = f"{year}-01-01"

        # Title: bold/strong, or first sentence under ~200 chars
        title_el = row.find(["strong", "b"])
        title = ""
        if title_el:
            title = " ".join(title_el.get_text(" ", strip=True).split())[:200]
        if not title:
            title = text_blob.split(".")[0][:200] if text_blob else "(news)"

        # Body: full text minus the title.
        # Mutate the cell trees first: drop the leading date paragraph (we already
        # have it in frontmatter), and rewrite the legacy "read more" anchor —
        # which wraps an empty CSS-styled div — into a proper textual link.
        body_html = ""
        for cell in cells:
            if cell.find("img") and not cell.find(string=re.compile(r"\w")):
                continue
            # Strip leading <p class="yearTEXT">...the date...</p> so it's not
            # rendered twice on the news index.
            for p in list(cell.find_all("p", class_="yearTEXT", limit=2)):
                ptxt = p.get_text(strip=True)
                # Heuristic: if the paragraph is just a date, remove it.
                if re.match(r"^[A-Za-z]+\s+\d{1,2}?,?\s*\d{4}$", ptxt) or re.match(r"^[A-Za-z]+\s+\d{4}$", ptxt):
                    p.decompose()

            # The legacy markup uses <a class="btn_readmore"><div class="imgsp_more_read"></div></a>
            # — an anchor whose only child is an empty CSS-styled div. Kramdown can't
            # parse this when there's a blank line between <a> and </a>, so the </a>
            # ends up rendered as text. Replace with a clean inline "Read more →" link.
            for a in cell.find_all("a", class_="btn_readmore"):
                href = a.get("href", "#")
                a.clear()
                a["class"] = "read-more"
                a.string = "Read more →"
            # Also catch read-more anchors that aren't tagged with btn_readmore but
            # wrap only a more_read/info background-image div.
            for a in list(cell.find_all("a")):
                child_divs = [c for c in a.find_all(recursive=False) if c.name == "div"]
                if (a.get_text(strip=True) == "" and child_divs
                        and any("imgsp_more" in (d.get("class") or []) for d in child_divs)):
                    href = a.get("href", "#")
                    a.clear()
                    a["class"] = "read-more"
                    a.string = "Read more →"

            for t in cell.find_all("img"):
                if t.get("src"): t["src"] = remap_url(t["src"])
            for t in cell.find_all("a", href=True):
                href = t["href"]
                t["href"] = remap_url(href) if href.startswith("/site_") else href

            inner = cell.decode_contents()
            body_html += inner + "\n"

        thumb = remap_url(img.get("src", ""))
        slug = slugify(title)[:60] or f"news-{count:03d}"
        count += 1
        filename = f"{date_str}-{slug}.md"
        fm = {
            "title": title,
            "date": date_str,
            "image": thumb,
        }
        write_md(news_dir / filename, fm, body=body_html)

    print(f"  news: {count}")


def main():
    print("Scraping current site HTML into Jekyll collections")
    parse_people((SCRAPE / "_people_.html").read_text(encoding="utf-8"))
    parse_publications((SCRAPE / "_publications_.html").read_text(encoding="utf-8"))
    parse_news((SCRAPE / "_news_.html").read_text(encoding="utf-8"))
    print("Done.")

if __name__ == "__main__":
    main()
