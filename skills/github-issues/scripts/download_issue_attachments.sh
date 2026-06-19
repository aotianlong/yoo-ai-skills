#!/usr/bin/env bash
# Download images and file attachments linked from a GitHub issue body (and comments).
# Requires: gh (logged in), curl, python3
#
# Usage:
#   download_issue_attachments.sh [--repo owner/repo] <issue_number>
#
# Output: /tmp/issue-<n>-attachments/ with manifest.json

set -euo pipefail

REPO="aotianlong/container-house"
ISSUE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO="${2:?}"
      shift 2
      ;;
    -h|--help)
      sed -n '2,8p' "$0"
      exit 0
      ;;
    *)
      if [[ -n "$ISSUE" ]]; then
        echo "Unexpected argument: $1" >&2
        exit 1
      fi
      ISSUE="$1"
      shift
      ;;
  esac
done

if [[ -z "$ISSUE" ]]; then
  echo "Usage: $0 [--repo owner/repo] <issue_number>" >&2
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "gh is not logged in. Run: gh auth login" >&2
  exit 1
fi

TOKEN="$(gh auth token)"
OUT_DIR="/tmp/issue-${ISSUE}-attachments"
mkdir -p "$OUT_DIR"

JSON="$(gh issue view "$ISSUE" --repo "$REPO" --json title,body,comments)"
TITLE="$(echo "$JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['title'])")"

COUNT="$(python3 - "$OUT_DIR" "$JSON" <<'PY'
import json
import re
import sys
from pathlib import Path

out_dir = Path(sys.argv[1])
data = json.loads(sys.argv[2])

texts = [data.get("body") or ""]
for c in data.get("comments") or []:
    texts.append(c.get("body") or "")

asset_re = re.compile(
    r"https://github\.com/user-attachments/(?:assets/[0-9a-f-]+|files/\d+/[^\s\)\]\"'>]+)",
    re.I,
)
seen = []
for t in texts:
    for url in asset_re.findall(t):
        if url not in seen:
            seen.append(url)

Path(out_dir / "urls.txt").write_text(
    "\n".join(seen) + ("\n" if seen else ""),
    encoding="utf-8",
)
print(len(seen))
PY
)"

MANIFEST="$OUT_DIR/manifest.json"
python3 - "$MANIFEST" "$ISSUE" "$REPO" "$TITLE" "$OUT_DIR/urls.txt" <<'PY'
import json
import sys
from pathlib import Path

manifest_path, issue, repo, title, urls_file = sys.argv[1:6]
urls = [u.strip() for u in Path(urls_file).read_text(encoding="utf-8").splitlines() if u.strip()]
payload = {
    "issue": int(issue),
    "repo": repo,
    "title": title,
    "urls": urls,
    "files": [],
}
Path(manifest_path).write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
PY

idx=0
while IFS= read -r url || [[ -n "${url:-}" ]]; do
  [[ -z "$url" ]] && continue
  idx=$((idx + 1))
  base="$(basename "$url" | sed 's/[?#].*//')"
  if [[ "$url" == *"/assets/"* ]]; then
    fname="image-${idx}.png"
  else
    fname="${base:-file-${idx}}"
  fi
  dest="$OUT_DIR/$fname"
  echo "Downloading [$idx/$COUNT]: $url"
  http_code="$(curl -sL \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Accept: application/vnd.github+json" \
    -w "%{http_code}" \
    -o "$dest" \
    "$url")"
  size="$(wc -c < "$dest" | tr -d ' ')"
  kind="$(file -b "$dest" 2>/dev/null || echo unknown)"
  python3 - "$MANIFEST" "$fname" "$url" "$http_code" "$size" "$kind" <<'PY'
import json
import sys
from pathlib import Path

p, fname, url, code, size, kind = sys.argv[1:7]
data = json.loads(Path(p).read_text(encoding="utf-8"))
data["files"].append({
    "name": fname,
    "url": url,
    "http_code": code,
    "bytes": int(size),
    "file_type": kind,
})
Path(p).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
done < "$OUT_DIR/urls.txt"

echo ""
echo "Issue: #$ISSUE — $TITLE"
echo "Repo:  $REPO"
echo "Saved: $OUT_DIR"
echo "Manifest: $MANIFEST"
if [[ "$COUNT" -eq 0 ]]; then
  echo "No user-attachments URLs found in issue body/comments."
fi
