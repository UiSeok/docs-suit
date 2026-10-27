# 이 저장소에서 일하는 법

docs-suit 를 고치는 사람과 AI 에이전트가 읽는 작업 규칙이다. 쓰는 법은 `README.md`, 앞으로 할 일은 `ROADMAP.md` 에 있다.

## 구조

| 자리 | 내용 |
|---|---|
| `suit.py` | 엔진 한 파일. bootstrap, compose, export, bundle, selftest |
| `themes/ko/` | 한국어 테마 팩. 축과 값은 `axes.yaml`, 독자와 문서 종류는 `defaults.yaml`, 클래스는 `classes/`, 페르소나 질문은 `persona.yaml` |
| `themes/ko/<축>/<값>.md` | 값마다 규칙 문서 한 장. 끝의 `## 보기` 절은 웹 카드에만 쓰고 지침에는 싣지 않는다 |
| `themes/ko/kinds/<종류>.md` | 문서 종류의 틀 |
| `docs/` | 웹 고르개. `core.js` 가 조립하고 `themes.json` 은 `suit.py bundle` 이 만든다 |
| `tests/parity.js` | 웹과 엔진의 조립 결과를 견준다 |

## 고친 뒤에는 세 가지를 돌린다

```sh
python3 suit.py bundle      # 테마를 고쳤으면 웹 묶음을 다시 만든다
python3 suit.py selftest    # 데이터 정합과 값 정하는 순서, bootstrap, export 계약
node tests/parity.js        # 웹과 엔진이 같은 지침을 내는지
```

CI 가 같은 검사를 돌린다. `docs/themes.json` 이 테마와 다르면 selftest 가 실패한다.

## 지킬 것

- `suit.py` 의 `resolve` 나 `compose` 를 고치면 `docs/core.js` 도 같은 커밋에서 고친다. 두 쪽의 출력은 글자 하나까지 같아야 하고, parity 가 그것을 잰다.
- 표준 라이브러리만 쓰고 파이썬 3.9 문법 안에서 쓴다. 웹은 빌드 도구 없이 정적 파일로 둔다.
- 규칙 문서는 평어체로 쓴다. 한 문장에 한 맥락을 담고, 대시로 문장을 잇지 않고, 개수는 "세 가지" 처럼 단위 명사로 센다.
- 새 값의 `## 보기` 는 다른 값과 같은 예문인 정류장 대기 시간 조사로 쓴다. 같은 예문이어야 카드끼리 견줄 수 있다.
- 규칙과 예문에 특정 회사의 이름과 내부 정보, 실제 사람의 이름과 연락처를 넣지 않는다. 공개 저장소다.
- 프로필은 `~/.config/docs-suit/` 에 두고 저장소에 넣지 않는다. export 를 시험할 때는 `--dest` 로 임시 폴더에 쓰고, 실제 홈 폴더의 스킬 자리에 쓰는 일은 사람에게 확인받은 뒤에 한다.
