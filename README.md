# pilsa-content

Pilsa(필사) 앱이 동기화하는 콘텐츠 저장소. 앱 코드는 비공개 저장소에 따로 있다.

앱은 열릴 때와 다시 앞으로 올 때 `manifest.json`을 받아 파일별 체크섬을 비교하고, 바뀐 파일만 내려받아 바로 반영한다. 인터넷이 없으면 앱에 들어 있는 사본을 쓴다.

## 구조

```
manifest.json               # 앱이 처음 읽는 파일: 스키마, 버전, 파일 목록과 SHA-256
content/
├── kr/packs.json           # 한국 플레이버의 팩 구성 (오늘의 말씀, 계획 팩, 확언 팩)
├── collections/
│   └── affirmations.json   # 영어 확언과 한글 뜻, 단어 풀이
├── bible/
│   ├── books.json          # 성경 책 이름 (한글, 영어)
│   ├── krv.json            # 개역한글 (1961)
│   ├── kjv.json            # King James Version
│   └── glossary_kjv.json   # KJV 옛 영어 단어장
└── voice/                  # 미리 만든 낭독 파일 <번역ID>_<본문키>_<줄번호>.m4a
tools/
└── build_manifest.py       # content/ 스캔, 체크섬 계산, manifest.json 생성
```

## 고치는 순서

1. `content/` 파일을 고친다. 파일 이름은 저장소 안에서 겹치지 않게 한다.
2. 낭독 문장이 바뀌었으면 앱 저장소의 `tools/render_voice.py`로 `content/voice/`를 다시 만든다.
3. `python3 tools/build_manifest.py`
4. 커밋하고 `main`에 푸시한다. 앱은 다음에 열릴 때 받아 간다.
5. 출시 전에는 앱 저장소의 `tools/pull_content.py`로 앱 번들 사본도 맞춘다.

## 주의

- 성경 본문은 아직 샘플이다. 원문 대조 전까지 `verification` 표시를 지우지 않는다.
- 스키마를 바꾸면 `schema_version`을 올린다. 그 버전을 모르는 옛 앱은 동기화를 건너뛰고 번들 사본을 쓴다.
- 팩의 상품 ID와 가격은 앱 코드(`KoreanFlavor.swift`)에 있다. 판매 팩을 새로 넣을 때는 앱 업데이트가 함께 필요하다.

## 저작권

- 개역한글(1961)과 King James Version 본문은 퍼블릭 도메인이다. KJV는 영국에서는 왕실 특허 대상이다.
- 확언 문장, 한글 뜻, 단어 풀이, 팩 구성, 낭독 파일은 ForgeLab이 만들었다. 저장소는 앱 동기화를 위해 공개하며, 무단 복제와 재배포를 허용하지 않는다.
- 낭독 파일은 Kokoro-82M(Apache-2.0) 음성 모델로 만든 합성 음성이다.
