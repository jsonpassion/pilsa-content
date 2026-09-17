#!/usr/bin/env python3
"""콘텐츠를 올리기 전에, 그리고 GitHub에 올라올 때마다 도는 점검.

앱은 열릴 때마다 이 저장소의 manifest.json을 따라 파일을 받는다. 잘못 올린 파일이 바로 앱에 퍼지지 않게 막는다.

1. 모든 JSON이 읽힌다
2. manifest.json이 최신이고 파일 체크섬이 맞다
3. packs.json의 본문 키가 역본과 컬렉션에 있다
4. 스티커 목록의 그림과 배경음악 파일이 있다
5. 파일 이름(basename)이 겹치지 않는다 (앱은 이름으로 찾는다)

    python3 tools/validate.py
"""
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"


def main():
    problems = []
    data = {}
    for path in sorted(CONTENT.rglob("*.json")):
        try:
            data[path.relative_to(CONTENT).as_posix()] = json.loads(path.read_text(encoding="utf-8"))
        except Exception as error:
            problems.append(f"JSON을 읽을 수 없음: {path.relative_to(ROOT)} ({error})")

    check = subprocess.run([sys.executable, str(ROOT / "tools/build_manifest.py"), "--check"], capture_output=True, text=True)
    if check.returncode != 0:
        problems.append("manifest.json이 최신이 아님: python3 tools/build_manifest.py 후 다시 올리세요")

    names = Counter(p.name for p in CONTENT.rglob("*") if p.is_file())
    problems += [f"같은 파일 이름이 여러 곳에 있음: {name}" for name, count in names.items() if count > 1]

    verses = {tid: data.get(f"bible/{tid}.json", {}).get("verses", {}) for tid in ("krv", "kjv", "dra")}
    collections = {"affirm": data.get("collections/affirmations.json", {}).get("items", {}), "buddhist": data.get("collections/buddhist.json", {}).get("items", {})}
    bible_translations = {"bible": ["krv", "kjv"], "catholic": ["dra"]}
    for pack in data.get("kr/packs.json", []):
        collection = pack.get("collection", "bible")
        for day in pack.get("days", []):
            key = day.get("passage", "")
            if collection in bible_translations:
                try:
                    book, chapter, span = key.split(".")
                    start, _, end = span.partition("-")
                    ids = [f"{book}.{chapter}.{v}" for v in range(int(start), int(end or start) + 1)]
                except ValueError:
                    problems.append(f"{pack['id']}: 본문 키 형식이 이상함 {key}")
                    continue
                targets = [pack["translationID"]] if pack.get("translationID") else bible_translations[collection]
                for tid in targets:
                    missing = [v for v in ids if v not in verses.get(tid, {})]
                    if missing:
                        problems.append(f"{pack['id']} {key} [{tid}] 없음: {missing}")
            elif key not in collections.get(collection, {}):
                problems.append(f"{pack['id']}: {collection}에 없는 글 {key}")

    music_ids = set()
    for track in data.get("music/music.json", {}).get("tracks", []):
        if track.get("id") in music_ids:
            problems.append(f"배경음악 id가 겹침: {track.get('id')}")
        music_ids.add(track.get("id"))
        if not (CONTENT / "music" / f"{track.get('file')}.m4a").exists():
            problems.append(f"배경음악 {track.get('id')}: 파일 없음 {track.get('file')}.m4a")

    for pack in data.get("stickers/stickers.json", {}).get("packs", []):
        if pack.get("access") not in ("free", "plus"):
            problems.append(f"스티커 팩 {pack.get('id')}: access는 free나 plus")
        for name in pack.get("stickers", []):
            if not (CONTENT / "stickers" / f"{name}.png").exists():
                problems.append(f"스티커 팩 {pack.get('id')}: 그림 없음 {name}")

    for problem in problems:
        print(f"✗ {problem}")
    print("✓ 콘텐츠 점검 통과" if not problems else f"문제 {len(problems)}개")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
