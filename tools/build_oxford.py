# Gọn bộ Oxford 5000 cho trang web, chỉ giữ giọng Mỹ:
#   raw/oxford5000/full-word-5000-vi.json -> data/oxford5000.json
# Giữ: word, type, level, ipa (Mỹ), audio (mp3 Mỹ), vi, examples. Bỏ href, ogg, mọi trường Anh–Anh.
import json, os

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(root, 'raw', 'oxford5000', 'full-word-5000-vi.json')
out = os.path.join(root, 'data', 'oxford5000.json')

with open(src, encoding='utf-8') as f:
    data = json.load(f)

# phiên âm trong nguồn bị sai (lấy nhầm trang), ghi dạng đọc yếu (would) hoặc bỏ trống
IPA_FIX = {
    ('more', 'pronoun'): '/mɔːr/', ('most', 'pronoun'): '/moʊst/', ('much', 'pronoun'): '/mʌtʃ/',
    ('mission', 'noun'): '/ˈmɪʃn/', ('would', 'modal verb'): '/wʊd/',
    ('aged', 'adjective'): '/eɪdʒd/', ('beloved', 'adjective'): '/bɪˈlʌvɪd/',
}
# nguồn lấy nhầm trang của từ khác (many, impossible): ví dụ là của từ đó nên bỏ
WRONG_EXAMPLES = {('more', 'pronoun'), ('most', 'pronoun'), ('much', 'pronoun'), ('mission', 'noun')}
# nguồn lấy file đọc yếu /wəd/; đổi sang file đọc mạnh /wʊd/ cùng trang Oxford
AUDIO_FIX = {
    ('would', 'modal verb'):
    'https://www.oxfordlearnersdictionaries.com/media/english/us_pron/w/wou/would/would__us_8_rr.mp3',
}


def american(v):
    # Oxford ghi nguyên âm trong "go" là əʊ cả ở giọng Mỹ; ở đây đổi sang ký hiệu Mỹ thông dụng oʊ
    ipa = IPA_FIX.get((v['word'], v['type'])) or v['phonetics'].get('us', '')
    return ipa.strip().replace('əʊ', 'oʊ')


rows = []
for row in data:
    v = row['value']
    audio = AUDIO_FIX.get((v['word'], v['type']), v['us']['mp3'])
    rows.append({
        'word': v['word'],
        'type': v['type'],
        'level': v['level'].strip(),
        'ipa': american(v),
        # vài mục nguồn có link hỏng kiểu "…comundefined"
        'audio': audio if audio.endswith('.mp3') else '',
        'vi': v['vi'],
        'examples': [] if (v['word'], v['type']) in WRONG_EXAMPLES
        else [x.strip() for x in v['examples'] if x.strip()],
    })

with open(out, 'w', encoding='utf-8') as f:
    f.write('[\n' + ',\n'.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) for r in rows) + '\n]\n')
print(len(rows), 'mục ->', out)
print('không có audio:', [r['word'] for r in rows if not r['audio']])
