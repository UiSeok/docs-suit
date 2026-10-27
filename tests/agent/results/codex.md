# 동작 테스트: codex

- 날짜: 2026-10-27
- 에이전트: codex-cli 0.164.0
- 모델: 알 수 없음
- 요금제: free
- 맞음: 26/27
- 사용료: 에이전트가 알려 주지 않음

| 케이스 | 기대 | 에이전트가 부른 것 | 판정 | 비고 | 초 |
|---|---|---|---|---|---|
| report | report | `compose --kind report --audience professor` | 맞음 |  | 43 |
| slides | slides | `compose --kind slides --audience listener` | 맞음 |  | 55 |
| minutes | minutes, 독자 teammate | `compose --kind minutes --audience teammate` | 맞음 |  | 9 |
| email | email, 독자 professor | `compose --kind email --audience professor` | 맞음 |  | 13 |
| resume | resume | `compose --kind resume --audience recruiter` | 맞음 |  | 26 |
| cover-letter | cover-letter, 700자 | `compose --kind cover-letter --audience recruiter --chars 700` | 맞음 |  | 18 |
| portfolio | portfolio | `compose --kind portfolio --audience recruiter` | 맞음 |  | 16 |
| interview | interview | `compose --kind interview --audience recruiter` | 맞음 |  | 17 |
| abstract | abstract | `compose --kind abstract --audience reviewer` | 맞음 |  | 15 |
| proposal | proposal | `compose --kind proposal --audience professor` | 맞음 |  | 51 |
| design-doc | design-doc | `compose --kind design-doc --audience peer-dev` | 맞음 |  | 36 |
| pr | pr | `compose --kind pr --audience reviewer` | 맞음 |  | 18 |
| postmortem | postmortem | `compose --kind postmortem --audience teammate` | 맞음 |  | 70 |
| spec | spec | `compose --kind spec` | 맞음 |  | 37 |
| work-report | work-report, 독자 manager | `compose --kind work-report --audience manager` | 맞음 |  | 18 |
| blog | blog | `compose --kind blog --audience peer-dev` | 맞음 |  | 31 |
| newsletter | newsletter | `compose --kind newsletter --audience reader` | 맞음 |  | 15 |
| sns | sns, register=haeyo, length=brief | `compose --kind sns --set 어법=해요체 --chars 100; compose --kind sns --chars 100` | 맞음 |  | 42 |
| set-register | report, register=polite | `compose --kind report --audience professor --set register=합쇼체; compose --kind report --audience professor --set register=polite --set exposure=submit` | 맞음 |  | 46 |
| set-voice-length | postmortem, voice=prose, length=brief | `compose --kind postmortem --set style=prose --chars 400; compose --kind postmortem --chars 400` | 틀림: voice 가 bullet 이다, length 가 full 이다 |  | 31 |
| set-exposure | blog, exposure=team | `compose --kind blog --audience peer-dev --set 공개범위=사내위키; compose --kind blog --audience peer-dev --set exposure=team` | 맞음 |  | 37 |
| audience-stakeholder | report, 독자 stakeholder | `compose --kind report --audience stakeholder` | 맞음 |  | 35 |
| ambiguous-notice | email 또는 minutes, 독자 stakeholder | `compose --kind email --audience stakeholder` | 맞음 |  | 57 |
| no-kind | 종류 없음 | `compose` | 맞음 |  | 29 |
| skip-code | 부르지 않음 | `부르지 않음` | 맞음 |  | 14 |
| skip-question | 부르지 않음 | `부르지 않음` | 맞음 |  | 4 |
| no-profile | work-report | `compose --kind work-report --audience manager` | 맞음 |  | 12 |
