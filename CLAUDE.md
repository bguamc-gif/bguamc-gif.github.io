# 3D Lab website (GitHub Pages)

- The whole site is one self-contained file: `index.html` (Hebrew, RTL, hash routing).
- Served by GitHub Pages from `main` / root at https://bguamc-gif.github.io
- After ANY change to the inline `<script>`, run `python3 tools/csp.py` – it recomputes the
  script hash in the Content-Security-Policy meta tag. Without it the site's script is blocked.
- Commit as `bguamc-gif <bguamc-gif@users.noreply.github.com>` (keeps the personal email out of git history).
- Never add secrets, tokens or personal data to this repository – it is public.
- Writing style for site copy: neutral service tone, no first-person plural ("אנחנו", "שלנו").

## Private quotes tool (`/quotes/`)
- `quotes/index.html` is the owner's private quote/order-form tool, **encrypted** (AES-256-GCM, PBKDF2-SHA256 600k).
  It holds only ciphertext + a password loader. Not linked from the public site; `noindex`.
- Rebuild after changing the tool:  `QUOTES_PASSWORD='…' python3 tools/build_quotes.py /path/to/plaintext-tool.html`
  (the script also recomputes that page's CSP hashes). Ask the owner for the plaintext HTML and the password.
- NEVER commit the plaintext tool or the password.
- The page backs up its data to a separate PRIVATE repo via the GitHub API (token kept only in the browser); CSP allows connect-src https://api.github.com only.
