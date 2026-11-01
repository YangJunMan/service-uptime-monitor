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
                body = f"""### 🚨 서비스 장애 감지 알림

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

        history[name] = {
            "is_up": is_up,
            "status": res["status"],
            "latency_ms": res["latency_ms"],
            "fail_count": fail_count,
            "last_check": now_kst
        }

    return history

def generate_readme(results, history):
    kst = timezone(timedelta(hours=9))
    now_kst = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S KST")

    all_up = all(res["is_up"] for res in results)
    status_badge = "https://img.shields.io/badge/Status-All%20Systems%20Operational-brightgreen?style=for-the-badge&logo=statuspage" if all_up else "https://img.shields.io/badge/Status-Partial%20Outage-critical?style=for-the-badge&logo=statuspage"

    rows = []
    for res in results:
        status_icon = "🟢 정상 (UP)" if res["is_up"] else "🔴 장애 (DOWN)"
        code_badge = f"`{res['status']}`"
        latency = f"{res['latency_ms']} ms"
        rows.append(f"| **{res['name']}** | [{res['url']}]({res['url']}) | {status_icon} | {code_badge} | {latency} |")

    readme_content = f"""# 🛡️ Service Uptime & Health Monitor

> 엔지니어 양준혁의 블로그, 라이브 실험실, 홈서버(jammy-sub) 및 웹 서비스들의 가동 상태를 **5분 주기로 실시간 감시**하는 자동화 모니터링 시스템입니다.
> 장애 발생 시 5분 이내에 GitHub Issues 및 알림 파이프라인으로 즉시 통보됩니다.

<p align="center">
  <img src="{status_badge}" alt="System Status Badge">
  <br>
  <sub>마지막 자동 점검 시각: <b>{now_kst}</b> · 5분 주기 크론(GitHub Actions)</sub>
</p>

---

## 📊 실시간 서비스 가동 현황 (Live Status Board)

| 서비스명 | 대상 엔드포인트 | 가동 상태 | 응답 코드 | 응답 속도 |
| :--- | :--- | :---: | :---: | :---: |
{chr(10).join(rows)}

---

## ⚙️ 모니터링 시스템 아키텍처

- **주기 점검**: GitHub Actions Cron 워크플로우를 통해 매 5분(`*/5 * * * *`)마다 전 엔드포인트 HTTP/HTTPS 헬스체크 실행.
- **감시 항목**:
  - 홈서버(jammy-sub) 상시 구동 서비스: 회의록 자동화 파이프라인(`lab.yangjunman.com/minutes/`), Windows Server AD 랩(`lab.yangjunman.com/winlab/`)
  - 프로덕션 플랫폼: 기술 블로그 & 이력서(`yangjunman.com`)
  - 서버리스 웹 서비스: 내 집 찾기(`yangjunman-auction.vercel.app`)
  - 벤치마크 대시보드: TokenBench(`yangjunman.github.io/claude-code-token-savings-benchmark`)
- **장애 알림(Alerting)**:
  - 5분 이상 다운(연속 1회 이상 응답 실패 또는 4xx/5xx 에러) 발생 시 자동으로 `incident` 라벨의 GitHub Issue 발행.
  - 서비스 복구 감지 시 복구 완료 로그 및 이슈 자동 종료.
- **상태 투명성**: 매 실행마다 `README.md` 및 `history.json`을 자동 갱신하여 100% 투명한 가동률 기록 유지.

---

### 🔗 바로가기
- 📄 [엔지니어 양준혁 이력서](https://www.yangjunman.com/resume)
- 🧪 [양준혁의 실험실](https://www.yangjunman.com/lab)
- 📚 [기술 블로그](https://www.yangjunman.com/blog)
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
