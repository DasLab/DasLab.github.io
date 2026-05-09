# Das Lab Website

Static Jekyll site for [daslab.stanford.edu](https://daslab.stanford.edu).

## For lab members: editing content

**See [CONTRIBUTING.md](CONTRIBUTING.md)** for step-by-step instructions on adding people, news, and publications — no command line needed.

## Local development (developers)

```bash
bundle install
bundle exec jekyll serve
# open http://localhost:4000/
```

## Hosting

Deployed via GitHub Pages at **https://daslab.stanford.edu**, built by the workflow at `.github/workflows/pages.yml`. Every push to `main` triggers a rebuild (~30 seconds).

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
