"""Recompute the Content-Security-Policy hash for the inline <script> in index.html.
Run after every edit to the script:  python3 tools/csp.py
"""
import base64, hashlib, re, pathlib
p = pathlib.Path(__file__).resolve().parent.parent / 'index.html'
s = p.read_text(encoding='utf-8')
scripts = re.findall(r'<script>(.*?)</script>', s, re.S)
hashes = ' '.join("'sha256-" + base64.b64encode(hashlib.sha256(x.encode('utf-8')).digest()).decode() + "'" for x in scripts)
csp = ("default-src 'none'; script-src " + hashes + "; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
       "font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'none'; base-uri 'none'; "
       "form-action 'none'; object-src 'none'; manifest-src 'none'; upgrade-insecure-requests")
s = re.sub(r'(<meta http-equiv="Content-Security-Policy" content=")[^"]*(">)', lambda m: m.group(1) + csp + m.group(2), s)
p.write_text(s, encoding='utf-8')
print(csp)
