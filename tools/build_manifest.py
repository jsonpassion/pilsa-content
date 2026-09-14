#!/usr/bin/env python3
"""content/ 아래 파일을 훑어 manifest.json을 만든다.

앱(Pilsa)은 열릴 때마다 이 매니페스트를 받아 파일별 SHA-256을 비교하고,
바뀐 파일만 내려받아 번들 사본 대신 쓴다. version은 모든 체크섬을 합친 해시라
콘텐츠가 하나라도 바뀌면 달라진다.

규칙
- 파일 이름(basename)은 저장소 전체에서 겹치지 않아야 한다. 앱은 이름으로 파일을 찾는다.
- 앱이 모르는 schema_version이 오면 앱은 동기화를 건너뛴다.

    python3 tools/build_manifest.py          # manifest.json 쓰기
    python3 tools/build_manifest.py --check  # 매니페스트가 최신인지 확인 (커밋 전)
"""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
MANIFEST = ROOT / "manifest.json"
SCHEMA_VERSION = 1


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    files = sorted(p for p in CONTENT.rglob("*") if p.is_file() and not p.name.startswith("."))
    names: dict[str, Path] = {}
    entries = []
    for path in files:
        if path.name in names:
            raise SystemExit(f"파일 이름이 겹칩니다: {path.relative_to(ROOT)} / {names[path.name].relative_to(ROOT)}")
        names[path.name] = path
        if path.suffix == ".json":
            json.loads(path.read_text(encoding="utf-8"))  # 깨진 JSON은 올리지 않는다
        entries.append({
            "id": path.name,
            "path": str(path.relative_to(ROOT)),
            "checksum_sha256": sha256(path),
            "size": path.stat().st_size,
        })
    version = hashlib.sha256("".join(e["checksum_sha256"] for e in entries).encode()).hexdigest()[:12]
    return {"schema_version": SCHEMA_VERSION, "version": version, "entries": entries}


def main():
    manifest = build()
    if "--check" in sys.argv:
        current = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
        if current.get("version") != manifest["version"] or current.get("entries") != manifest["entries"]:
            raise SystemExit("manifest.json이 오래됐습니다. python3 tools/build_manifest.py 를 실행하세요.")
        print(f"manifest.json 최신 (version {manifest['version']}, 파일 {len(manifest['entries'])}개)")
        return
    existing = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    if existing.get("version") == manifest["version"] and existing.get("entries") == manifest["entries"]:
        manifest["generated_at"] = existing.get("generated_at")
    else:
        manifest["generated_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    ordered = {k: manifest[k] for k in ["schema_version", "version", "generated_at", "entries"]}
    MANIFEST.write_text(json.dumps(ordered, ensure_ascii=False, indent=1) + "\n")
    size = sum(e["size"] for e in manifest["entries"])
    print(f"manifest.json version {manifest['version']}, 파일 {len(manifest['entries'])}개, {size / 1e6:.2f}MB")


if __name__ == "__main__":
    main()
