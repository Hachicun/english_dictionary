# Bảng tra audio giọng Mỹ: data/audio.json = { từ: đường_dẫn_mp3 }
# Nguồn: raw/kaikki/kaikki.org-dictionary-English.jsonl.gz (Wiktionary tiếng Anh, có link audio Wikimedia Commons)
# Không gọi API nào. Link đầy đủ = https://upload.wikimedia.org/wikipedia/commons/ + đường_dẫn_mp3
# Người đọc + giấy phép: app tự hỏi Commons khi hiển thị từ (xem index.html).
import gzip, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'raw', 'kaikki', 'kaikki.org-dictionary-English.jsonl.gz')
BASE = 'https://upload.wikimedia.org/wikipedia/commons/'
US = {'US', 'General-American', 'General American'}

d = json.load(open(os.path.join(ROOT, 'data', 'dict.json'), encoding='utf-8'))
heads, seen = [], set()
for e in d:
    h = e['headword'].lower()
    if h not in seen:
        seen.add(h)
        heads.append(h)

best = {}  # từ -> (ưu tiên, đường dẫn); ưu tiên 0 = file En-us-* (kiểu từ điển), 1 = bản ghi giọng Mỹ khác
for line in gzip.open(SRC, 'rt', encoding='utf-8'):
    if '"mp3_url"' not in line:
        continue
    e = json.loads(line)
    w = e.get('word', '').lower()
    if w not in seen:
        continue
    for s in e.get('sounds', []):
        url = s.get('mp3_url', '')
        tags = set(s.get('tags', [])) | set(s.get('raw_tags', []))
        name = s.get('audio', '')
        if not url.startswith(BASE) or not (tags & US or name.lower().startswith('en-us-')):
            continue
        cand = (0 if name.lower().startswith('en-us-') else 1, url[len(BASE):])
        if w not in best or cand[0] < best[w][0]:
            best[w] = cand

out = {w: p for w, (_, p) in best.items()}
path = os.path.join(ROOT, 'data', 'audio.json')
with open(path, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, separators=(',', ':'), sort_keys=True)
print(f'{len(out)} từ có audio giọng Mỹ -> {path} ({os.path.getsize(path) / 1e6:.1f} MB)')

single = [h for h in heads if re.fullmatch(r"[a-z][a-z'-]*", h)]
for n in (1000, 5000, 10000, 20000):
    print(f'Top {n} từ đơn: {sum(w in out for w in single[:n]) / n:.0%} có audio')
print('Thiếu trong top 300:', [w for w in single[:300] if w not in out][:40])
