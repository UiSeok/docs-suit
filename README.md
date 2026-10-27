# docs-suit

문서에 입히는 옷(suit)입니다. 도구 모음을 뜻하는 suite 가 아닙니다.

AI 에게 글을 맡길 때 매번 "합쇼체로, 결론 먼저, 출처는 각주로" 를 다시 쓰지 않도록, 글의 모양과 말투를 축으로 나눠 갈아입히는 테마 엔진입니다. 처음 받으면 게임에서 캐릭터를 만들듯 클래스(직업)를 고르고 페르소나를 입력합니다. 그다음 문서 종류만 말하면 클래스와 독자, 문서 종류에 맞는 규칙을 골라 AI 에게 줄 지침 한 장으로 조립합니다.

출력은 마크다운 지침 한 장이라서 어떤 AI 에도 붙습니다. Claude Code, Codex, Antigravity CLI, Grok Build, Cursor 는 공용 규격인 Agent Skills(`SKILL.md`)로, ChatGPT 와 Claude, Gemini, Grok 웹 채팅은 붙여 넣기로 씁니다.

## 처음 받았을 때

파이썬 3.9 이상만 있으면 되고, 따로 설치할 패키지는 없습니다.

```sh
git clone https://github.com/dodokim-lab/docs-suit.git && cd docs-suit
python3 suit.py bootstrap
```

bootstrap 은 세 단계를 묻습니다.
1. 클래스 고르기. 클래스가 기본 말투와 주력 문서를 정합니다.
2. 페르소나 여섯 가지. 호칭, 소속, 목표, 자주 쓰는 문서, AI 가 모르는 나, 싫어하는 말투입니다. 답하기 싫은 것은 넘어갑니다.
3. 쓰는 AI 도구 고르기. 고른 도구에 docs-suit 스킬을 설치합니다.

답은 `~/.config/docs-suit/profile.yaml` 에 남습니다. 저장소 밖이라 실수로 커밋되지 않습니다. 에이전트에게 "docs-suit 세팅해 줘" 라고 해도 됩니다. 스킬이 같은 질문을 대신 묻고 `bootstrap --class … --yes` 로 저장합니다.

## 클래스

| 클래스 | 이런 사람 | 주력 문서 |
|---|---|---|
| 학생 | 과제와 수행평가, 조별 활동, 발표를 하는 중고등학생과 대학생 | 보고서, 발표 자료, 회의록·공유자료, 메일 |
| 취업 준비생 | 이력서와 자기소개서, 포트폴리오로 문을 두드리는 사람 | 이력서, 자기소개서, 포트폴리오, 면접 답변 |
| 대학원생·연구자 | 논문과 연구계획서, 학회 발표를 쓰는 사람 | 논문 초록, 연구계획서, 보고서, 발표 자료 |
| 개발자 | 설계 문서와 PR, 장애 회고, 기술 글을 쓰는 사람 | 설계 문서, PR 설명, 사건 회고, 블로그·기술 글 |
| 기획자·PM | 기획서와 회의록, 진행 보고로 사람들을 한 방향으로 모으는 사람 | 기획서, 회의록, 업무 보고, 발표 자료 |
| 직장인 | 업무 보고와 메일, 회의록을 매일 쓰는 사람 | 업무 보고, 메일, 회의록, 발표 자료 |
| 크리에이터 | 블로그와 뉴스레터, SNS 로 독자를 만나는 사람 | 블로그, 뉴스레터, SNS 글 |

주력이 아닌 문서도 모두 쓸 수 있습니다. 문서 종류는 열여덟 가지이고 `python3 suit.py list` 로 봅니다.

## 쓰는 법

```sh
python3 suit.py compose --kind report                    # 보고서 지침 조립
python3 suit.py compose --kind cover-letter --chars 1000 # 자기소개서, 공백 포함 1,000자 제한
python3 suit.py compose --kind pr --set register=polite  # 축 하나만 바꿔 입기
python3 suit.py compose --class researcher --kind slides # 이번만 다른 클래스로
python3 suit.py get --kind spec                          # 축마다 어떤 값이 어디서 왔는지
python3 suit.py set register haeyo --audience teammate   # 팀원에게는 해요체로 남기기
python3 suit.py export --agent claude,codex              # 도구에 스킬 다시 설치
python3 suit.py export --agent web                       # 웹 채팅용 지침을 파일로
```

| 도구 | 연결 |
|---|---|
| Claude Code | `~/.claude/skills/docs-suit/SKILL.md`. output style 로 쓰려면 `compose --format output-style -o ~/.claude/output-styles/<이름>.md` |
| Codex CLI | `~/.agents/skills/docs-suit/SKILL.md` |
| Antigravity CLI | `~/.gemini/config/skills/docs-suit/SKILL.md`. suit.py 실행을 물으면 항상 허용을 고른다 |
| Cursor | `~/.cursor/skills/docs-suit/SKILL.md` |
| Grok Build | Claude 자리와 공용 자리에 함께 설치 |
| 웹 채팅 | `export --agent web` 이 만든 지침이나 웹 고르개에서 복사한 지침을 맞춤 지침, 프로젝트, Gem 에 붙여 넣기 |

Claude Code, Antigravity CLI, Codex CLI 는 실제 요청을 넣어 스킬이 불리는 것을 확인했습니다. 결과는 `tests/agent/results/` 에 있습니다. Codex CLI 는 ChatGPT 무료 요금제로도 됩니다. Antigravity 와 Codex 는 작업 폴더의 `.agents/skills/` 로 확인했습니다. 두 도구의 전역 자리와 나머지 도구의 자리는 2차 자료 기준이라 각 도구 문서로 확인이 필요합니다. 스킬 파일은 이 저장소의 `suit.py` 를 절대 경로로 부르므로, `git pull` 하면 모든 도구에 바로 반영됩니다. 저장소를 옮겼다면 `export` 를 다시 돌립니다.

## 웹 고르개

설치 없이 쓰는 화면입니다. 클래스와 문서 종류, 독자를 칩으로 고르면, 축마다 같은 예문을 값별로 써 본 카드가 나란히 보입니다. 평어체와 합쇼체, 해요체가 같은 문장에서 어떻게 달라지는지, 발표 디자인 세 가지가 같은 슬라이드에서 어떻게 보이는지 보고 누르면 됩니다. 오른쪽에서 조립된 지침을 복사합니다. GitHub Pages 주소는 https://dodokim-lab.github.io/docs-suit/ 이고, 로컬에서는 `docs` 폴더에서 `python3 -m http.server` 를 띄웁니다.

## 축과 값

| 축 | 값 | 중립 기본값 |
|---|---|---|
| 디자인 · 문서 | Sakura, new.css | Sakura |
| 디자인 · 발표 | 종이 톤, 어두운 고대비, 흰 바탕 한 색 | 흰 바탕 한 색 |
| 문체 | 줄글, 개조식 | 줄글 |
| 어법 | 평어체, 합쇼체, 해요체 | 평어체 |
| 용어 수준 | 일상어, 풀어 쓰고 전문어 곁들임, 전문 용어 그대로 | 풀어 쓰기 |
| 골격 | 결론 먼저, 시간순, 문제·원인·대책, 목적·방법·결과·고찰, 문제·해결·효과 | 결론 먼저 |
| 분량 | 짧게, 한 쪽, 상세. 글자수는 `--chars` 로 따로 겁니다 | 한 쪽 |
| 강조 | 굵은 글씨, 쓰지 않음 | 굵은 글씨 |
| 그림 | 표 먼저, mermaid, 그리지 않음 | 표 먼저 |
| 출처 표기 | 각주, 참고문헌(APA), 본문 링크 | 각주 |
| 공개 범위 | 인터넷 공개, 정해진 상대, 팀 내부 | 인터넷 공개 |
| AI 사용 고지 | 각주로 밝힘, 부록으로 밝힘, 밝히지 않음 | 밝히지 않음 |

어떤 옷을 입어도 지키는 공통 바닥이 있습니다. 모르면 지어내지 않고 `[확인 필요]` 로 남기기, 확인한 사실과 추정을 섞지 않기, 수치를 지어내지 않기 같은 규칙입니다.

## 값은 이 순서로 정해집니다

위에 있는 것이 이깁니다.

1. 문서 종류가 고정한 축
2. 직접 고른 값 (`--set`, 웹에서 누른 카드)
3. 프로필의 독자별 값
4. 문서 종류가 권하는 값
5. 프로필의 기본값
6. 독자 프로필
7. 클래스 기본값
8. 중립 기본값

클래스를 독자보다 아래에 둔 까닭은, 어법이나 용어 수준은 쓰는 사람보다 읽는 사람이 정하는 게 맞기 때문입니다. 공개 범위는 예외입니다. 개인정보가 새지 않게 하려는 안전 축이라서, 직접 고른 값과 프로필은 범위를 더 좁힐 때만 이깁니다.

페르소나는 지침의 "쓰는 사람" 절에 실리고, AI 가 관점과 예시를 고르는 데만 씁니다. 직접 넣으라고 하지 않는 한 본문에 옮겨 적지 않도록 지침에 적어 둡니다.

## 내 옷을 만들어 입기

이 저장소를 fork 해서 `themes/ko/` 아래 문서를 고치면 그대로 내 테마가 됩니다.
- 값을 새로 만들 때는 `themes/ko/<축>/<값>.md` 를 만들고 `axes.yaml` 에 한 줄 더합니다. 문서 끝 `## 보기` 절에 공통 예문을 그 값으로 써 두면 웹 고르개가 카드로 보여 줍니다. 보기 절은 AI 에게 주는 지침에는 실리지 않습니다.
- 클래스는 `themes/ko/classes/<id>.yaml`, 문서 종류는 `defaults.yaml` 과 `kinds/<종류>.md` 입니다.
- 고친 뒤 `python3 suit.py bundle` 로 웹 묶음을 다시 만들고, `python3 suit.py selftest` 와 `node tests/parity.js` 로 확인합니다. parity 는 웹과 엔진이 608가지 조합에서 같은 지침을 내는지 글자 하나까지 견줍니다. GitHub Actions 도 같은 검사를 돌립니다.

## 함께 쓰면 좋은 것

- `starters/start.md`: 일을 맡길 때 첫 메시지. 상황과 이유는 요약하지 말고 줄글로 다 풀고, 꼭 지킬 조건만 목록으로 뽑습니다.
- `starters/review.md`: 다 쓴 글을 새 대화에서 처음 보는 채점자에게 검토받는 프롬프트입니다.

## 비슷한 프로젝트와 다른 점

조립형 프롬프트 모음은 이미 있습니다. microsoft/PromptKit 은 페르소나와 형식을 조립하지만 엔지니어링 문서용이고, 문체와 독자 축은 없습니다. simonpainter/tone 은 공통 기준과 형식별 지침을 두지만 영어이고 조립 엔진이 없습니다. docs-suit 는 한국어 어법과 클래스, 문서 종류, 독자를 축으로 다루고, 값마다 보기를 그려 눈으로 고르게 하며, 웹과 터미널, AI 코딩 도구가 같은 데이터로 같은 지침을 조립한다는 점이 다릅니다.

## 라이선스

MIT 입니다. `themes/ko/visual-doc/` 의 CSS 두 개는 각자의 MIT 라이선스를 따르며, 출처와 해시는 `themes/ko/PROVENANCE.md` 에 있습니다. 앞으로 할 일은 `ROADMAP.md` 에 있습니다.
