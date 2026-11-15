"""Inject frames.json into the HTML template and write the page.

Security: the data is embedded with "<", ">" and "&" escaped, so no string in it
can close the <script> element. The template's Content-Security-Policy allows
only the one inline script, identified by its SHA-256 hash computed here.
"""
import base64
import hashlib
import json
import re

PLACEHOLDER = "/*__DATA__*/null"
HASH_PLACEHOLDER = "__SCRIPT_HASH__"
SCRIPT_RE = re.compile(r"<script>(.*?)</script>", re.S)


def safe_json(data):
    """Compact JSON that is safe inside an HTML <script> element."""
    text = json.dumps(data, separators=(",", ":"))
    return text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def csp_hash(script_text):
    digest = hashlib.sha256(script_text.encode("utf-8")).digest()
    return "sha256-" + base64.b64encode(digest).decode()


def run(cfg):
    paths = cfg["paths"]
    data = json.loads(paths["frames_json"].read_text())
    html = paths["template"].read_text()
    for marker in (PLACEHOLDER, HASH_PLACEHOLDER):
        if marker not in html:
            raise ValueError(f"{paths['template'].name} has no {marker} placeholder")
    html = html.replace(PLACEHOLDER, safe_json(data))
    scripts = SCRIPT_RE.findall(html)
    if len(scripts) != 1:
        raise ValueError(f"expected one inline <script>, found {len(scripts)}")
    html = html.replace(HASH_PLACEHOLDER, csp_hash(scripts[0]))
    paths["page"].parent.mkdir(parents=True, exist_ok=True)
    paths["page"].write_text(html)
    print(paths["page"].name, paths["page"].stat().st_size, "bytes")
