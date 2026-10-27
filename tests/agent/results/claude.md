# 동작 테스트: claude

- 날짜: 2026-10-27
- 에이전트: 2.1.311 (Claude Code)
- 스킬 자리: 임시 작업 폴더
- SKILL.md 지문: 4ab23827
- 모델: claude-opus-5-5
- 고르기: 27/28 맞음
- 본문 검사: 24/25 맞음. 어법, 문체, 분량, 강조를 어림 기준으로 잰다
- 검사 기록: 본문을 쓴 25건 가운데 25건이 check 로 성장 기록을 남겼다
- 여러 턴 흐름: 3/3 맞음
- 사용료: 8.88달러

## 요청 하나

| 케이스 | 기대 | 에이전트가 부른 것 | 판정 | 본문 검사 | 비고 | 초 |
|---|---|---|---|---|---|---|
| report | report | `compose --kind report --audience professor` | 맞음 | 맞음 | 거절된 도구 1건, 먼저 질문해 한 번 더 재촉함 | 152 |
| slides | slides | `compose --kind slides --audience listener` | 맞음 | 맞음 | 거절된 도구 1건, 먼저 질문해 한 번 더 재촉함 | 129 |
| minutes | minutes, 독자 teammate | `compose --kind minutes --audience teammate` | 맞음 | 맞음 |  | 36 |
| email | email, 독자 professor | `compose --kind email --audience professor` | 맞음 | 틀림: 강조 (굵은 글씨 있음) | 먼저 질문해 한 번 더 재촉함 | 60 |
| resume | resume | `compose --kind resume --audience recruiter` | 맞음 | 맞음 |  | 48 |
| cover-letter | cover-letter, 700자 | `compose --kind cover-letter --audience recruiter --chars 700` | 맞음 | 맞음 | 거절된 도구 1건 | 66 |
| portfolio | portfolio | `compose --kind portfolio --audience recruiter` | 맞음 | 맞음 |  | 48 |
| interview | interview | `compose --kind interview --audience recruiter` | 맞음 | 맞음 |  | 47 |
| abstract | abstract | `compose --kind abstract --audience reviewer` | 맞음 | 맞음 |  | 38 |
| proposal | proposal | `compose --kind proposal` | 맞음 | 맞음 | 거절된 도구 4건, 먼저 질문해 한 번 더 재촉함 | 195 |
| design-doc | design-doc | `compose --kind design-doc` | 맞음 | 맞음 |  | 61 |
| pr | pr | `compose --kind pr --audience peer-dev` | 맞음 | 맞음 |  | 42 |
| postmortem | postmortem | `compose --kind postmortem` | 맞음 | 맞음 | 거절된 도구 1건 | 78 |
| spec | spec | `compose --kind spec` | 맞음 | 맞음 |  | 57 |
| work-report | work-report, 독자 manager | `compose --kind work-report --audience manager` | 맞음 | 맞음 |  | 48 |
| blog | blog | `compose --kind blog` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 116 |
| newsletter | newsletter | `compose --kind newsletter --audience reader` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 62 |
| sns | sns, register=haeyo, length=brief | `compose --kind sns --audience reader --set register=haeyo --set length=brief` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 51 |
| set-register | report, register=polite | `compose --kind report --audience professor --set register=polite` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 79 |
| set-voice-length | postmortem, voice=prose, length=brief | `compose --kind postmortem --set voice=prose --set length=brief` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 60 |
| set-exposure | blog, exposure=team | `compose --kind blog --audience peer-dev` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 70 |
| audience-stakeholder | report, 독자 stakeholder | `compose --kind report --audience stakeholder` | 맞음 | 맞음 |  | 72 |
| folder-defaults | report, register=haeyo | `compose --kind report --audience professor` | 맞음 | 맞음 | 거절된 도구 1건, 먼저 질문해 한 번 더 재촉함 | 99 |
| ambiguous-notice | email 또는 minutes, 독자 stakeholder | `compose --kind email --audience stakeholder` | 맞음 | 맞음 |  | 38 |
| no-kind | 종류 없음 | `부르지 않음` | 틀림: compose 를 부르지 않았다 | - |  | 21 |
| skip-code | 부르지 않음 | `부르지 않음` | 맞음 | - |  | 14 |
| skip-question | 부르지 않음 | `부르지 않음` | 맞음 | - |  | 6 |
| no-profile | work-report | `compose --kind work-report --audience manager` | 맞음 | 맞음 |  | 37 |

## 여러 턴 흐름

| 흐름 | 기대 | 에이전트가 부른 것 | 판정 | 비고 | 초 |
|---|---|---|---|---|---|
| flow-bootstrap | 프로필 profile.class=office, 프로필 persona.call=지수 님, 프로필 persona.docs=['work-report', 'email'] | `bootstrap --questions; bootstrap --class office --call 지수 님 --affiliation 플랫폼팀 백엔드 3년 차 --goal 보고서를 빨리 끝내기 --docs work-report,email --yes` | 맞음 |  | 41 |
| flow-restyle | 프로필 audiences.manager.register=haeyo | `set register haeyo --audience manager` | 맞음 |  | 57 |
| flow-here | 폴더 파일 defaults.register=plain, 프로필에 defaults.register 없음 | `set register plain --here` | 맞음 |  | 23 |
