#!/usr/bin/env python3
"""issue-key.py: docs-suit 승급 키를 만든다. 저장소 관리자만 쓴다.

3차와 4차 전직은 이 저장소에 기여하고 받은 승급 키가 있어야 오른다. 관리자는 기여가 머지되면 키를 만들어 PR 댓글로
주고, 사용자는 `suit.py promote <키>` 로 넣는다. 키는 내용(GitHub 아이디, 차수, 기여 링크)과 그 서명이다.
개인 키는 저장소 밖 ~/.config/docs-suit-admin/promote-key.pem 에 두고, 엔진 suit.py 의 PROMOTE_KEYS 에는
공개 키 값만 넣는다. 서명은 openssl 로 하고, 엔진은 표준 라이브러리로 확인한다.

  python3 tools/issue-key.py init                         개인 키를 만들고 PROMOTE_KEYS 에 넣을 공개 키 값을 보인다
  python3 tools/issue-key.py public                       지금 개인 키의 공개 키 값을 보인다
  python3 tools/issue-key.py issue --who <GitHub 아이디> --tier 3 --ref "PR #12"
"""
import argparse
import base64
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ADMIN = Path(os.path.expanduser(os.environ.get("DOCS_SUIT_ADMIN", "~/.config/docs-suit-admin")))
KEY = ADMIN / "promote-key.pem"
KID = "dodokim-2026"


def b64(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def engine():
    spec = importlib.util.spec_from_file_location("suit", ROOT / "suit.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def modulus():
    out = subprocess.run(["openssl", "rsa", "-in", str(KEY), "-noout", "-modulus"],
                         capture_output=True, text=True, check=True).stdout
    return out.strip().split("=", 1)[1].lower()


def public():
    n = modulus()
    print(f'# suit.py 의 PROMOTE_KEYS 에 넣는다. kid 는 {KID}')
    print(f'"{KID}": (int(')
    for i in range(0, len(n), 96):
        print(f'    "{n[i:i + 96]}"')
    print("    , 16), 65537),")
    return 0


def init():
    if KEY.exists():
        print(f"개인 키가 이미 있다: {KEY}. 새로 만들면 지금까지 낸 키를 엔진이 확인하지 못한다", file=sys.stderr)
        return 1
    ADMIN.mkdir(parents=True, exist_ok=True)
    os.chmod(ADMIN, 0o700)
    subprocess.run(["openssl", "genpkey", "-algorithm", "RSA", "-pkeyopt", "rsa_keygen_bits:2048", "-out", str(KEY)],
                   check=True, capture_output=True)
    os.chmod(KEY, 0o600)
    print(f"개인 키를 만들었다: {KEY}. 잃어버리면 새 키를 만들어야 하니 비밀번호 관리자에 따로 남긴다", file=sys.stderr)
    return public()


def issue(who, tier, ref):
    if not KEY.exists():
        print(f"개인 키가 없다: {KEY}. 먼저 init 을 돌린다", file=sys.stderr)
        return 1
    payload = {"v": 1, "kid": KID, "who": who.lstrip("@"), "tier": tier, "ref": ref, "at": date.today().isoformat()}
    body = b64(json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    with tempfile.NamedTemporaryFile() as f:
        f.write(body.encode("ascii"))
        f.flush()
        sig = subprocess.run(["openssl", "dgst", "-sha256", "-sign", str(KEY), f.name],
                             capture_output=True, check=True).stdout
    key = f"dsk1.{body}.{b64(sig)}"
    if engine().read_promote_key(key) != payload:
        print("엔진이 이 키를 확인하지 못한다. suit.py 의 PROMOTE_KEYS 가 이 개인 키의 공개 키인지 본다", file=sys.stderr)
        return 1
    print(key)
    print(f"\n{tier}차 승급 키다. PR 댓글로 주고, 받은 사람은 `python3 suit.py promote <키>` 로 넣는다", file=sys.stderr)
    return 0


def main():
    ap = argparse.ArgumentParser(description="docs-suit 승급 키 발급")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    sub.add_parser("public")
    i = sub.add_parser("issue")
    i.add_argument("--who", required=True, help="기여한 사람의 GitHub 아이디")
    i.add_argument("--tier", type=int, required=True, choices=(3, 4), help="3 은 기여 하나, 4 는 테마 조합 기여")
    i.add_argument("--ref", required=True, help='기여 링크. 예) "PR #12"')
    a = ap.parse_args()
    if a.cmd == "init":
        return init()
    if a.cmd == "public":
        return public()
    return issue(a.who, a.tier, a.ref)


if __name__ == "__main__":
    sys.exit(main())
