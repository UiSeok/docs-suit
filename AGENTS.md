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
| `tests/agent/` | 실제 에이전트에 요청을 넣는 동작 테스트. 케이스는 `cases.py`, 에이전트별 결과는 `results/` |

## 고친 뒤에는 세 가지를 돌린다

```sh
python3 suit.py bundle      # 테마를 고쳤으면 웹 묶음을 다시 만든다
python3 suit.py selftest    # 데이터 정합과 값 정하는 순서, bootstrap, export 계약
node tests/parity.js        # 웹과 엔진이 같은 지침을 내는지
```

CI 가 같은 검사를 돌린다. `docs/themes.json` 이 테마와 다르면 selftest 가 실패한다.

## 요청을 고르는 단계는 동작 테스트로 본다

selftest 와 parity 는 문서 종류와 독자를 넘겨받은 뒤의 조립만 잰다. 요청 문장을 보고 종류와 독자를 고르는 일은 SKILL.md 를 읽은 에이전트가 하므로, 실제 에이전트에 요청을 넣어 확인한다.

```sh
python3 tests/agent/run.py --agent claude             # 케이스 전체
python3 tests/agent/run.py --agent antigravity --only sns  # 몇 건만
python3 tests/agent/run.py --agent claude --record    # 결과를 tests/agent/results/ 에 남긴다
```

SKILL.md 문구나 문서 종류, 독자를 바꿨으면 돌리고 `--record` 로 결과를 갱신한다. 새 문서 종류를 더하면 `cases.py` 에도 케이스를 하나 더한다. 에이전트 로그인이 필요하고 돌릴 때마다 사용료가 들어서 CI 에는 넣지 않는다.

실행기는 홈 폴더의 스킬과 프로필을 건드리지 않는다. 케이스마다 임시 폴더에 프로젝트 단위 스킬과 시험 프로필을 두고, `DOCS_SUIT_LOG` 로 suit.py 호출 인자를 모아 채점한다. Claude Code 는 사용자 설정과 개인 스킬, MCP 를 끄고 돌려서 처음 설치한 사람과 조건을 맞춘다.

Antigravity CLI 는 한 번 실행 모드에서 확인 창을 띄우지 못해 명령을 거절하고, 작업 폴더 단위 설정이 없다. 그래서 `~/.gemini/antigravity-cli/settings.json` 의 `permissions.allow` 에 `command(python3 <suit.py 절대 경로>)` 를 더한 뒤 돌린다. Codex CLI 는 exec 모드가 샌드박스 안에서 확인 없이 돌아서 따로 설정하지 않는다.

무료 요금제로 돌리면 사용 한도에 걸릴 수 있다. 한도 때문에 답 없이 끝난 건은 틀림이 아니라 재지 못함으로 표에 남고, 맞은 비율에서도 뺀다.

## 지킬 것

- `suit.py` 의 `resolve` 나 `compose` 를 고치면 `docs/core.js` 도 같은 커밋에서 고친다. 두 쪽의 출력은 글자 하나까지 같아야 하고, parity 가 그것을 잰다.
- 표준 라이브러리만 쓰고 파이썬 3.9 문법 안에서 쓴다. 웹은 빌드 도구 없이 정적 파일로 둔다.
- 규칙 문서는 평어체로 쓴다. 한 문장에 한 맥락을 담고, 대시로 문장을 잇지 않고, 개수는 "세 가지" 처럼 단위 명사로 센다.
- 새 값의 `## 보기` 는 다른 값과 같은 예문인 정류장 대기 시간 조사로 쓴다. 같은 예문이어야 카드끼리 견줄 수 있다.
- 규칙과 예문에 특정 회사의 이름과 내부 정보, 실제 사람의 이름과 연락처를 넣지 않는다. 공개 저장소다.
- 프로필은 `~/.config/docs-suit/` 에 두고 저장소에 넣지 않는다. export 를 시험할 때는 `--dest` 로 임시 폴더에 쓰고, 실제 홈 폴더의 스킬 자리에 쓰는 일은 사람에게 확인받은 뒤에 한다.
