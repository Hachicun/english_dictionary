# Thêm nghĩa tiếng Việt vào danh sách Oxford 5000, ghép theo từ + từ loại.
#   raw/oxford5000/full-word-5000.json + raw/thichhoc/*.jsonl -> raw/oxford5000/full-word-5000-vi.json
# Giữ nguyên mọi trường gốc, chỉ thêm value.vi (lấy từ senses_vi; [] nếu không khớp).
# value.vi là dữ liệu thichhoc-dict, giấy phép CC BY-SA 4.0 (phải ghi nguồn).
import json, glob, os

POS = {'noun': 'n', 'verb': 'v', 'adjective': 'adj', 'adverb': 'adv'}

# Các cặp mục dùng chung một mục thichhoc: chia nghĩa bằng tay theo (word, type, level).
OVERRIDE = {
    ('lie', 'verb', 'A1'): ['nằm'],
    ('lie', 'verb', 'B1'): ['nói dối; nói láo'],
    ('March', 'noun', 'A1'): ['tháng Ba'],
    ('march', 'noun', 'C1'): ['sự tiến triển, bước tiến', 'cuộc diễu hành, cuộc hành quân'],
}

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
base = os.path.join(root, 'raw', 'oxford5000', 'full-word-5000.json')
src = os.path.join(root, 'raw', 'thichhoc')
out = os.path.join(root, 'raw', 'oxford5000', 'full-word-5000-vi.json')

vi = {}
for path in sorted(glob.glob(os.path.join(src, '*.jsonl'))):
    with open(path, encoding='utf-8') as f:
        for line in f:
            e = json.loads(line)
            vi[(e['headword'].lower(), e['pos'])] = e.get('senses_vi', [])
if not vi:
    raise SystemExit('Không thấy dữ liệu trong ' + src)

with open(base, encoding='utf-8') as f:
    rows = json.load(f)

missing = []
for row in rows:
    v = row['value']
    v['vi'] = OVERRIDE.get((v['word'], v['type'], v['level'])) \
        or vi.get((v['word'].lower(), POS.get(v['type'])), [])
    if not v['vi']:
        missing.append(v)

with open(out, 'w', encoding='utf-8') as f:
    json.dump(rows, f, ensure_ascii=False, indent=4)
    f.write('\n')

other = sum(v['type'] not in POS for v in missing)
print(len(rows), 'mục ->', out)
print('có nghĩa Việt:', len(rows) - len(missing))
print('trống:', len(missing), f'(từ loại không hỗ trợ: {other}, không tìm thấy: {len(missing) - other})')
