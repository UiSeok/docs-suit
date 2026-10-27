# 동작 테스트: antigravity

- 날짜: 2026-10-27
- 에이전트: 1.4.8
- 모델: gemini-3.8-flash-high
- 맞음: 25/26 (사용 한도로 재지 못한 1건 제외)
- 사용료: 에이전트가 알려 주지 않음
- 한계: 한 번 실행 모드는 허용 규칙 밖의 명령을 만나면 답 없이 끝난다. 이 표는 종류와 축을 고르는 단계까지 잰다.

| 케이스 | 기대 | 에이전트가 부른 것 | 판정 | 비고 | 초 |
|---|---|---|---|---|---|
| report | report | `compose --kind report --audience professor` | 맞음 | 거절된 도구 1건 | 39 |
| slides | slides | `compose --kind slides --audience listener` | 맞음 | 거절된 도구 1건 | 25 |
| minutes | minutes, 독자 teammate | `compose --kind minutes --audience teammate` | 맞음 | 거절된 도구 1건 | 45 |
| email | email, 독자 professor | `compose --kind email --audience professor` | 맞음 | 거절된 도구 1건 | 26 |
| resume | resume | `compose --kind resume --audience recruiter` | 맞음 | 거절된 도구 1건 | 45 |
| cover-letter | cover-letter, 700자 | `compose --kind cover-letter --audience recruiter --chars 700` | 맞음 | 거절된 도구 1건 | 31 |
| portfolio | portfolio | `compose --kind portfolio --audience recruiter` | 맞음 | 거절된 도구 1건 | 26 |
| interview | interview | `compose --kind interview --audience recruiter` | 맞음 | 거절된 도구 1건 | 22 |
| abstract | abstract | `compose --kind abstract --audience reviewer` | 맞음 | 거절된 도구 1건 | 27 |
| proposal | proposal | `compose --kind proposal` | 맞음 | 거절된 도구 1건 | 20 |
| design-doc | design-doc | `compose --kind design-doc` | 맞음 | 거절된 도구 1건 | 20 |
| pr | pr | `compose --kind pr` | 맞음 | 거절된 도구 1건 | 22 |
| postmortem | postmortem | `compose --kind postmortem` | 맞음 | 거절된 도구 1건 | 26 |
| spec | spec | `compose --kind spec` | 맞음 | 거절된 도구 1건 | 33 |
| work-report | work-report, 독자 manager | `compose --kind work-report --audience manager` | 맞음 |  | 67 |
| blog | blog | `compose --kind blog --audience peer-dev; compose --kind blog --audience reader; compose --kind blog` | 맞음 | 거절된 도구 1건 | 39 |
| newsletter | newsletter | `compose --kind newsletter --audience reader` | 맞음 | 거절된 도구 1건 | 32 |
| sns | sns, register=haeyo, length=brief | `compose --kind sns --audience reader --set register=haeyo --set length=brief` | 맞음 | 거절된 도구 1건 | 30 |
| set-register | report, register=polite | `compose --kind report --audience professor --set register=polite` | 맞음 | 거절된 도구 1건 | 25 |
| set-voice-length | postmortem, voice=prose, length=brief | `compose --kind postmortem --set voice=prose --set length=brief` | 맞음 | 거절된 도구 1건 | 30 |
| set-exposure | blog, exposure=team | `compose --kind blog --set exposure=team --audience peer-dev; compose --kind blog --set exposure=team` | 틀림: exposure 가 public 이다 | 거절된 도구 1건 | 24 |
| audience-stakeholder | report, 독자 stakeholder | `compose --kind report --audience stakeholder` | 맞음 |  | 40 |
| ambiguous-notice | email 또는 minutes, 독자 stakeholder | `compose --kind email --audience stakeholder` | 맞음 | 거절된 도구 1건 | 32 |
| no-kind | 종류 없음 | `compose --audience listener; compose --audience listener --set voice=prose --set skeleton=chrono --set register=polite` | 맞음 |  | 32 |
| skip-code | 부르지 않음 | `부르지 않음` | 맞음 |  | 17 |
| skip-question | 부르지 않음 | `부르지 않음` | 맞음 |  | 9 |
| no-profile | work-report | `부르지 않음` | 재지 못함: 사용 한도 |  | 5 |
