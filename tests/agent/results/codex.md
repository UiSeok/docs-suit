# 동작 테스트: codex

- 날짜: 2026-10-28
- 에이전트: codex-cli 0.164.0
- 스킬 자리: 임시 작업 폴더
- SKILL.md 지문: cb058544
- 모델: 알 수 없음
- 요금제: free
- 고르기: 36/36 맞음
- 본문 검사: 30/32 맞음. 어법, 문체, 분량, 강조를 어림 기준으로 잰다
- 검사 기록: 본문을 쓴 32건 가운데 27건이 check 로 성장 기록을 남겼다
- 여러 턴 흐름: 3/3 맞음
- 사용료: 에이전트가 알려 주지 않음

## 요청 하나

| 케이스 | 기대 | 에이전트가 부른 것 | 판정 | 본문 검사 | 비고 | 초 |
|---|---|---|---|---|---|---|
| report | report | `compose --kind report --audience professor` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 36 |
| slides | slides | `compose --kind slides --audience listener --set visual-deck=minimal --set register=polite` | 맞음 | 맞음 |  | 32 |
| minutes | minutes, 독자 teammate | `compose --kind minutes --audience teammate` | 맞음 | 맞음 |  | 12 |
| email | email, 독자 professor | `compose --kind email --audience professor --set markup=plain` | 맞음 | 맞음 |  | 18 |
| resume | resume | `compose --kind resume --audience recruiter` | 맞음 | 맞음 |  | 19 |
| cover-letter | cover-letter, 700자 | `compose --kind cover-letter --audience recruiter --set markup=plain --chars 700` | 맞음 | 맞음 |  | 17 |
| portfolio | portfolio | `compose --kind portfolio --audience recruiter` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 23 |
| interview | interview | `compose --kind interview --audience recruiter` | 맞음 | 맞음 |  | 20 |
| abstract | abstract | `compose --kind abstract --audience reviewer` | 맞음 | 맞음 | check 를 부르지 않음 | 14 |
| proposal | proposal | `compose --kind proposal --audience professor; compose --kind proposal --audience professor --set length=full` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 91 |
| design-doc | design-doc | `compose --kind design-doc --audience peer-dev` | 맞음 | 맞음 |  | 24 |
| pr | pr | `compose --kind pr --audience reviewer` | 맞음 | 맞음 |  | 15 |
| postmortem | postmortem | `compose --kind postmortem --audience teammate` | 맞음 | 맞음 |  | 19 |
| spec | spec | `compose --kind spec --set length=full` | 맞음 | 맞음 |  | 32 |
| biz-report | biz-report, 독자 manager | `compose --kind biz-report --audience manager; compose --kind biz-report --audience manager` | 맞음 | 틀림: 문서 종류의 틀 (빠짐: 요약) | check 를 부르지 않음 | 16 |
| work-report | work-report, 독자 manager | `compose --kind work-report --audience manager` | 맞음 | 맞음 |  | 20 |
| blog | blog | `compose --kind blog --audience reader` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 33 |
| newsletter | newsletter | `compose --kind newsletter --audience reader` | 맞음 | 맞음 |  | 23 |
| sns | sns, register=haeyo, length=brief | `compose --kind sns --set register=haeyo --set length=brief --chars 100` | 맞음 | 맞음 |  | 13 |
| guide | guide | `compose --kind guide --audience teammate,peer-dev` | 맞음 | 맞음 |  | 17 |
| notice | notice, 독자 stakeholder | `compose --kind notice --audience stakeholder` | 맞음 | 맞음 |  | 19 |
| script | script | `compose --kind script --audience listener --set register=polite --set terms=everyday --chars 3000` | 맞음 | 맞음 | check 를 부르지 않음 | 18 |
| set-register | report, register=polite | `compose --kind report --audience professor --set register=polite --set exposure=submit --set skeleton=imrad; compose --kind report --audience professor --set register=polite --set exposure=submit --set skeleton=imrad` | 맞음 | 맞음 | check 를 부르지 않음 | 19 |
| set-voice-length | postmortem, voice=prose, length=brief | `compose --kind postmortem --audience teammate --set voice=prose --set length=brief` | 맞음 | 틀림: 문서 종류의 틀 (빠짐: 타임라인) | check 를 부르지 않음 | 14 |
| set-exposure | blog 또는 guide, exposure=team | `compose --kind blog --audience peer-dev --set exposure=team` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 31 |
| set-markup | notice, markup=plain | `compose --kind notice --audience teammate --set markup=plain --set length=brief` | 맞음 | 맞음 |  | 17 |
| audience-stakeholder | report, 독자 stakeholder | `compose --kind report --audience stakeholder --set length=brief` | 맞음 | 맞음 |  | 22 |
| folder-defaults | report, register=haeyo | `compose --kind report --audience professor` | 맞음 | 맞음 | 먼저 질문해 한 번 더 재촉함 | 28 |
| revise-email | email, 독자 professor, 다듬기 | `compose --kind email --audience professor --set markup=plain --revise` | 맞음 | 맞음 |  | 10 |
| toast | script 또는 종류 없음 | `compose --kind script --audience listener` | 맞음 | 맞음 |  | 15 |
| no-kind | 종류 없음 | `compose` | 맞음 | 맞음 |  | 18 |
| skip-code | 부르지 않음 | `부르지 않음` | 맞음 | - |  | 5 |
| skip-question | 부르지 않음 | `부르지 않음` | 맞음 | - |  | 3 |
| no-profile | work-report | `compose --kind work-report --audience manager --set register=haeyo --set length=brief` | 맞음 | 맞음 |  | 12 |
| screen-theme | serve --detach, 화면 index | `serve --detach` | 맞음 | - |  | 10 |
| screen-setup | serve --detach, 화면 create | `serve --page create --detach` | 맞음 | - |  | 10 |

## 여러 턴 흐름

| 흐름 | 기대 | 에이전트가 부른 것 | 판정 | 비고 | 초 |
|---|---|---|---|---|---|
| flow-bootstrap | 프로필 profile.class=office, 프로필 persona.call=지수 님, 프로필 persona.docs=['work-report', 'email'] | `bootstrap --questions; bootstrap --class office --call 지수 님 --affiliation 플랫폼팀 백엔드 3년 차 --goal 보고서를 빨리 끝내기 --docs work-report,email --facts  --dislikes  --yes` | 맞음 |  | 30 |
| flow-restyle | 프로필 audiences.manager.register=haeyo | `set register haeyo --audience manager` | 맞음 |  | 25 |
| flow-here | 폴더 파일 defaults.register=plain, 프로필에 defaults.register 없음 | `set register plain --here` | 맞음 |  | 9 |
