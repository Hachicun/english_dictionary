# Từ điển Anh–Việt (giọng Mỹ)

Tra từ tiếng Anh trên web và trên terminal. Bộ chính là 5000 từ Oxford (cấp độ A1–C1, phiên âm, ví dụ, audio giọng Mỹ)
kèm nghĩa tiếng Việt; từ nằm ngoài bộ này lấy từ bộ từ điển lớn thichhoc-dict.

Web: https://hachicun.github.io/english_dictionary/

## Dùng

**Web** (HTML thuần, không backend):

```bash
python3 -m http.server 8000
```

Mở `http://localhost:8000`.

**Terminal** (`cli/dicts.py`, chỉ cần Python 3; phát âm dùng `mpv`, `ffplay` hoặc `afplay`, không được thì `say`):

```bash
ln -sfn "$PWD/cli/dicts.py" ~/bin/dicts
```

| Lệnh | Việc |
|---|---|
| `dicts hello` | tra một từ |
| `dicts -s hello` | tra và phát âm |
| `dicts -a hello` | hiện hết ví dụ (mặc định 3 ví dụ mỗi từ loại) |
| `dicts` | tra liên tục; Enter trống hoặc `q` để thoát |

Chuyển thư mục dự án thì chạy lại lệnh `ln` ở trên.

## Cấu trúc

| Đường dẫn | Nội dung |
|---|---|
| `index.html` | trang tra từ |
| `cli/dicts.py` | bản terminal |
| `data/oxford5000.json` | bộ 5000 từ, ưu tiên khi tra |
| `data/dict.json` | bộ lớn: từ ngoài bộ 5000 và nhận ra dạng chia |
| `data/audio.json` | bảng audio giọng Mỹ trên Wikimedia Commons cho bộ lớn |
| `tools/` | script dựng dữ liệu |
| `raw/` | dữ liệu nguồn (không đưa lên git) |
| `archive/` | file không còn dùng (không đưa lên git) |

## Bộ 5000 từ

`data/oxford5000.json` là một mảng, mỗi mục là một từ ở một từ loại:

```json
{"word": "…", "type": "noun", "level": "A1", "ipa": "/…/", "audio": "https://…mp3", "vi": ["…"], "examples": ["…"]}
```

5948 mục. Cùng một từ có thể có cấp độ khác nhau theo từ loại.

Chỗ đã chỉnh so với nguồn (`tools/build_oxford.py`):

- Nguyên âm trong *go* đổi từ `əʊ` (cách ghi của Oxford, cả ở giọng Mỹ) sang `oʊ`.
- `more`, `most`, `much` (đại từ) và `mission` (danh từ) bị nguồn lấy nhầm trang của từ khác: sửa phiên âm, bỏ ví dụ.
- `would`: dùng phiên âm và audio dạng đọc mạnh.
- `aged`, `beloved`: bổ sung phiên âm còn trống.

Giới hạn: 356 mục chưa có nghĩa tiếng Việt (chủ yếu là số từ, đại từ, giới từ…); 5 mục không có audio Oxford và
5 mục không có cấp độ (`major` danh từ, `accounting`, `angrily`, `cleaning`, `feeding`); một số ví dụ gắn nhãn
tiếng Anh–Anh.

## Dựng lại dữ liệu

Nguồn cần có trong `raw/`:

- `raw/thichhoc/*.jsonl`: https://github.com/thichhoc-org/thichhoc-dict
- `raw/oxford5000/full-word-5000.json`: https://github.com/tyypgzl/Oxford-5000-words
- `raw/kaikki/kaikki.org-dictionary-English.jsonl.gz`: https://kaikki.org/dictionary/English/

Bộ 5000 (chạy theo thứ tự):

```bash
python3 tools/merge_vi.py
```

```bash
python3 tools/build_oxford.py
```

Bộ lớn và bảng audio Commons:

```bash
python3 tools/build.py
```

```bash
python3 tools/build_audio.py
```

## Dự án dùng chung

[voice2IPA2word](https://github.com/Hachicun/voice2IPA2word) (luyện phát âm, game Leo Tháp) lấy cấp độ, nghĩa và audio
từ `data/oxford5000.json`. Dựng lại bộ 5000 xong thì chạy `python3 build_oxford.py` bên đó.

## Nguồn dữ liệu và giấy phép

- Từ điển Anh–Việt thichhoc.com (thichhoc-dict), giấy phép CC BY-SA 4.0.
  https://github.com/thichhoc-org/thichhoc-dict
  Nguồn gốc: WordNet 3.1 (Princeton), CMUdict (CMU), Wiktionary. Đã chỉnh sửa dữ liệu (rút gọn trường).
  WordNet 3.1 Copyright 2011 The Trustees of Princeton University. All rights reserved.
  → `data/dict.json` phát hành theo CC BY-SA 4.0.
- Bộ 5000 từ: danh sách từ, cấp độ, phiên âm, ví dụ lấy từ Oxford Learner's Dictionaries
  (qua https://github.com/tyypgzl/Oxford-5000-words, repo không ghi giấy phép); audio phát từ máy chủ Oxford.
  Nội dung © Oxford University Press, **không** thuộc CC BY-SA; chỉ trường `vi` trong `data/oxford5000.json` là
  CC BY-SA 4.0.
- Audio ngoài bộ 5000: Wikimedia Commons (danh sách lấy từ dữ liệu Wiktionary của kaikki.org). Mỗi file có người đọc
  và giấy phép riêng, hiển thị cạnh từng từ trong trang web.
