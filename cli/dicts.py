#!/usr/bin/env python3
"""dicts: từ điển Anh–Việt trên terminal, dùng chung data/ với bản web.

  dicts hello        tra một từ
  dicts -s hello     tra và phát âm giọng Mỹ
  dicts -a hello     hiện hết ví dụ (mặc định 3 ví dụ mỗi từ loại)
  dicts              chế độ liên tục: gõ từ, Enter; "-s từ" để nghe; "-a từ" xem hết ví dụ; "-s" để nghe lại từ vừa tra;
                     Enter trống hoặc q để thoát
"""

import argparse
import difflib
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
CACHE = Path.home() / ".cache" / "dicts"
COMMONS = "https://upload.wikimedia.org/wikipedia/commons/"
POS = {
    "n": "danh từ", "v": "động từ", "adj": "tính từ", "adv": "trạng từ",
    "noun": "danh từ", "verb": "động từ", "adjective": "tính từ", "adverb": "trạng từ",
    "preposition": "giới từ", "pronoun": "đại từ", "determiner": "từ hạn định", "conjunction": "liên từ",
    "exclamation": "thán từ", "number": "số từ", "ordinal number": "số thứ tự",
    "modal verb": "động từ khuyết thiếu", "auxiliary verb": "trợ động từ", "linking verb": "động từ nối",
    "definite article": "mạo từ xác định", "indefinite article": "mạo từ không xác định",
    "infinitive marker": "từ đứng trước động từ nguyên mẫu",
}
# Từ loại bộ Oxford -> ký hiệu trong dict.json
SHORT = {"noun": "n", "verb": "v", "adjective": "adj", "adverb": "adv"}
SOURCE = "Nguồn: thichhoc-dict · CC BY-SA 4.0"
SOURCE_OX = "Bộ 5000 từ, phiên âm, ví dụ, audio: Oxford Learner's Dictionaries © Oxford University Press"
MAX_EXAMPLES = 3  # -a để xem hết
CLOSE_ENOUGH = 0.85  # độ giống để hỏi "Có phải là ...?"

USE_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ


def style(text, code):
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


class Dictionary:
    def __init__(self):
        entries = json.loads((DATA / "dict.json").read_text(encoding="utf-8"))
        self.audio = json.loads((DATA / "audio.json").read_text(encoding="utf-8"))
        # Bộ Oxford 5000 (giọng Mỹ), ưu tiên khi tra; thiếu file thì chỉ dùng bộ lớn
        ox = DATA / "oxford5000.json"
        self.ox_by_word = {}
        for e in json.loads(ox.read_text(encoding="utf-8")) if ox.exists() else []:
            self.ox_by_word.setdefault(e["word"].lower(), []).append(e)
        self.by_word = {}
        for e in entries:
            # Mỗi mục được lập chỉ mục theo từ gốc và các dạng chia (giống bản web)
            forms = {e["headword"].lower(), *(f.lower() for f in e.get("inflections", []))}
            for w in forms:
                self.by_word.setdefault(w, []).append(e)
        self.words = list({**self.by_word, **self.ox_by_word})
        self.last = []  # [(từ, link audio Oxford)] của lần tra thành công, để nghe lại

    def lookup(self, q):
        """(mục bộ 5000, mục bộ lớn cần hiện thêm) — cùng quy tắc với bản web."""
        # Khớp đúng từ gõ, cộng mục của từ gốc nếu từ gõ là dạng chia
        ox = list(self.ox_by_word.get(q, []))
        for d in self.by_word.get(q, []):
            for e in self.ox_by_word.get(d["headword"].lower(), []):
                if SHORT.get(e["type"]) == d.get("pos") and e not in ox:
                    ox.append(e)
        # Khớp từ gốc trước, rồi tới dạng chia
        other = sorted(self.by_word.get(q, []), key=lambda e: e["headword"].lower() != q)
        if ox:
            # Chỉ thêm từ loại của đúng từ gõ mà bộ 5000 không có
            covered = {SHORT.get(e["type"]) for e in ox if e["word"].lower() == q}
            other = [e for e in other if e["headword"].lower() == q and e.get("pos") not in covered]
        return ox, other

    def suggest(self, q, n=5):
        cands = difflib.get_close_matches(q, self.words, n=20, cutoff=0.6)
        # Độ giống giảm dần; cùng độ giống thì ưu tiên từ có độ dài gần với từ gõ
        cands.sort(key=lambda w: (-difflib.SequenceMatcher(None, q, w).ratio(), abs(len(w) - len(q))))
        return cands[:n]


def run_quiet(cmd):
    return subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def fetch_audio(url):
    """Tải file audio một lần rồi lưu cache: nghe lại nhanh và không cần mạng."""
    CACHE.mkdir(parents=True, exist_ok=True)
    local = CACHE / url.removeprefix(COMMONS).split("://")[-1].replace("/", "_")
    if not local.exists():
        req = urllib.request.Request(url, headers={"User-Agent": "dicts-cli/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                local.write_bytes(r.read())
        except OSError:
            return None
    return local


def play_file(f):
    s = str(f)
    for cmd in (
        ["mpv", "--no-video", "--really-quiet", s],
        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", s],
        ["afplay", s],
    ):
        if shutil.which(cmd[0]) and run_quiet(cmd):
            return True
    return False


def play(d, word, url=""):
    # Audio Oxford (Mỹ) trước, rồi Wikimedia Commons
    path = d.audio.get(word.lower())
    for src in (url, COMMONS + path if path else ""):
        if src:
            f = fetch_audio(src)
            if f and play_file(f):
                return
    # Không có file audio hoặc không phát được: dùng giọng máy của macOS
    if shutil.which("say") and run_quiet(["say", "-v", "Samantha", word]):
        return
    print("(không phát được âm: cần mpv, ffplay, hoặc macOS 'say')")


def speak_all(d, items):
    # Từ loại khác nhau có thể đọc khác nhau (record): phát lần lượt từng audio riêng
    for word, url in items:
        play(d, word, url)


def note_inflection(d, q, headword):
    if q != headword.lower() and any(e["headword"] == headword for e in d.by_word.get(q, [])):
        print(style(f"  {q} là dạng chia của {headword}", "2"))


def show_oxford(d, q, hits, all_examples):
    groups = {}
    for e in hits:
        groups.setdefault(e["word"], []).append(e)
    for word, items in groups.items():
        print(style(word, "1"))
        note_inflection(d, q, word.lower())
        for e in items:
            head = POS.get(e["type"], e["type"]) + (f" · {e['level']}" if e["level"] else "")
            print(f"  {head}" + (f"  {e['ipa']}" if e["ipa"] else ""))
            for i, sense in enumerate(e["vi"], 1):
                print(f"    {i}. {sense}")
            if not e["vi"]:
                print(style("    Chưa có nghĩa tiếng Việt.", "2"))
            shown = e["examples"] if all_examples else e["examples"][:MAX_EXAMPLES]
            for x in shown:
                print(style(f"    • {x}", "2"))
            if len(e["examples"]) > len(shown):
                print(style(f"    (còn {len(e['examples']) - len(shown)} ví dụ, thêm -a để xem)", "2"))
        print()


def show_entries(d, q, hits, shown):
    groups = {}
    for e in hits:
        groups.setdefault(e["headword"], []).append(e)
    for headword, items in groups.items():
        if headword.lower() in shown:
            print(style(f"{headword}: từ loại khác (ngoài bộ 5000)", "2"))
        else:
            print(style(headword, "1"))
            note_inflection(d, q, headword)
        for e in items:
            pos = POS.get(e.get("pos", ""), e.get("pos", ""))
            pron = e.get("pron") or ""
            print(f"  {pos}" + (f"  {pron}" if pron else ""))
            for i, sense in enumerate(e.get("senses_vi", []), 1):
                print(f"    {i}. {sense}")
        print()


def to_speak(q, ox, other):
    """Đọc đúng từ gõ trước; nếu từ gõ chỉ là dạng chia thì đọc từ gốc."""
    exact = [e for e in ox if e["word"].lower() == q]
    if not exact:
        own = [e["headword"] for e in other if e["headword"].lower() == q]
        if own:
            return [(own[0], "")]
        if not ox:
            return [(other[0]["headword"], "")]
    first = (exact or ox)[0]["word"]
    return list(dict.fromkeys((e["word"], e["audio"]) for e in ox if e["word"] == first))


def lookup_and_show(d, word, speak=False, all_examples=False):
    q = word.strip().lower()
    if not q:
        return True
    ox, other = d.lookup(q)
    if ox or other:
        d.last = to_speak(q, ox, other)
        show_oxford(d, q, ox, all_examples)
        show_entries(d, q, other, {e["word"].lower() for e in ox})
        if speak:
            speak_all(d, d.last)
        if ox:
            print(style(SOURCE_OX, "2"))
        print(style(SOURCE, "2"))
        return True

    print(f'Không có "{word.strip()}".')
    close = d.suggest(q)
    if not close:
        return False
    ratios = [difflib.SequenceMatcher(None, q, w).ratio() for w in close[:2]]
    # Chỉ hỏi khi có một từ rõ ràng giống nhất; nếu hai từ ngang nhau thì liệt kê
    clear_top = len(ratios) == 1 or ratios[0] > ratios[1]
    if sys.stdin.isatty() and ratios[0] >= CLOSE_ENOUGH and clear_top:
        try:
            ans = input(f'Có phải là "{close[0]}"? [Y/n] ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return False
        if ans in ("", "y", "yes"):
            return lookup_and_show(d, close[0], speak, all_examples)
        return False
    print("Có phải là: " + ", ".join(close) + "?")
    return False


def loop(d, all_examples=False):
    print('dicts: gõ từ để tra, "-s từ" để nghe, "-a từ" để xem hết ví dụ, "-s" để nghe lại, Enter trống hoặc q để thoát.')
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line or line.lower() == "q":
            break
        if line == "-s":
            if d.last:
                speak_all(d, d.last)
            else:
                print("Chưa có từ nào để nghe lại.")
            continue
        speak, show_all = False, all_examples
        while line.startswith(("-s ", "-a ")):
            speak = speak or line[1] == "s"
            show_all = show_all or line[1] == "a"
            line = line[3:].strip()
        lookup_and_show(d, line, speak, show_all)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="dicts",
        description="Từ điển Anh–Việt. Không truyền từ: vào chế độ tra liên tục.",
    )
    parser.add_argument("word", nargs="?", help="từ cần tra")
    parser.add_argument("-s", "--speak", action="store_true", help="phát âm giọng Mỹ")
    parser.add_argument("-a", "--all", action="store_true", help="hiện hết ví dụ")
    args = parser.parse_args(argv)

    d = Dictionary()
    if args.word is None:
        loop(d, args.all)
        return 0
    return 0 if lookup_and_show(d, args.word, args.speak, args.all) else 1


if __name__ == "__main__":
    sys.exit(main())
