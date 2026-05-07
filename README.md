# Das Lab Website

Static Jekyll site for [daslab.stanford.edu](https://daslab.stanford.edu).

## Local development

```bash
bundle install
bundle exec jekyll serve
# open http://localhost:4000/daslab-website/
```

## Editing content

Lab members can update content directly through the GitHub web UI — no command line needed:

- **People:** edit a file in `_people/`
- **Alumni:** edit a file in `_alumni/`
- **News:** add a file to `_news/` (filename: `YYYY-MM-DD-short-title.md`)
- **Publications:** edit a file in `_publications/`

Each entry is a small markdown file with a frontmatter block at the top — copy an existing entry as a template. Save the change and the site rebuilds in ~30 seconds.

## Hosting

Deployed via GitHub Pages from the `main` branch. The custom domain `daslab.stanford.edu` is wired up via DNS CNAME → `daslab.github.io`.
