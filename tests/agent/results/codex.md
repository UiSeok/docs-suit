# 동작 테스트: codex

- 날짜: 2026-10-27
- 에이전트: codex-cli 0.164.0
- SKILL.md 지문: 84114856
- 모델: 알 수 없음
- 요금제: free
- 맞음: 25/25 (재지 못한 2건 제외)
- 사용료: 에이전트가 알려 주지 않음

| 케이스 | 기대 | 에이전트가 부른 것 | 판정 | 비고 | 초 |
|---|---|---|---|---|---|
| report | report | `compose --kind report --audience professor` | 맞음 |  | 0 |
| slides | slides | `compose --kind slides --audience listener --set voice=bullet --set register=plain --set visual-deck=minimal` | 맞음 |  | 0 |
| minutes | minutes, 독자 teammate | `compose --kind minutes --audience teammate` | 맞음 |  | 0 |
| email | email, 독자 professor | `compose --kind email --audience professor` | 맞음 |  | 0 |
| resume | resume | `compose --kind resume --audience recruiter` | 맞음 |  | 0 |
| cover-letter | cover-letter, 700자 | `compose --kind cover-letter --audience recruiter --set voice=prose --set register=polite --set length=brief --chars 700` | 맞음 |  | 0 |
| portfolio | portfolio | `compose --kind portfolio --audience recruiter` | 맞음 |  | 0 |
| interview | interview | `compose --kind interview --audience recruiter` | 맞음 |  | 0 |
| abstract | abstract | `compose --kind abstract --audience reviewer` | 맞음 |  | 0 |
| proposal | proposal | `compose --kind proposal --set exposure=submit --set length=full` | 맞음 |  | 0 |
| design-doc | design-doc | `compose --kind design-doc --audience peer-dev` | 맞음 |  | 0 |
| pr | pr | `compose --kind pr --audience peer-dev` | 맞음 |  | 0 |
| postmortem | postmortem | `compose --kind postmortem --audience teammate --set exposure=team --set length=brief` | 맞음 |  | 0 |
| spec | spec | `compose --kind spec` | 맞음 |  | 0 |
| work-report | work-report, 독자 manager | `compose --kind work-report --audience manager` | 맞음 |  | 0 |
| blog | blog | `compose --kind blog --audience peer-dev` | 맞음 |  | 0 |
| newsletter | newsletter | `부르지 않음` | 재지 못함: 연결 실패 |  | 0 |
| sns | sns, register=haeyo, length=brief | `부르지 않음` | 재지 못함: 연결 실패 |  | 0 |
| set-register | report, register=polite | `compose --kind report --audience professor --set exposure=submit --set skeleton=imrad --set voice=prose --set register=polite --set terms=explained --set length=page --set sources=none --set ai-disclosure=none --set diagram=table --set emphasis=bold --chars 3000; compose --kind report --audience professor --set exposure=submit --set skeleton=imrad --set voice=prose --set register=polite --set terms=explained --set length=page --set sources=footnote --set ai-disclosure=none --set diagram=table --set emphasis=bold --chars 3000` | 맞음 |  | 0 |
| set-voice-length | postmortem, voice=prose, length=brief | `compose --kind postmortem --audience teammate --set voice=prose --set length=brief --chars 400` | 맞음 |  | 0 |
| set-exposure | blog, exposure=team | `compose --kind blog --audience peer-dev --set exposure=team` | 맞음 |  | 0 |
| audience-stakeholder | report, 독자 stakeholder | `compose --kind report --audience stakeholder,teammate --chars 1; compose --kind report --audience stakeholder,teammate` | 맞음 |  | 0 |
| ambiguous-notice | email 또는 minutes, 독자 stakeholder | `compose --kind email --audience stakeholder,peer-dev` | 맞음 |  | 0 |
| no-kind | 종류 없음 | `compose --audience listener --chars 900` | 맞음 |  | 0 |
| skip-code | 부르지 않음 | `부르지 않음` | 맞음 |  | 0 |
| skip-question | 부르지 않음 | `부르지 않음` | 맞음 |  | 0 |
| no-profile | work-report | `compose --kind work-report --audience manager` | 맞음 |  | 0 |
