#!/usr/bin/env bash
set -euo pipefail

echo "==> Generating GEO files (llms.txt, llms-full.txt)..."
python3 scripts/generate-llms.py

hugo "$@"

echo "==> Generating companion .md files for direct URL access..."
find public -name "index.md" -type f | while read -r file; do
  dir=$(dirname "$file")
  parent=$(dirname "$dir")
  slug=$(basename "$dir")
  if [ "$slug" != "public" ]; then
    cp "$file" "$parent/${slug}.md"
  fi
done

echo "==> Fixing raw <img> relative assets paths in blog posts..."
python3 -c '
import glob, re
for p in glob.glob("public/blog/*/index.html"):
    with open(p, "r", encoding="utf-8") as f:
        content = f.read()
    new_content = re.sub(r"""src=["\x27](\./)?assets/""", "src=\"/blog/assets/", content)
    if new_content != content:
        with open(p, "w", encoding="utf-8") as f:
            f.write(new_content)
'
echo "==> Done!"
