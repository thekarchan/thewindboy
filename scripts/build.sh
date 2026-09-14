#!/usr/bin/env bash
set -euo pipefail

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
echo "==> Done!"
