# AI 코딩 도구의 지침 파일에 넣는 조각

Codex 의 `AGENTS.md`, Claude Code 의 `CLAUDE.md`, Gemini CLI 의 `GEMINI.md` 에 아래를 붙이면, 그 도구가 문서를 쓸 때 테마 엔진을 부른다. `<경로>` 는 이 저장소를 받은 자리다.

```
## 문서를 쓸 때

이력서, 발표 자료, 보고서, 팀플 공유자료를 쓰기 전에
`python3 <경로>/theme.py compose --kind <resume|slides|report|teamwork>` 를 돌리고,
출력된 지침을 그 문서의 규칙으로 따른다. 독자가 정해져 있으면 `--audience` 로 넘긴다.
```
