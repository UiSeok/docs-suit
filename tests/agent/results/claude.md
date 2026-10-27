# 동작 테스트: claude

- 날짜: 2026-10-27
- 에이전트: 2.1.311 (Claude Code)
- SKILL.md 지문: 84114856
- 모델: claude-opus-5-5
- 맞음: 27/27
- 사용료: 3.65달러

| 케이스 | 기대 | 에이전트가 부른 것 | 판정 | 비고 | 초 |
|---|---|---|---|---|---|
| report | report | `compose --kind report --audience professor` | 맞음 |  | 33 |
| slides | slides | `compose --kind slides --audience listener` | 맞음 |  | 27 |
| minutes | minutes, 독자 teammate | `compose --kind minutes --audience teammate` | 맞음 |  | 32 |
| email | email, 독자 professor | `compose --kind email --audience professor` | 맞음 |  | 472 |
| resume | resume | `compose --kind resume --audience recruiter` | 맞음 |  | 49 |
| cover-letter | cover-letter, 700자 | `compose --kind cover-letter --audience recruiter --chars 700` | 맞음 | 거절된 도구 1건 | 46 |
| portfolio | portfolio | `compose --kind portfolio --audience recruiter` | 맞음 |  | 29 |
| interview | interview | `compose --kind interview --audience recruiter` | 맞음 |  | 44 |
| abstract | abstract | `compose --kind abstract --audience reviewer` | 맞음 |  | 32 |
| proposal | proposal | `compose --kind proposal` | 맞음 |  | 26 |
| design-doc | design-doc | `compose --kind design-doc --audience peer-dev` | 맞음 |  | 32 |
| pr | pr | `compose --kind pr --audience peer-dev` | 맞음 |  | 33 |
| postmortem | postmortem | `compose --kind postmortem` | 맞음 | 거절된 도구 1건 | 67 |
| spec | spec | `compose --kind spec` | 맞음 | 거절된 도구 1건 | 392 |
| work-report | work-report, 독자 manager | `compose --kind work-report --audience manager` | 맞음 |  | 34 |
| blog | blog | `compose --kind blog --audience reader,peer-dev` | 맞음 |  | 291 |
| newsletter | newsletter | `compose --kind newsletter --audience reader` | 맞음 |  | 333 |
| sns | sns, register=haeyo, length=brief | `compose --kind sns --audience reader --set register=haeyo --set length=brief` | 맞음 |  | 22 |
| set-register | report, register=polite | `compose --kind report --audience professor --set register=polite` | 맞음 |  | 30 |
| set-voice-length | postmortem, voice=prose, length=brief | `compose --kind postmortem --set voice=prose --set length=brief` | 맞음 |  | 27 |
| set-exposure | blog, exposure=team | `compose --kind blog --audience peer-dev` | 맞음 |  | 28 |
| audience-stakeholder | report, 독자 stakeholder | `compose --kind report --audience stakeholder` | 맞음 |  | 26 |
| ambiguous-notice | email 또는 minutes, 독자 stakeholder | `compose --kind email --audience stakeholder` | 맞음 |  | 33 |
| no-kind | 종류 없음 | `compose --audience listener --set register=polite --set voice=prose` | 맞음 |  | 40 |
| skip-code | 부르지 않음 | `부르지 않음` | 맞음 |  | 12 |
| skip-question | 부르지 않음 | `부르지 않음` | 맞음 |  | 7 |
| no-profile | work-report | `compose --kind work-report --audience manager` | 맞음 |  | 26 |
