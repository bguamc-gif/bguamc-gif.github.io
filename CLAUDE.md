# 3D Lab website (GitHub Pages)

- The whole site is one self-contained file: `index.html` (Hebrew, RTL, hash routing).
- Served by GitHub Pages from `main` / root at https://bguamc-gif.github.io
- After ANY change to the inline `<script>`, run `python3 tools/csp.py` – it recomputes the
  script hash in the Content-Security-Policy meta tag. Without it the site's script is blocked.
- Commit as `bguamc-gif <bguamc-gif@users.noreply.github.com>` (keeps the personal email out of git history).
- Never add secrets, tokens or personal data to this repository – it is public.
- Writing style for site copy: neutral service tone, no first-person plural ("אנחנו", "שלנו").
