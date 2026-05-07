# Das Lab Website

Static Jekyll site for [daslab.stanford.edu](https://daslab.stanford.edu).

## Local development

```bash
bundle install
bundle exec jekyll serve
# open http://localhost:4000/
```

## Editing content

Lab members can update content directly through the GitHub web UI — no command line needed:

- **People:** edit a file in `_people/`
- **Alumni:** edit a file in `_alumni/`
- **News:** add a file to `_news/` (filename: `YYYY-MM-DD-short-title.md`)
- **Publications:** edit a file in `_publications/`

Each entry is a small markdown file with a frontmatter block at the top — copy an existing entry as a template. Save the change and the site rebuilds in ~30 seconds.

## Hosting

Deployed via GitHub Pages, built by the workflow at `.github/workflows/pages.yml`. Currently live at:

**https://daslab.github.io/**

### DNS cutover to daslab.stanford.edu (when ready)

Two steps, in order:

1. **Update DNS at Stanford.** Have Stanford IT change the CNAME (or A/AAAA records) for `daslab.stanford.edu` to point at GitHub Pages. The four GitHub Pages IPs for apex domains are: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`. For a CNAME, point at `daslab.github.io`.
2. **Add a `CNAME` file to this repo** containing exactly `daslab.stanford.edu` and push. GitHub will detect it and provision a Let's Encrypt cert automatically (give it a few minutes after DNS propagates).

Until DNS resolves to GitHub Pages, leave the `CNAME` file out — committing it early will make GitHub Pages redirect the staging URL to `daslab.stanford.edu`, which still points at AWS, breaking the preview.

## Re-running the content scraper

The current site's content was migrated by `tools/scrape_content.py` from HTML in `_scrape/`. To refresh from the live AWS site (e.g., after a CMS update):

```bash
cd _scrape
for p in / /research/ /news/ /people/ /publications/ /resources/ /contact/; do
  curl -sL "https://daslab.stanford.edu$p" -o "$(echo "$p" | sed 's:/:_:g').html"
done
cd ..
python3 tools/scrape_content.py
```

Note: this overwrites everything in `_people/`, `_alumni/`, `_publications/`, `_news/`. Don't run it after lab members have hand-edited content unless you're prepared to re-merge.
