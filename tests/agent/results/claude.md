# 동작 테스트: claude

- 날짜: 2026-10-28
- 에이전트: 2.1.311 (Claude Code)
- 스킬 자리: 임시 작업 폴더
- SKILL.md 지문: be531ef2
- 모델: claude-opus-5-5, claude-sonnet-5-5
- 고르기: 34/35 맞음
- 본문 검사: 29/30 맞음. 어법, 문체, 분량, 강조를 어림 기준으로 잰다
- 검사 기록: 본문을 쓴 30건 가운데 30건이 check 로 성장 기록을 남겼다
- 여러 턴 흐름: 3/3 맞음
- 사용료: 8.89달러

## 요청 하나

| 케이스 | 기대 | 에이전트가 부른 것 | 판정 | 본문 검사 | 비고 | 초 |
|---|---|---|---|---|---|---|
| report | report | `compose --kind report --audience professor` | 맞음 | 맞음 | 거절된 도구 1건, 먼저 질문해 한 번 더 재촉함 | 121 |
| slides | slides | `compose --kind slides --audience listener` | 맞음 | 맞음 | 거절된 도구 2건, 먼저 질문해 한 번 더 재촉함 | 151 |
| minutes | minutes, 독자 teammate | `compose --kind minutes --audience teammate` | 맞음 | 맞음 | 거절된 도구 1건 | 53 |
| email | email, 독자 professor | `compose --kind email --audience professor --set markup=plain` | 맞음 | 맞음 | 거절된 도구 1건 | 37 |
| resume | resume | `compose --kind resume --audience recruiter` | 맞음 | 맞음 | 거절된 도구 1건 | 51 |
| cover-letter | cover-letter, 700자 | `compose --kind cover-letter --audience recruiter --chars 700` | 맞음 | 맞음 | 거절된 도구 2건, 먼저 질문해 한 번 더 재촉함 | 101 |
| portfolio | portfolio | `compose --kind portfolio` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 66 |
| interview | interview | `compose --kind interview --audience recruiter` | 맞음 | 맞음 | 거절된 도구 1건 | 52 |
| abstract | abstract | `compose --kind abstract --audience reviewer` | 맞음 | 맞음 | 거절된 도구 1건 | 49 |
| proposal | proposal | `compose --kind proposal` | 맞음 | 맞음 | 거절된 도구 6건, 먼저 질문해 한 번 더 재촉함 | 221 |
| design-doc | design-doc | `compose --kind design-doc` | 맞음 | 맞음 | 거절된 도구 1건 | 66 |
| pr | pr | `compose --kind pr` | 맞음 | 맞음 | 거절된 도구 1건 | 34 |
| postmortem | postmortem | `compose --kind postmortem --audience teammate` | 맞음 | 맞음 | 거절된 도구 2건 | 64 |
| spec | spec | `compose --kind spec` | 맞음 | 맞음 |  | 45 |
| work-report | work-report, 독자 manager | `compose --kind work-report --audience manager` | 맞음 | 맞음 | 거절된 도구 1건 | 33 |
| blog | blog | `compose --kind blog --audience peer-dev; compose --kind blog --audience peer-dev,reader --set exposure=public --set voice=prose --set length=full` | 맞음 | 맞음 | 거절된 도구 1건 | 85 |
| newsletter | newsletter | `compose --kind newsletter --audience reader` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 62 |
| sns | sns, register=haeyo, length=brief | `compose --kind sns --audience reader --set register=haeyo --set length=brief` | 맞음 | 맞음 | 거절된 도구 1건 | 32 |
| guide | guide | `compose --kind guide --audience teammate --set exposure=team` | 맞음 | 맞음 | 거절된 도구 1건 | 44 |
| notice | notice, 독자 stakeholder | `compose --kind notice --audience stakeholder` | 맞음 | 맞음 |  | 33 |
| script | script | `compose --kind script --audience listener` | 맞음 | 맞음 | 거절된 도구 2건, 먼저 질문해 한 번 더 재촉함 | 88 |
| set-register | report, register=polite | `compose --kind report --audience professor --set register=polite` | 맞음 | 맞음 | 거절된 도구 1건 | 42 |
| set-voice-length | postmortem, voice=prose, length=brief | `compose --kind postmortem --set voice=prose --set length=brief` | 맞음 | 맞음 | 거절된 도구 1건 | 36 |
| set-exposure | blog 또는 guide, exposure=team | `compose --kind guide --audience peer-dev,teammate --set exposure=team` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 57 |
| set-markup | notice, markup=plain | `compose --kind notice --audience teammate --set markup=plain --set length=brief` | 맞음 | 맞음 | 거절된 도구 1건 | 34 |
| audience-stakeholder | report, 독자 stakeholder | `compose --kind report --audience stakeholder` | 맞음 | 맞음 | 거절된 도구 1건 | 60 |
| folder-defaults | report, register=haeyo | `compose --kind report --audience professor` | 맞음 | 틀림: 어법 (합쇼체 17) | 거절된 도구 1건, 먼저 질문해 한 번 더 재촉함 | 60 |
| revise-email | email, 독자 professor, 다듬기 | `compose --kind email --audience professor --set markup=plain --revise` | 맞음 | 맞음 | 거절된 도구 1건 | 31 |
| toast | script 또는 종류 없음 | `compose --kind script --audience listener` | 맞음 | 맞음 | 거절된 도구 1건 | 39 |
| no-kind | 종류 없음 | `부르지 않음` | 틀림: compose 를 부르지 않았다 | - |  | 15 |
| skip-code | 부르지 않음 | `부르지 않음` | 맞음 | - |  | 10 |
| skip-question | 부르지 않음 | `부르지 않음` | 맞음 | - |  | 4 |
| no-profile | work-report | `compose --kind work-report --audience manager` | 맞음 | 맞음 |  | 29 |
| screen-theme | serve --detach, 화면 index | `serve --detach` | 맞음 | - |  | 21 |
| screen-setup | serve --detach, 화면 create | `serve --page create --detach` | 맞음 | - | 거절된 도구 1건 | 85 |

## 여러 턴 흐름

| 흐름 | 기대 | 에이전트가 부른 것 | 판정 | 비고 | 초 |
|---|---|---|---|---|---|
| flow-bootstrap | 프로필 profile.class=office, 프로필 persona.call=지수 님, 프로필 persona.docs=['work-report', 'email'] | `bootstrap --questions; bootstrap --class office --call 지수 님 --affiliation 플랫폼팀 백엔드 3년 차 --goal 보고서를 빨리 끝내기 --docs work-report,email --yes` | 맞음 | 거절된 도구 1건 | 50 |
| flow-restyle | 프로필 audiences.manager.register=haeyo | `set register haeyo --audience manager` | 맞음 | 거절된 도구 1건 | 61 |
| flow-here | 폴더 파일 defaults.register=plain, 프로필에 defaults.register 없음 | `set register plain --here` | 맞음 |  | 21 |
