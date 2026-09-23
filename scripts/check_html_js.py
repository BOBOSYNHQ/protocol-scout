"""Extract <script> blocks from index.html and node --check each one."""
import re, subprocess, sys
from pathlib import Path

p = Path(r"C:\Users\Administrator\protocol-scout\index.html")
text = p.read_text(encoding="utf-8")
blocks = re.findall(r"<script(?:\s[^>]*)?>([\s\S]*?)</script>", text)
print(f"Found {len(blocks)} <script> blocks.")
fail = False
for i, b in enumerate(blocks):
    tmp = Path(rf"C:\Users\Administrator\protocol-scout\.smoke\html-block-{i}.js")
    tmp.write_text(b, encoding="utf-8")
    r = subprocess.run(
        ["node", "--check", str(tmp)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if r.returncode != 0:
        print(f"BLOCK {i}: SYNTAX ERROR (size={len(b)})")
        print(r.stdout[:300])
        print(r.stderr[:300])
        fail = True
    else:
        print(f"BLOCK {i}: ok ({len(b)} bytes)")
sys.exit(1 if fail else 0)