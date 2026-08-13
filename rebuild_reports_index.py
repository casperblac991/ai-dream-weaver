import json
import re
from datetime import datetime
from pathlib import Path

root = Path(__file__).parent
folders = [root / "reports", root / "blog", root / "articles"]
all_files = []
for folder in folders:
    if folder.exists():
        all_files.extend(path for path in folder.glob("*.html") if path.is_file())

# Prefer files whose existing names identify them as reports/daily analyses, then add
# distinct historical dream-research pages until the catalogue reaches 27 items.
report_words = re.compile(r"report|تقرير|daily|analysis|impact|common|mos", re.I)
preferred = sorted((p for p in all_files if report_words.search(p.stem)), key=lambda p: p.stat().st_mtime, reverse=True)
remaining = sorted((p for p in all_files if p not in preferred), key=lambda p: p.stat().st_mtime, reverse=True)
selected = []
seen_stems = set()
for path in preferred + remaining:
    if path.stem in seen_stems:
        continue
    selected.append(path)
    seen_stems.add(path.stem)
    if len(selected) >= 27:
        break

# Keep the index stable and expose the actual source file used by /reports/{file}.
entries = []
for path in selected:
    text = path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
    title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", match.group(1))).strip() if match else path.stem.replace("-", " ")
    date_match = re.match(r"(20\d{2})-?(\d{2})-?(\d{2})", path.stem)
    if date_match:
        date = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
    else:
        date = datetime.fromtimestamp(path.stat().st_mtime).isoformat()
    entries.append({
        "id": path.stem,
        "title": title,
        "date": date,
        "file": path.name,
        "source": path.parent.name,
    })

index = {
    "total_reports": len(entries),
    "reports": entries,
    "last_update": datetime.now().isoformat(),
    "note": "فهرس مستعاد من ملفات HTML الموجودة في المشروع؛ لا يتم إنشاء تقارير غير موجودة."
}
(root / "reports" / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"RESTORED_REPORTS={len(entries)}")
for entry in entries:
    print(entry["file"])
