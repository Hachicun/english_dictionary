# Gọn dữ liệu thichhoc-dict: raw/thichhoc/*.jsonl -> data/dict.json
# Giữ: headword, pos, pron, inflections, senses_vi. Sắp theo tần suất (phổ biến trước).
import json, glob, os, sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(root, 'raw', 'thichhoc')
out = os.path.join(root, 'data', 'dict.json')

rows = []
for path in sorted(glob.glob(os.path.join(src, '*.jsonl'))):
    with open(path, encoding='utf-8') as f:
        for line in f:
            e = json.loads(line)
            r = {'headword': e['headword'], 'pos': e.get('pos', '')}
            if e.get('pron'):
                r['pron'] = e['pron']
            if e.get('inflections'):
                r['inflections'] = e['inflections']
            r['senses_vi'] = e.get('senses_vi', [])
            rows.append((-(e.get('freq') or 0), e['headword'].lower(), r))

rows.sort(key=lambda x: (x[0], x[1]))
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'w', encoding='utf-8') as f:
    f.write('[\n' + ',\n'.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) for _, _, r in rows) + '\n]\n')
print(len(rows), 'entries ->', out)
