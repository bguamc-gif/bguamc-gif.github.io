"""Build the password-protected quotes tool page:  quotes/index.html

The page contains only AES-256-GCM ciphertext of the tool (key = PBKDF2-SHA256 of the password),
plus a small loader that asks for the password and decrypts in the browser (WebCrypto).
The plaintext tool and the password are NEVER committed to this public repository.

Usage:
    QUOTES_PASSWORD='...' python3 tools/build_quotes.py /path/to/plaintext-tool.html
"""
import base64, hashlib, os, pathlib, re, secrets, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ITER = 600_000
root = pathlib.Path(__file__).resolve().parent.parent
src = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
pw = os.environ.get('QUOTES_PASSWORD')
if not pw:
    sys.exit('set QUOTES_PASSWORD')

salt, iv = secrets.token_bytes(16), secrets.token_bytes(12)
key = hashlib.pbkdf2_hmac('sha256', pw.encode('utf-8'), salt, ITER, 32)
ct = AESGCM(key).encrypt(iv, src.encode('utf-8'), None)
b64 = lambda b: base64.b64encode(b).decode()
sha = lambda s: "'sha256-" + b64(hashlib.sha256(s.encode('utf-8')).digest()) + "'"

LOADER = r"""
(function(){
  if (window.top !== window.self) { document.documentElement.innerHTML = ''; return; }
  var KEY = 'bgu3d_unlock_key';
  var d = document.getElementById('d').dataset;
  var b64 = function(s){ return Uint8Array.from(atob(s), function(c){ return c.charCodeAt(0); }); };
  var enc = function(u){ var s=''; u.forEach(function(x){ s+=String.fromCharCode(x); }); return btoa(s); };
  function derive(pw){
    return crypto.subtle.importKey('raw', new TextEncoder().encode(pw), 'PBKDF2', false, ['deriveBits'])
      .then(function(base){ return crypto.subtle.deriveBits({name:'PBKDF2', salt:b64(d.salt), iterations:+d.iter, hash:'SHA-256'}, base, 256); })
      .then(function(bits){ return new Uint8Array(bits); });
  }
  function decrypt(raw){
    return crypto.subtle.importKey('raw', raw, 'AES-GCM', false, ['decrypt'])
      .then(function(k){ return crypto.subtle.decrypt({name:'AES-GCM', iv:b64(d.iv)}, k, b64(d.ct)); })
      .then(function(pt){ return new TextDecoder().decode(pt); });
  }
  function show(html){ window.__encrypted = true; document.open(); document.write(html); document.close(); }
  var f = document.getElementById('f'), err = document.getElementById('err'), btn = document.getElementById('go');
  try {
    var saved = JSON.parse(localStorage.getItem(KEY) || 'null');
    if (saved && saved.salt === d.salt) { decrypt(b64(saved.k)).then(show).catch(function(){ localStorage.removeItem(KEY); f.hidden = false; }); }
    else f.hidden = false;
  } catch(e) { f.hidden = false; }
  f.addEventListener('submit', function(e){
    e.preventDefault(); err.textContent = ''; btn.disabled = true; btn.textContent = 'בודק...';
    var raw;
    derive(document.getElementById('pw').value).then(function(r){ raw = r; return decrypt(r); }).then(function(html){
      if (document.getElementById('rem').checked) { try { localStorage.setItem(KEY, JSON.stringify({salt:d.salt, k:enc(raw)})); } catch(e){} }
      show(html);
    }).catch(function(){ err.textContent = 'סיסמה שגויה'; btn.disabled = false; btn.textContent = 'כניסה'; });
  });
})();
"""

tool_scripts = re.findall(r'<script>(.*?)</script>', src, re.S)
csp = ("default-src 'none'; script-src " + ' '.join(sha(x) for x in [LOADER] + tool_scripts) +
       "; style-src 'unsafe-inline'; img-src data: blob:; connect-src 'none'; base-uri 'none'; "
       "form-action 'none'; object-src 'none'; manifest-src 'none'; upgrade-insecure-requests")

page = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="{csp}">
<meta name="robots" content="noindex, nofollow, noarchive">
<meta name="referrer" content="no-referrer">
<title>כניסה</title>
<style>
body{{margin:0;min-height:100vh;display:grid;place-items:center;background:#14213d;font-family:"Segoe UI",Arial,sans-serif}}
form{{background:#fff;border-radius:12px;padding:28px 30px;width:min(340px,90vw);box-shadow:0 10px 40px rgba(0,0,0,.3)}}
h1{{font-size:18px;margin:0 0 16px;color:#14213d}}
input[type=password]{{width:100%;box-sizing:border-box;font:inherit;padding:10px;border:1px solid #cdd2da;border-radius:7px;direction:ltr}}
label{{display:flex;gap:6px;align-items:center;font-size:13px;color:#555;margin:12px 0}}
button{{width:100%;font:inherit;font-weight:600;padding:10px;border:0;border-radius:7px;background:#1f5fbf;color:#fff;cursor:pointer}}
#err{{color:#b42318;font-size:13px;min-height:18px;margin:10px 0 0}}
</style>
</head>
<body>
<form id="f" hidden autocomplete="on">
  <h1>כניסה לכלי הפנימי</h1>
  <input type="text" name="username" value="bgu-quotes" autocomplete="username" hidden>
  <input type="password" id="pw" autocomplete="current-password" placeholder="סיסמה" required autofocus>
  <label><input type="checkbox" id="rem"> זכור אותי במחשב הזה</label>
  <button id="go">כניסה</button>
  <p id="err"></p>
</form>
<div id="d" hidden data-iter="{ITER}" data-salt="{b64(salt)}" data-iv="{b64(iv)}" data-ct="{b64(ct)}"></div>
<script>{LOADER}</script>
</body>
</html>
"""
out = root / 'quotes' / 'index.html'
out.parent.mkdir(exist_ok=True)
out.write_text(page, encoding='utf-8')
print('wrote', out, len(page), 'bytes')
