# 동작 테스트: claude

- 날짜: 2026-10-27
- 에이전트: 2.1.311 (Claude Code)
- 스킬 자리: 임시 작업 폴더
- SKILL.md 지문: c2606f36
- 모델: claude-opus-5-5
- 고르기: 28/28 맞음
- 본문 검사: 23/25 맞음. 어법, 문체, 분량, 강조를 어림 기준으로 잰다
- 여러 턴 흐름: 3/3 맞음
- 사용료: 7.91달러

## 요청 하나

| 케이스 | 기대 | 에이전트가 부른 것 | 판정 | 본문 검사 | 비고 | 초 |
|---|---|---|---|---|---|---|
| report | report | `compose --kind report --audience professor` | 맞음 | 맞음 | 거절된 도구 1건, 먼저 질문해 한 번 더 재촉함 | 144 |
| slides | slides | `compose --kind slides --audience listener` | 맞음 | 잴 거리 없음 | 거절된 도구 1건, 먼저 질문해 한 번 더 재촉함 | 101 |
| minutes | minutes, 독자 teammate | `compose --kind minutes --audience teammate` | 맞음 | 맞음 |  | 26 |
| email | email, 독자 professor | `compose --kind email --audience professor` | 맞음 | 틀림: 강조 (굵은 글씨 있음) |  | 27 |
| resume | resume | `compose --kind resume --audience recruiter` | 맞음 | 맞음 |  | 38 |
| cover-letter | cover-letter, 700자 | `compose --kind cover-letter --audience recruiter --chars 700` | 맞음 | 맞음 | 거절된 도구 1건 | 47 |
| portfolio | portfolio | `compose --kind portfolio --audience recruiter` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 43 |
| interview | interview | `compose --kind interview --audience recruiter` | 맞음 | 맞음 |  | 40 |
| abstract | abstract | `compose --kind abstract --audience reviewer` | 맞음 | 맞음 |  | 35 |
| proposal | proposal | `compose --kind proposal` | 맞음 | 맞음 | 거절된 도구 5건, 먼저 질문해 한 번 더 재촉함 | 161 |
| design-doc | design-doc | `compose --kind design-doc` | 맞음 | 틀림: 분량 (2046자, 한도 1500자) | 거절된 도구 1건 | 87 |
| pr | pr | `compose --kind pr --audience peer-dev` | 맞음 | 맞음 |  | 28 |
| postmortem | postmortem | `compose --kind postmortem` | 맞음 | 맞음 | 거절된 도구 1건 | 59 |
| spec | spec | `compose --kind spec` | 맞음 | 맞음 | 거절된 도구 1건, 먼저 질문해 한 번 더 재촉함 | 85 |
| work-report | work-report, 독자 manager | `compose --kind work-report --audience manager` | 맞음 | 맞음 |  | 29 |
| blog | blog | `compose --kind blog --audience reader,peer-dev` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 62 |
| newsletter | newsletter | `compose --kind newsletter --audience reader` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 45 |
| sns | sns, register=haeyo, length=brief | `compose --kind sns --audience reader --set register=haeyo --set length=brief` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 26 |
| set-register | report, register=polite | `compose --kind report --audience professor --set register=polite` | 맞음 | 맞음 | 거절된 도구 1건, 먼저 질문해 한 번 더 재촉함 | 109 |
| set-voice-length | postmortem, voice=prose, length=brief | `compose --kind postmortem --set voice=prose --set length=brief` | 맞음 | 맞음 | 거절된 도구 1건, 먼저 질문해 한 번 더 재촉함 | 49 |
| set-exposure | blog, exposure=team | `compose --kind blog --audience peer-dev` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 45 |
| audience-stakeholder | report, 독자 stakeholder | `compose --kind report --audience stakeholder` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 66 |
| folder-defaults | report, register=haeyo | `compose --kind report --audience professor` | 맞음 | 맞음 | 거절된 도구 1건, 먼저 질문해 한 번 더 재촉함 | 76 |
| ambiguous-notice | email 또는 minutes, 독자 stakeholder | `compose --kind email --audience stakeholder` | 맞음 | 맞음 |  | 35 |
| no-kind | 종류 없음 | `compose --audience listener --set register=polite --set voice=prose` | 맞음 | 맞음 |  | 35 |
| skip-code | 부르지 않음 | `부르지 않음` | 맞음 | - |  | 12 |
| skip-question | 부르지 않음 | `부르지 않음` | 맞음 | - |  | 5 |
| no-profile | work-report | `compose --kind work-report --audience manager` | 맞음 | 맞음 |  | 24 |

## 여러 턴 흐름

| 흐름 | 기대 | 에이전트가 부른 것 | 판정 | 비고 | 초 |
|---|---|---|---|---|---|
| flow-bootstrap | 프로필 profile.class=office, 프로필 persona.call=지수 님, 프로필 persona.docs=['work-report', 'email'] | `bootstrap --questions; bootstrap --class office --call 지수 님 --affiliation 플랫폼팀 백엔드 3년 차 --goal 보고서를 빨리 끝내기 --docs work-report,email --yes` | 맞음 |  | 50 |
| flow-restyle | 프로필 audiences.manager.register=haeyo | `set register haeyo --audience manager` | 맞음 | 거절된 도구 1건 | 49 |
| flow-here | 폴더 파일 defaults.register=plain, 프로필에 defaults.register 없음 | `set --help; set register plain --here` | 맞음 |  | 25 |
