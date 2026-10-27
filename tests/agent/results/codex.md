# 동작 테스트: codex

- 날짜: 2026-10-27
- 에이전트: codex-cli 0.164.0
- 스킬 자리: 임시 작업 폴더
- SKILL.md 지문: 4ab23827
- 모델: 알 수 없음
- 요금제: free
- 고르기: 28/28 맞음
- 본문 검사: 24/26 맞음. 어법, 문체, 분량, 강조를 어림 기준으로 잰다
- 검사 기록: 본문을 쓴 26건 가운데 11건이 check 로 성장 기록을 남겼다
- 여러 턴 흐름: 3/3 맞음
- 사용료: 에이전트가 알려 주지 않음

## 요청 하나

| 케이스 | 기대 | 에이전트가 부른 것 | 판정 | 본문 검사 | 비고 | 초 |
|---|---|---|---|---|---|---|
| report | report | `compose --kind report --audience professor` | 맞음 | 맞음 | check 를 부르지 않음 | 21 |
| slides | slides | `compose --kind slides --audience listener` | 맞음 | 맞음 |  | 32 |
| minutes | minutes, 독자 teammate | `compose --kind minutes --audience teammate` | 맞음 | 맞음 | check 를 부르지 않음 | 12 |
| email | email, 독자 professor | `compose --kind email --audience professor` | 맞음 | 맞음 | check 를 부르지 않음 | 12 |
| resume | resume | `compose --kind resume --audience recruiter` | 맞음 | 맞음 |  | 21 |
| cover-letter | cover-letter, 700자 | `compose --kind cover-letter --audience recruiter --set register=plain --set voice=prose --chars 700` | 맞음 | 맞음 | check 를 부르지 않음 | 26 |
| portfolio | portfolio | `compose --kind portfolio --audience recruiter --set voice=prose --set length=brief` | 맞음 | 맞음 |  | 14 |
| interview | interview | `compose --kind interview --audience recruiter` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 31 |
| abstract | abstract | `compose --kind abstract --audience reviewer` | 맞음 | 맞음 | check 를 부르지 않음 | 17 |
| proposal | proposal | `compose --kind proposal` | 맞음 | 맞음 |  | 46 |
| design-doc | design-doc | `compose --kind design-doc --audience peer-dev` | 맞음 | 틀림: 분량 (2158자, 한도 1500자) | check 를 부르지 않음 | 52 |
| pr | pr | `compose --kind pr --audience peer-dev` | 맞음 | 맞음 |  | 19 |
| postmortem | postmortem | `compose --kind postmortem --audience teammate` | 맞음 | 맞음 | check 를 부르지 않음 | 31 |
| spec | spec | `compose --kind spec --audience stakeholder` | 맞음 | 맞음 |  | 31 |
| work-report | work-report, 독자 manager | `compose --kind work-report --audience manager` | 맞음 | 맞음 | check 를 부르지 않음 | 9 |
| blog | blog | `compose --kind blog --audience peer-dev` | 맞음 | 맞음 | check 를 부르지 않음 | 20 |
| newsletter | newsletter | `compose --kind newsletter --audience reader` | 맞음 | 맞음 |  | 22 |
| sns | sns, register=haeyo, length=brief | `compose --kind sns --set register=haeyo --set length=brief --chars 180` | 맞음 | 맞음 | check 를 부르지 않음 | 7 |
| set-register | report, register=polite | `compose --kind report --audience professor --set register=polite` | 맞음 | 맞음 | check 를 부르지 않음 | 35 |
| set-voice-length | postmortem, voice=prose, length=brief | `compose --kind postmortem --audience teammate --set voice=prose --set length=brief --chars 500` | 맞음 | 맞음 |  | 23 |
| set-exposure | blog, exposure=team | `compose --kind blog --audience peer-dev,teammate` | 맞음 | 틀림: 어법 (합쇼체 2 · 해요체 1) | check 를 부르지 않음 | 16 |
| audience-stakeholder | report, 독자 stakeholder | `compose --kind report --audience stakeholder` | 맞음 | 맞음 | check 를 부르지 않음 | 29 |
| folder-defaults | report, register=haeyo | `compose --kind report --audience professor` | 맞음 | 맞음 | check 를 부르지 않음 | 34 |
| ambiguous-notice | email 또는 minutes, 독자 stakeholder | `compose --kind email --audience stakeholder --set length=brief` | 맞음 | 맞음 | check 를 부르지 않음 | 13 |
| no-kind | 종류 없음 | `compose; compose --audience listener --set voice=prose --set register=polite --set length=brief` | 맞음 | 맞음 |  | 17 |
| skip-code | 부르지 않음 | `부르지 않음` | 맞음 | - |  | 5 |
| skip-question | 부르지 않음 | `부르지 않음` | 맞음 | - |  | 4 |
| no-profile | work-report | `compose --kind work-report --audience manager` | 맞음 | 맞음 |  | 12 |

## 여러 턴 흐름

| 흐름 | 기대 | 에이전트가 부른 것 | 판정 | 비고 | 초 |
|---|---|---|---|---|---|
| flow-bootstrap | 프로필 profile.class=office, 프로필 persona.call=지수 님, 프로필 persona.docs=['work-report', 'email'] | `bootstrap --questions; bootstrap --help; bootstrap --class office --call 지수 님 --affiliation 플랫폼팀 백엔드 3년 차 --goal 보고서를 빨리 끝내는 것 --docs work-report,email --facts  --dislikes  --yes` | 맞음 |  | 29 |
| flow-restyle | 프로필 audiences.manager.register=haeyo | `set register haeyo --audience manager` | 맞음 |  | 19 |
| flow-here | 폴더 파일 defaults.register=plain, 프로필에 defaults.register 없음 | `set --help; set register plain --here` | 맞음 |  | 11 |
