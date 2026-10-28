# 동작 테스트: codex

- 날짜: 2026-10-28
- 에이전트: codex-cli 0.164.0
- 스킬 자리: 임시 작업 폴더
- SKILL.md 지문: 63f4a856, 7c175ade
- 모델: 알 수 없음
- 요금제: free
- 고르기: 36/36 맞음
- 본문 검사: 30/32 맞음. 어법, 문체, 분량, 강조를 어림 기준으로 잰다
- 검사 기록: 본문을 쓴 32건 가운데 30건이 check 로 성장 기록을 남겼다
- 여러 턴 흐름: 5/5 맞음
- 사용료: 에이전트가 알려 주지 않음

## 요청 하나

| 케이스 | 기대 | 에이전트가 부른 것 | 판정 | 본문 검사 | 비고 | 초 |
|---|---|---|---|---|---|---|
| report | report | `compose --kind report --audience professor` | 맞음 | 맞음 |  | 0 |
| slides | slides | `compose --kind slides --audience listener` | 맞음 | 맞음 |  | 0 |
| minutes | minutes, 독자 teammate | `compose --kind minutes --audience teammate` | 맞음 | 맞음 |  | 0 |
| email | email, 독자 professor | `compose --kind email --audience professor --set markup=plain` | 맞음 | 맞음 |  | 0 |
| resume | resume | `compose --kind resume --audience recruiter` | 맞음 | 맞음 |  | 0 |
| cover-letter | cover-letter, 700자 | `compose --kind cover-letter --audience recruiter --set markup=plain --chars 700` | 맞음 | 맞음 |  | 0 |
| portfolio | portfolio | `compose --kind portfolio --audience recruiter` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함, check 를 부르지 않음 | 0 |
| interview | interview | `compose --kind interview --audience recruiter --set length=brief --set voice=prose --set register=polite` | 맞음 | 틀림: 문서 종류의 틀 (빠짐: 꼬리 질문) | 먼저 질문해 한 번 더 재촉함, check 를 부르지 않음 | 0 |
| abstract | abstract | `compose --kind abstract --audience reviewer` | 맞음 | 맞음 |  | 0 |
| proposal | proposal | `compose --kind proposal` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 0 |
| design-doc | design-doc | `compose --kind design-doc --audience peer-dev` | 맞음 | 맞음 |  | 0 |
| pr | pr | `compose --kind pr --audience peer-dev` | 맞음 | 맞음 |  | 0 |
| postmortem | postmortem | `compose --kind postmortem --audience teammate` | 맞음 | 맞음 |  | 0 |
| spec | spec | `compose --kind spec --audience stakeholder` | 맞음 | 맞음 |  | 0 |
| biz-report | biz-report, 독자 manager | `compose --kind biz-report --audience manager` | 맞음 | 맞음 |  | 0 |
| work-report | work-report, 독자 manager | `compose --kind work-report --audience manager` | 맞음 | 맞음 |  | 0 |
| blog | blog | `compose --kind blog --audience peer-dev` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 0 |
| newsletter | newsletter | `compose --kind newsletter --audience reader` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 0 |
| sns | sns, register=haeyo, length=brief | `compose --kind sns --set register=haeyo --set length=brief --set markup=plain` | 맞음 | 맞음 |  | 0 |
| guide | guide | `compose --kind guide --audience peer-dev` | 맞음 | 맞음 |  | 0 |
| notice | notice, 독자 stakeholder | `compose --kind notice --audience stakeholder` | 맞음 | 맞음 |  | 0 |
| script | script | `compose --kind script --audience listener --set register=polite --set voice=prose --set terms=everyday --chars 6000` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 0 |
| set-register | report, register=polite | `compose --kind report --audience professor --set register=polite` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 0 |
| set-voice-length | postmortem, voice=prose, length=brief | `compose --kind postmortem --set voice=prose --set length=brief` | 맞음 | 틀림: 문서 종류의 틀 (빠짐: 타임라인) | 먼저 질문해 한 번 더 재촉함 | 0 |
| set-exposure | blog 또는 guide, exposure=team | `compose --kind blog --audience peer-dev --set exposure=team` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 0 |
| set-markup | notice, markup=plain | `compose --kind notice --audience teammate --set markup=plain --set length=brief` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 0 |
| audience-stakeholder | report, 독자 stakeholder | `compose --kind report --audience stakeholder` | 맞음 | 맞음 |  | 0 |
| folder-defaults | report, register=haeyo | `compose --kind report --audience professor` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 0 |
| revise-email | email, 독자 professor, 다듬기 | `compose --kind email --audience professor --set register=haeyo --set length=brief --set markup=plain --revise` | 맞음 | 맞음 |  | 0 |
| toast | script 또는 종류 없음 | `compose --kind script --audience listener` | 맞음 | 맞음 |  | 0 |
| no-kind | 종류 없음 | `compose` | 맞음 | 맞음 |  | 0 |
| skip-code | 부르지 않음 | `부르지 않음` | 맞음 | - |  | 0 |
| skip-question | 부르지 않음 | `부르지 않음` | 맞음 | - |  | 0 |
| no-profile | work-report | `compose --kind work-report --audience manager --set register=haeyo --set length=brief` | 맞음 | 맞음 |  | 0 |
| screen-theme | serve --detach, 화면 index | `serve --detach` | 맞음 | - |  | 0 |
| screen-setup | serve --detach, 화면 create | `serve --page create --detach` | 맞음 | - |  | 0 |

## 여러 턴 흐름

| 흐름 | 기대 | 에이전트가 부른 것 | 판정 | 비고 | 초 |
|---|---|---|---|---|---|
| flow-bootstrap | 프로필 profile.class=office, 프로필 persona.call=지수 님, 프로필 persona.docs=['work-report', 'email'] | `bootstrap --questions; bootstrap --class office --call 지수 님 --affiliation 플랫폼팀 백엔드 3년 차 --goal 보고서를 빨리 끝내는 것 --docs work-report,email --yes` | 맞음 |  | 0 |
| flow-restyle | 프로필 audiences.manager.register=haeyo | `set register haeyo --kind work-report --audience manager; set register haeyo --audience manager` | 맞음 |  | 0 |
| flow-kind | 프로필 kinds.work-report.voice=prose, 프로필에 defaults.voice 없음 | `set voice prose --kind work-report` | 맞음 |  | 0 |
| flow-here | 폴더 파일 defaults.register=plain, 프로필에 defaults.register 없음 | `set register plain --here` | 맞음 |  | 0 |
| flow-learn | 프로필 어딘가에 register=polite, 내 문체 문서, 샘플 이름과 수치 새지 않음 | `learn samples/01-weekly.md samples/02-review.md samples/03-wrapup.md samples/04-request.md; learn --guide; set register polite --audience teammate; set voice prose --audience teammate; set emphasis none --audience teammate; voice set - --samples samples/01-weekly.md samples/02-review.md samples/03-wrapup.md samples/04-request.md` | 맞음 |  | 0 |
