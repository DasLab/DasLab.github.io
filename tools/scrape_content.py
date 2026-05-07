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

def parse_people(html: str):
    soup = BeautifulSoup(html, "html.parser")
    current_dir = ROOT / "_people"
    alumni_dir = ROOT / "_alumni"
    # wipe to avoid stale entries
    for d in (current_dir, alumni_dir):
        if d.exists():
            for f in d.glob("*.md"): f.unlink()

    order = 0
    # current members live in <tr class="current_member">
    for tr in soup.select("tr.current_member"):
        order += 1
        img = tr.find("img")
        photo = remap_url(img["src"]) if img and img.get("src") else ""
        name_el = tr.select_one("p.peopleH2")
        if not name_el: continue
        name = name_el.get_text(strip=True)
        role_el = tr.select_one("p.peopleTEXT")
        role = ""
        if role_el:
            # take first short paragraph text, normalize whitespace
            txt = " ".join(role_el.get_text(" ", strip=True).split())
            # drop trailing CV / link blurb common in Rhiju's row
            role = txt[:280]
        slug = slugify(name)
        write_md(current_dir / f"{order:02d}-{slug}.md", {
            "name": name,
            "role": role,
            "photo": photo,
            "order": order,
        })

    # alumni — past members are paragraphs marked .past_member; they're listed
    # below current_member rows. Walk all .past_member name paragraphs and pair
    # each with the immediately following peopleTEXT (role/years).
    alum_index = 0
    for past in soup.select("p.past_member"):
        alum_index += 1
        name = past.get_text(strip=True)
        role = ""
        # find next p.peopleTEXT sibling-ish in document order
        nxt = past.find_next("p", class_="peopleTEXT")
        if nxt:
            role = " ".join(nxt.get_text(" ", strip=True).split())[:280]
        slug = slugify(name)
        write_md(alumni_dir / f"{alum_index:03d}-{slug}.md", {
            "name": name,
            "role": role,
            "order": alum_index,
        })

    print(f"  people: {order} current, {alum_index} alumni")


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

        # Skip header blurb on the page (no <u> for title, no year in parens, no authors)
        u_el = el.find("u")
        if not u_el:
            continue

        title = " ".join(u_el.get_text(" ", strip=True).split())

        # Year: prefer (YYYY) in the paragraph text, fall back to current_year
        text = el.get_text(" ", strip=True)
        year = current_year
        m = re.search(r"\((\d{4})\)", text)
        if m: year = int(m.group(1))

        # Authors: text before the (YYYY) marker
        authors = ""
        if m:
            authors = text[:m.start()].strip()
        else:
            authors = text.split('"')[0].strip()
        authors = " ".join(authors.split())

        # Journal: <i> after the title
        journal = ""
        i_el = el.find("i")
        if i_el: journal = " ".join(i_el.get_text(" ", strip=True).split())

        # Links
        pdf_url = ""; doi_url = ""; other_links = []
        for a in el.find_all("a", href=True):
            href = a["href"]
            label = a.get_text(strip=True)
            llower = label.lower()
            if "/pub_pdf/" in href or href.endswith(".pdf"):
                if not pdf_url:
                    pdf_url = remap_pdf(href) if href.startswith("/") else href
            elif "doi.org" in href or "doi/" in href:
                if not doi_url: doi_url = href
            elif label and href.startswith("http"):
                other_links.append({"label": label, "url": href})

        # Thumb: img inside the same paragraph or its parent row
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
            "authors": authors[:600],
            "journal": journal,
            "thumb": thumb,
            "pdf": pdf_url,
            "doi": doi_url,
            "order": count,
        }
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

        # Body: full text minus the title
        body_html = ""
        for cell in cells:
            # skip the image-only cell
            if cell.find("img") and not cell.find(string=re.compile(r"\w")):
                continue
            # take the inner HTML, fix urls
            for t in cell.find_all("img"):
                if t.get("src"): t["src"] = remap_url(t["src"])
            for t in cell.find_all("a", href=True):
                href = t["href"]
                t["href"] = remap_url(href) if href.startswith("/site_") else href
            # serialize, then strip the wrapping <td>...</td>
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
