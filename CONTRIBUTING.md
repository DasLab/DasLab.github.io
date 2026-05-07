# Editing the Das Lab website

Lab members can update people, news, and publications **without leaving the browser** — no terminal, no git commands. All content lives in plain markdown files in this repo. Edit them via the GitHub web UI and the site rebuilds automatically in ~30 seconds.

You'll need a (free) GitHub account, and Rhiju (or any DasLab org admin) needs to add you to the org as a member or to the repo as a collaborator. Once added, you'll see an **"Edit"** pencil icon at the top right of any file when you open it on github.com.

---

## How content is organized

| Folder | What's in it | When to edit |
|---|---|---|
| `_people/` | One `.md` file per person (current + alumni in the same folder) | Adding a new lab member, moving someone to alumni, fixing a role/photo |
| `_news/` | One `.md` file per news item, filename starts with the date | Adding lab news |
| `_publications/` | One `.md` file per paper | Adding a new paper, marking one as featured |
| `assets/images/people/` | Lab member portraits | Uploading a new photo |
| `assets/images/news/` | Photos for news posts | Uploading a thumbnail for a news item |

---

## Adding a new lab member

1. Pick or upload a photo. Open `assets/images/people/` on github.com, click **"Add file → Upload files"**, drag the photo in, then **"Commit changes"**. Use a short, lowercase filename like `chaitanya-joshi.jpg` (no spaces).
2. Open `_people/`, click **"Add file → Create new file"**.
3. Name the file `<firstname>-<lastname>.md` (lowercase, hyphens). Example: `jane-doe.md`.
4. Paste this template and fill it in:

   ```yaml
   ---
   name: Jane Doe
   role: Postdoctoral Fellow, Biochemistry
   photo: /assets/images/people/jane-doe.jpg
   status: current
   last_name: doe
   ---
   ```

5. Click **"Commit changes"** at the bottom.

The `last_name` is used for sorting (alphabetical, case-insensitive) — write it lowercased. Members are listed alphabetically by `last_name`. The principal investigator is pinned to the end (see below).

### Optional fields

- `cv_url:` — link to a CV (e.g., a Dropbox link)
- `profile_url:` — link to a Stanford profile page
- `pi: true` — pins this person to the end of the current-members list. Only the principal investigator should have this.

---

## Moving someone to alumni

When a lab member leaves, you only edit one file — no need to move it between folders.

1. Open their file in `_people/`.
2. Click the pencil icon (edit).
3. Change two lines in the frontmatter:

   ```yaml
   status: alumnus
   end_year: 2026
   ```

   `end_year` is the year they left. (You can also remove `pi`, `cv_url`, etc. if no longer relevant — but `last_name` should stay; it sorts within their year.)

4. Update the `role` line to include the date range, e.g.:

   ```yaml
   role: Ph.D. Student, 2021-2026
   ```

5. Click **"Commit changes"**.

The alumni list is automatically sorted by `end_year` (newest first), then alphabetically. They'll show up in the right place automatically.

---

## Adding a news item

1. (Optional) Upload an image to `assets/images/news/`. Same process as people photos.
2. Open `_news/`, click **"Add file → Create new file"**.
3. **Name it with today's date in front:** `YYYY-MM-DD-short-title.md`. Example: `2026-05-15-chaitanya-joins-lab.md`.
4. Paste this template:

   ```yaml
   ---
   title: Chaitanya joins the lab
   date: 2026-05-15
   image: /assets/images/news/chaitanya-joshi.jpg
   ---

   Welcome to **Chaitanya Joshi**, our newest postdoctoral fellow!
   Chaitanya joins us after developing the first RNA deep learning
   design methods at the University of Cambridge.

   <a class="read-more" href="https://example.com/announcement">Read more →</a>
   ```

5. Commit.

The news index shows the 10 most recent posts; older ones tuck under "Previous news" automatically.

---

## Adding a publication

1. (Optional) If the paper is "featured" — meaning you want it shown with a thumbnail at the top of its year — upload the figure to `assets/images/publications/` and note the path.
2. Open `_publications/`, click **"Add file → Create new file"**.
3. Name it `<year>-<short-title-slug>.md`. The `<year>-` prefix is what keeps publications grouped by year.
4. Paste this template:

   ```yaml
   ---
   title: A descriptive title without surrounding quotes
   year: 2026
   authors: Doe, J., Smith, K., Das, R.
   journal: Nature Communications
   pdf: https://example.com/paper.pdf      # link to the PDF
   doi: https://doi.org/10.1038/s41467-...  # link to the journal
   ---
   ```

5. **Optional fields:**
   - `featured: true` — paper appears with a thumbnail and pale-teal background highlight
   - `thumb: /assets/images/publications/myfigure.png` — figure for featured papers
   - `link_labels:` and `link_urls:` — extra labeled links (Preprint, Server, Code, etc.):

     ```yaml
     link_labels:
       - "Preprint"
       - "Code"
     link_urls:
       - "https://biorxiv.org/..."
       - "https://github.com/..."
     ```

6. Commit.

Publications sort newest year first; within a year, files sort alphabetically by filename — name your files starting with a `<year>-` prefix and they'll group cleanly.

---

## A few tips

- **Preview before committing:** at the top of the editor, click the **"Preview"** tab to see a rough render of your markdown.
- **Mistakes are fixable:** every commit is reversible. If the site looks wrong after your change, open the file, click the history icon, and revert. Or just edit again.
- **Build status:** click the **Actions** tab on github.com to see whether your last commit successfully deployed. A green check means the live site is updating; a red X means there's a syntax error in your frontmatter (often a missing colon or quote).
- **Commit messages:** GitHub auto-fills a reasonable default like "Update jane-doe.md". You can leave it.

If you get stuck, ask Rhiju or another lab member.
