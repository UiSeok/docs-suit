# 동작 테스트: claude

- 날짜: 2026-10-28
- 에이전트: 2.1.311 (Claude Code)
- 스킬 자리: 임시 작업 폴더
- SKILL.md 지문: 7c175ade
- 모델: claude-sonnet-5-5
- 고르기: 36/36 맞음
- 본문 검사: 32/32 맞음. 어법, 문체, 분량, 강조를 어림 기준으로 잰다
- 검사 기록: 본문을 쓴 32건 가운데 32건이 check 로 성장 기록을 남겼다
- 여러 턴 흐름: 3/5 맞음
- 사용료: 6.10달러

## 요청 하나

| 케이스 | 기대 | 에이전트가 부른 것 | 판정 | 본문 검사 | 비고 | 초 |
|---|---|---|---|---|---|---|
| report | report | `compose --kind report --audience professor` | 맞음 | 맞음 | 거절된 도구 1건, 먼저 질문해 한 번 더 재촉함 | 90 |
| slides | slides | `compose --kind slides --audience listener` | 맞음 | 맞음 | 거절된 도구 1건, 먼저 질문해 한 번 더 재촉함 | 96 |
| minutes | minutes, 독자 teammate | `compose --kind minutes --audience teammate --set exposure=team` | 맞음 | 맞음 |  | 26 |
| email | email, 독자 professor | `compose --kind email --audience professor --set markup=plain` | 맞음 | 맞음 |  | 30 |
| resume | resume | `compose --kind resume --audience recruiter` | 맞음 | 맞음 |  | 42 |
| cover-letter | cover-letter, 700자 | `compose --kind cover-letter --audience recruiter --set markup=plain --chars 700` | 맞음 | 맞음 |  | 33 |
| portfolio | portfolio | `compose --kind portfolio --audience recruiter` | 맞음 | 맞음 |  | 36 |
| interview | interview | `compose --kind interview --audience recruiter` | 맞음 | 맞음 |  | 42 |
| abstract | abstract | `compose --kind abstract --audience reviewer --set exposure=submit` | 맞음 | 맞음 |  | 30 |
| proposal | proposal | `compose --kind proposal` | 맞음 | 맞음 |  | 67 |
| design-doc | design-doc | `compose --kind design-doc` | 맞음 | 맞음 |  | 44 |
| pr | pr | `compose --kind pr` | 맞음 | 맞음 |  | 31 |
| postmortem | postmortem | `compose --kind postmortem` | 맞음 | 맞음 |  | 38 |
| spec | spec | `compose --kind spec` | 맞음 | 맞음 |  | 39 |
| biz-report | biz-report, 독자 manager | `compose --kind biz-report --audience manager` | 맞음 | 맞음 |  | 40 |
| work-report | work-report, 독자 manager | `compose --kind work-report --audience manager` | 맞음 | 맞음 |  | 31 |
| blog | blog | `compose --kind blog --audience peer-dev` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 71 |
| newsletter | newsletter | `compose --kind newsletter --audience reader` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 53 |
| sns | sns, register=haeyo, length=brief | `compose --kind sns --audience reader --set register=haeyo --set length=brief` | 맞음 | 맞음 |  | 29 |
| guide | guide | `compose --kind guide --audience teammate --set exposure=team` | 맞음 | 맞음 |  | 38 |
| notice | notice, 독자 stakeholder | `compose --kind notice --audience stakeholder` | 맞음 | 맞음 |  | 33 |
| script | script | `compose --kind script --audience listener` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 75 |
| set-register | report, register=polite | `compose --kind report --audience professor --set register=polite` | 맞음 | 맞음 | 거절된 도구 2건, 먼저 질문해 한 번 더 재촉함 | 78 |
| set-voice-length | postmortem, voice=prose, length=brief | `compose --kind postmortem --audience teammate --set voice=prose --set length=brief` | 맞음 | 맞음 |  | 38 |
| set-exposure | blog 또는 guide, exposure=team | `compose --kind guide --audience peer-dev --set exposure=team` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 56 |
| set-markup | notice, markup=plain | `compose --kind notice --audience teammate --set markup=plain --set exposure=team` | 맞음 | 맞음 |  | 31 |
| audience-stakeholder | report, 독자 stakeholder | `compose --kind report --audience stakeholder` | 맞음 | 맞음 |  | 45 |
| folder-defaults | report, register=haeyo | `compose --kind report --audience professor` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 58 |
| revise-email | email, 독자 professor, 다듬기 | `compose --kind email --audience professor --revise --set markup=plain` | 맞음 | 맞음 |  | 26 |
| toast | script 또는 종류 없음 | `compose --kind script --audience listener` | 맞음 | 맞음 |  | 29 |
| no-kind | 종류 없음 | `compose --set markup=plain --set register=haeyo --set voice=prose --set exposure=submit` | 맞음 | 맞음 |  | 47 |
| skip-code | 부르지 않음 | `부르지 않음` | 맞음 | - |  | 9 |
| skip-question | 부르지 않음 | `부르지 않음` | 맞음 | - |  | 5 |
| no-profile | work-report | `compose --kind work-report --audience manager` | 맞음 | 맞음 |  | 25 |
| screen-theme | serve --detach, 화면 index | `serve --detach` | 맞음 | - |  | 19 |
| screen-setup | serve --detach, 화면 create | `serve --page create --detach` | 맞음 | - |  | 20 |

## 여러 턴 흐름

| 흐름 | 기대 | 에이전트가 부른 것 | 판정 | 비고 | 초 |
|---|---|---|---|---|---|
| flow-bootstrap | 프로필 profile.class=office, 프로필 persona.call=지수 님, 프로필 persona.docs=['work-report', 'email'] | `bootstrap --questions` | 틀림: 프로필의 profile.class 가 None 이다, 프로필의 persona.call 가 None 이다, 프로필의 persona.docs 가 None 이다 |  | 28 |
| flow-restyle | 프로필 audiences.manager.register=haeyo | `set register haeyo --audience manager` | 맞음 |  | 46 |
| flow-kind | 프로필 kinds.work-report.voice=prose, 프로필에 defaults.voice 없음 | `set voice prose --kind work-report` | 맞음 |  | 18 |
| flow-here | 폴더 파일 defaults.register=plain, 프로필에 defaults.register 없음 | `set register plain --here` | 맞음 |  | 18 |
| flow-learn | 프로필 어딘가에 register=polite, 내 문체 문서, 샘플 이름과 수치 새지 않음 | `learn samples/01-weekly.md samples/02-review.md samples/03-wrapup.md samples/04-request.md; learn --guide; set register polite; set voice prose; set emphasis none; voice set - --samples samples/01-weekly.md samples/02-review.md samples/03-wrapup.md samples/04-request.md` | 틀림: 내 문체 문서를 남기지 않았다 | 거절된 도구 1건 | 81 |
