# Từ điển Anh–Việt (giọng Mỹ)

Từ điển web chạy hoàn toàn ở trình duyệt: HTML thuần, không backend.

- `index.html` — trang tra từ
- `data/dict.json` — dữ liệu từ điển (tạo bằng `tools/build.py`)
- `data/audio.json` — bảng audio giọng Mỹ trên Wikimedia Commons (tạo bằng `tools/build_audio.py`)

## Nguồn dữ liệu và giấy phép

- Dữ liệu từ điển: Từ điển Anh–Việt thichhoc.com (thichhoc-dict), giấy phép CC BY-SA 4.0.
  https://github.com/thichhoc-org/thichhoc-dict
  Nguồn gốc: WordNet 3.1 (Princeton), CMUdict (CMU), Wiktionary. Đã chỉnh sửa dữ liệu (rút gọn trường).
  WordNet 3.1 Copyright 2011 The Trustees of Princeton University. All rights reserved.
  → `data/dict.json` phát hành theo CC BY-SA 4.0.
- Audio: Wikimedia Commons (danh sách lấy từ dữ liệu Wiktionary của kaikki.org). Mỗi file có người đọc và giấy phép riêng, hiển thị cạnh từng từ trong app.
