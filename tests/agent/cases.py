"""동작 테스트 케이스. tests/agent/run.py 가 읽는다.

expect 가 compose 이면 에이전트가 suit.py compose 를 불러야 한다. kind 는 기대하는 문서 종류이고, 여럿을 허용하면
목록으로, 종류 없이 조립해야 하면 빈 문자열로 쓴다. want 는 조립 결과에서 이 값이어야 하는 축이다. audience 는 실제로
쓰인 독자에 들어 있어야 하는 키다. expect 가 skip 이면 suit.py 를 부르지 않아야 한다. profile 이 False 이면 프로필 없이
시작한다. 어느 케이스든 사용자의 답 없이 bootstrap 으로 프로필을 저장하면 틀린다.
"""

# 시험 프로필. bootstrap 이 만드는 것과 같은 꼴이다.
PROFILE = {
    "profile": {"class": "office", "lang": "ko"},
    "persona": {"call": "지수 님", "affiliation": "플랫폼팀 백엔드 3년 차", "goal": "보고와 공유 문서를 빨리 끝낸다",
                "dislikes": "과장된 마케팅 말투", "docs": ["work-report", "email", "minutes"]},
}

CASES = [
    # 문서 종류마다 하나
    {"id": "report", "kind": "report",
     "ask": "환경공학 수업 기말 레포트 써 줘. 주제는 우리 동네 정류장 대기 시간 조사고, 평일 아침 사흘 동안 재 봤어."},
    {"id": "slides", "kind": "slides",
     "ask": "다음 주 동아리 발표 자료 만들어 줘. 정류장 대기 시간을 조사한 결과를 10분 동안 발표해."},
    {"id": "minutes", "kind": "minutes", "audience": "teammate",
     "ask": "오늘 회의 내용을 팀 공유용으로 정리해 줘. 다음 스프린트는 결제 개선에 집중하고, 캐시는 지수, 모니터링은 민호가 맡고, 금요일까지 설계 초안을 낸다."},
    {"id": "email", "kind": "email", "audience": "professor",
     "ask": "다음 주 화요일에 교수님 면담이 가능한지 여쭤보는 메일 써 줘. 졸업 논문 주제를 상담하려고 해."},
    {"id": "resume", "kind": "resume",
     "ask": "백엔드 개발자 신입 지원용 이력서 써 줘. 학교 프로젝트로 버스 도착 알림 앱을 만들었고 Spring 이랑 MySQL 을 썼어."},
    {"id": "cover-letter", "kind": "cover-letter", "chars": 700,
     "ask": "데이터 분석 직무 자기소개서의 지원 동기 항목 써 줘. 700자 이내로."},
    {"id": "portfolio", "kind": "portfolio",
     "ask": "디자인 포트폴리오에 넣을 프로젝트 소개 글 써 줘. 정류장 안내판을 다시 디자인한 프로젝트야."},
    {"id": "interview", "kind": "interview",
     "ask": "면접에서 가장 힘들었던 협업 경험을 물으면 할 답변 정리해 줘. 조별 과제에서 연락이 끊긴 조원이 있었어."},
    {"id": "abstract", "kind": "abstract",
     "ask": "학회에 낼 논문 초록 써 줘. 버스 정류장 대기 시간을 GPS 데이터로 예측하는 모델이고, 기존 방법보다 오차가 20% 줄었어."},
    {"id": "proposal", "kind": "proposal",
     "ask": "연구계획서 써 줘. 정류장 대기 시간이 대중교통 이용 만족도에 주는 영향을 설문으로 조사하려고 해."},
    {"id": "design-doc", "kind": "design-doc",
     "ask": "알림 서비스 재시도 큐 설계 문서 써 줘. 지금은 발송에 실패하면 그냥 버리는데, 지수 백오프로 세 번까지 다시 보내려고 해."},
    {"id": "pr", "kind": "pr",
     "ask": "이 PR 설명 써 줘. 정산 배치가 실패하면 세 번까지 다시 시도하게 바꿨고 테스트를 두 개 더했어."},
    {"id": "postmortem", "kind": "postmortem",
     "ask": "어제 배포 후 30분 동안 로그인이 실패했던 건 회고 문서로 정리해 줘. 원인은 새 설정값 누락이었고 롤백으로 복구했어."},
    {"id": "spec", "kind": "spec",
     "ask": "정류장 도착 알림 기능 기획서 써 줘. 버스가 3분 안에 도착하면 푸시를 보내는 기능이야."},
    {"id": "work-report", "kind": "work-report", "audience": "manager",
     "ask": "팀장님께 올릴 이번 주 업무 보고 써 줘. 결제 API 가 느렸던 원인이 DB 커넥션 풀 고갈이었고, 풀 크기를 조정하고 캐시를 붙여서 p95 가 800ms 에서 200ms 로 줄었어."},
    {"id": "blog", "kind": "blog",
     "ask": "기술 블로그에 올릴 글 써 줘. 서비스에 Redis 캐시를 붙였다가 캐시 정합성 문제로 고생한 경험담이야."},
    {"id": "newsletter", "kind": "newsletter",
     "ask": "이번 달 구독자에게 보낼 뉴스레터 써 줘. 동네 버스 노선이 바뀐 소식이랑 정류장 대기 시간 조사 결과를 담을 거야."},
    {"id": "sns", "kind": "sns", "want": {"register": "haeyo", "length": "brief"},
     "ask": "주말에 다녀온 카페 인스타 후기 써 줘. 해요체로 짧게."},

    # 사용자가 축을 말한 요청
    {"id": "set-register", "kind": "report", "want": {"register": "polite"},
     "ask": "교수님께 낼 정류장 대기 시간 조사 보고서 써 줘. 이번에는 합쇼체로 써 줘."},
    {"id": "set-voice-length", "kind": "postmortem", "want": {"voice": "prose", "length": "brief"},
     "ask": "어제 캐시 서버가 30분 멈춘 건 회고 문서로 써 줘. 개조식 말고 줄글로, 짧게."},
    {"id": "set-exposure", "kind": "blog", "want": {"exposure": "team"},
     "ask": "사내 위키에만 올릴 기술 글 써 줘. 밖에는 공개하지 않아. 주제는 로그 수집 파이프라인을 정리한 이야기야."},
    {"id": "audience-stakeholder", "kind": "report", "audience": "stakeholder",
     "ask": "이번 분기 실험 결과 보고서를 다른 팀 사람들이 읽을 수 있게 써 줘. 추천 알고리즘을 바꿨더니 클릭률이 3% 올랐어."},

    # 경계
    {"id": "ambiguous-notice", "kind": ["email", "minutes"], "audience": "stakeholder",
     "ask": "다른 팀에 다음 주 API 변경을 알리는 공지 써 줘. 응답 필드 하나의 이름이 바뀌어."},
    {"id": "no-kind", "kind": "",
     "ask": "친구 결혼식 축사 써 줘. 대학 동아리에서 만난 친구야."},
    {"id": "skip-code", "expect": "skip",
     "ask": "이 정규식이 왜 이메일 주소를 못 잡는지 설명해 줘: ^[a-z]+@[a-z]+$"},
    {"id": "skip-question", "expect": "skip",
     "ask": "정류장 대기 시간을 영어로 뭐라고 해?"},
    {"id": "no-profile", "kind": "work-report", "profile": False,
     "ask": "팀장님께 올릴 주간 업무 보고 써 줘. 이번 주에는 로그인 오류를 고쳤어."},
]
