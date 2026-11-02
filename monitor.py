import urllib.request
import ssl
import time
import json
import os
import subprocess
from datetime import datetime, timezone, timedelta

SERVICES = [
    {
        "name": "포트폴리오 & 기술 블로그",
        "url": "https://www.yangjunman.com",
        "category": "Main Platform",
        "expected": 200
    },
    {
        "name": "양준혁의 실험실 (Lab Portal)",
        "url": "https://www.yangjunman.com/lab",
        "category": "Lab & Showcase",
        "expected": 200
    },
    {
        "name": "회의록 만들기 (홈서버 AI 음성 전사·요약)",
        "url": "https://lab.yangjunman.com/minutes/",
        "category": "HomeServer AI (jammy-sub)",
        "expected": 200
    },
    {
        "name": "Windows Server AD 랩 (권한 격리 실습 포털)",
        "url": "https://lab.yangjunman.com/winlab/",
        "category": "Virtual Infra (jammy-sub)",
        "expected": 200
    },
    {
        "name": "Token Savings Benchmark (대시보드)",
        "url": "https://yangjunman.github.io/claude-code-token-savings-benchmark/web/#overview",
        "category": "OpenSource Benchmark",
        "expected": 200
    },
    {
        "name": "내 집 찾기 (Search Auction 경매 지도 검색)",
        "url": "https://yangjunman-auction.vercel.app/",
        "category": "Web Service (Vercel)",
        "expected": 200
    }
]

HISTORY_FILE = "history.json"

def check_service(service):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    start_time = time.time()
    try:
        req = urllib.request.Request(
            service["url"],
            headers={"User-Agent": "YangJunMan-HealthMonitor/1.0 (+https://github.com/YangJunMan/service-uptime-monitor)"}
        )
        with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
            latency_ms = int((time.time() - start_time) * 1000)
            is_up = resp.status < 400
            return {
                "name": service["name"],
                "url": service["url"],
                "category": service["category"],
                "status": resp.status,
                "latency_ms": latency_ms,
                "is_up": is_up,
                "error": None
            }
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        return {
            "name": service["name"],
            "url": service["url"],
            "category": service["category"],
            "status": "DOWN",
            "latency_ms": latency_ms,
            "is_up": False,
            "error": str(e)
        }

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def handle_alerts(results, history):
    # KST 기준 시간
    kst = timezone(timedelta(hours=9))
    now_kst = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S KST")

    for res in results:
        name = res["name"]
        is_up = res["is_up"]
        prev_data = history.get(name, {"fail_count": 0, "is_up": True})
        prev_up = prev_data.get("is_up", True)
        fail_count = prev_data.get("fail_count", 0)

        if not is_up:
            fail_count += 1
            print(f"[ALERT] {name} is DOWN! (Fail count: {fail_count})")
            # 5분 이상 다운 시 (연속 1회 이상 실패 시) GitHub Issue 알림 생성
            if fail_count == 1:
                title = f"[CRITICAL] Service Outage Detected: {name}"
                body = f"""### 서비스 장애 감지 알림

- **서비스명**: {name}
- **URL**: {res['url']}
- **카테고리**: {res['category']}
- **감지 시각**: {now_kst}
- **응답 상태**: `{res['status']}`
- **에러 내용**: `{res['error']}`
- **지연 시간**: {res['latency_ms']}ms

자동 헬스체크 모니터링 시스템에서 5분 주기 점검 중 서비스 이상을 감지하여 긴급 이슈를 등록합니다.
원격 서버 상태 및 Cloudflare Tunnel, Vercel 인스턴스를 확인해 주세요.
"""
                try:
                    subprocess.run(["gh", "issue", "create", "--title", title, "--body", body, "--label", "incident,bug"], check=False)
                    print(f"Created GitHub issue for {name}")
                except Exception as ex:
                    print(f"Failed to create issue via gh: {ex}")
        else:
            if not prev_up or fail_count > 0:
                print(f"[RECOVERY] {name} is back ONLINE!")
                title = f"[RECOVERED] Service Restored: {name}"
                body = f"서비스 정상 복구 확인 ({now_kst}): 지연 시간 {res['latency_ms']}ms, 상태 {res['status']}"
                try:
                    subprocess.run(["gh", "issue", "create", "--title", title, "--body", body, "--label", "resolved"], check=False)
                except Exception:
                    pass
            fail_count = 0

        samples = list(prev_data.get("samples", []))
        if not samples and "last_check" in prev_data:
            samples.append({key: prev_data.get(key) for key in ("is_up", "status", "latency_ms", "last_check")})
        samples.append({"is_up": is_up, "status": res["status"], "latency_ms": res["latency_ms"], "last_check": now_kst})
        history[name] = {
            "url": res["url"],
            "category": res["category"],
            "samples": samples[-288:],
            "is_up": is_up,
            "status": res["status"],
            "latency_ms": res["latency_ms"],
            "fail_count": fail_count,
            "last_check": now_kst
        }

    return history

def generate_readme(results, history):
    last_check = next((history.get(res["name"], {}).get("last_check") for res in results
                       if history.get(res["name"], {}).get("last_check")), "확인되지 않음")
    rows = []
    for res in results:
        status = "정상" if res["is_up"] else "장애"
        rows.append(f"| **{res['name']}** | [{res['url']}]({res['url']}) | {status} | `{res['status']}` | {res['latency_ms']} ms |")

    readme_content = f"""# 서비스 가동 상태 모니터

## [실시간 대시보드 열기](https://yangjunman.github.io/service-uptime-monitor/)

서비스 가동 상태와 방문자 브라우저에서 측정한 핑, 홈서버 `jammy-sub`의 CPU, RAM, VRAM 사용량을 확인할 수 있습니다.

## 서비스 가동 현황

마지막 자동 점검: {last_check} · GitHub Actions에서 5분마다 점검

| 서비스명 | 대상 주소 | 상태 | HTTP 상태 | 응답 시간 |
| :--- | :--- | :---: | :---: | :---: |
{chr(10).join(rows)}

## 모니터링 방식

- GitHub Actions가 서비스에 HTTP 요청을 보내 상태와 응답 시간을 기록합니다.
- 최초 장애 감지와 복구 시 GitHub Issue 생성을 시도합니다.
- `history.json`에는 서비스별 최근 점검 결과를 최대 288개 저장합니다. 기존 기록은 누적되기 시작한 시점부터 확인할 수 있습니다.
- 브라우저 핑은 방문자의 네트워크에서 측정하며, 자동 점검 결과와 다를 수 있습니다.

## 바로가기

- [이력서](https://www.yangjunman.com/resume)
- [실험실](https://www.yangjunman.com/lab)
- [기술 블로그](https://www.yangjunman.com/blog)
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("Generated README.md successfully!")

if __name__ == "__main__":
    print(f"[{datetime.now().isoformat()}] Starting health checks...")
    results = [check_service(s) for s in SERVICES]
    history = load_history()
    updated_history = handle_alerts(results, history)
    save_history(updated_history)
    generate_readme(results, updated_history)
    print("Health checks finished.")
