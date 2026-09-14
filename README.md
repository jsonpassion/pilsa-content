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
│   ├── krv.json            # 개역한글 (1961) 전체 본문
│   ├── kjv.json            # King James Version 전체 본문
│   └── glossary_kjv.json   # KJV 옛 영어 단어장
└── voice/                  # 미리 만든 낭독 파일. 확언 en_aff.NN_0.m4a, 성경 절 kjv_PSA.23.1_0.m4a
tools/
└── build_manifest.py       # content/ 스캔, 체크섬 계산, manifest.json 생성
```

## 고치는 순서

1. `content/` 파일을 고친다. 파일 이름은 저장소 안에서 겹치지 않게 한다.
2. 낭독 문장이 바뀌었으면 앱 저장소의 `tools/render_voice.py`로 `content/voice/`를 다시 만든다.
3. `python3 tools/build_manifest.py`
4. 커밋하고 `main`에 푸시한다. 앱은 다음에 열릴 때 받아 간다.
5. 출시 전에는 앱 저장소의 `tools/pull_content.py`로 앱 번들 사본도 맞춘다.

## 성경 본문 출처 (2026-09-14 받음)

| 역본 | 원본 | 정리 |
|---|---|---|
| KJV | eBible.org `eng-kjv2006_vpl.zip` (1769 표준본, 외경 없음) | 인쇄본의 기울임 표시 [ ]와 문단 표시 ¶를 빼고 단어는 그대로 둠 |
| 개역한글 | SourceForge Zefania `SF_2022-09-19_KOR_KORRV` (위키문헌 기반 1952/1961) | 그대로 둠. 본문 속 [ ]는 개역한글 인쇄본에 있는 표시라 남김 |

- 두 역본 모두 시편 표제(다윗의 시, A Psalm of David.)를 1절에서 떼어 `titles`에 둔다 (116편).
- 변환: 앱 저장소의 `tools/import_bible.py` (zefania, vpl 형식).
- 개역한글 원본에 빠진 절 19개: 2CO.13.14, ACT.15.26, ACT.15.34, ACT.28.29, ACT.8.37, EZK.24.5, ISA.30.2, ISA.48.2, JER.21.2, LUK.17.36, LUK.23.17, MAT.18.11, MRK.11.26, MRK.15.28, MRK.9.44, MRK.9.46, PSA.72.20, ROM.16.24, ROM.9.2. 앞뒤 절에 합쳐졌을 수 있어 팩에 쓰지 않는다.
- 원본 오탈자로 보이는 곳: PSA.121.7 "여호와께 너를 지켜" (인쇄본은 "여호와께서"로 알려져 있음). 인쇄본으로 확인한 뒤에만 고친다.

## 주의

- 스키마를 바꾸면 `schema_version`을 올린다. 그 버전을 모르는 옛 앱은 동기화를 건너뛰고 번들 사본을 쓴다.
- 팩의 상품 ID와 가격은 앱 코드(`KoreanFlavor.swift`)에 있다. 판매 팩을 새로 넣을 때는 앱 업데이트가 함께 필요하다.

## 저작권

- 개역한글(1961)과 King James Version 본문은 퍼블릭 도메인이다. KJV는 영국에서는 왕실 특허 대상이다.
- 확언 문장, 한글 뜻, 단어 풀이, 팩 구성, 낭독 파일은 ForgeLab이 만들었다. 저장소는 앱 동기화를 위해 공개하며, 무단 복제와 재배포를 허용하지 않는다.
- 낭독 파일은 Kokoro-82M(Apache-2.0) 음성 모델로 만든 합성 음성이다.
