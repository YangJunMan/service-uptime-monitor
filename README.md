# 🛡️ Service Uptime & Health Monitor

> 엔지니어 양준혁의 블로그, 라이브 실험실, 홈서버(jammy-sub) 및 웹 서비스들의 가동 상태를 **5분 주기로 실시간 감시**하는 자동화 모니터링 시스템입니다.
> 장애 발생 시 5분 이내에 GitHub Issues 및 알림 파이프라인으로 즉시 통보됩니다.

<p align="center">
  <img src="https://img.shields.io/badge/Status-All%20Systems%20Operational-brightgreen?style=for-the-badge&logo=statuspage" alt="System Status Badge">
  <br>
  <sub>마지막 자동 점검 시각: <b>2026-11-02 03:25:56 KST</b> · 5분 주기 크론(GitHub Actions)</sub>
</p>

---

## 📊 실시간 서비스 가동 현황 (Live Status Board)

| 서비스명 | 대상 엔드포인트 | 가동 상태 | 응답 코드 | 응답 속도 |
| :--- | :--- | :---: | :---: | :---: |
| **포트폴리오 & 기술 블로그** | [https://www.yangjunman.com](https://www.yangjunman.com) | 🟢 정상 (UP) | `200` | 387 ms |
| **양준혁의 실험실 (Lab Portal)** | [https://www.yangjunman.com/lab](https://www.yangjunman.com/lab) | 🟢 정상 (UP) | `200` | 338 ms |
| **회의록 만들기 (홈서버 AI 음성 전사·요약)** | [https://lab.yangjunman.com/minutes/](https://lab.yangjunman.com/minutes/) | 🟢 정상 (UP) | `200` | 639 ms |
| **Windows Server AD 랩 (권한 격리 실습 포털)** | [https://lab.yangjunman.com/winlab/](https://lab.yangjunman.com/winlab/) | 🟢 정상 (UP) | `200` | 643 ms |
| **Token Savings Benchmark (대시보드)** | [https://yangjunman.github.io/claude-code-token-savings-benchmark/web/#overview](https://yangjunman.github.io/claude-code-token-savings-benchmark/web/#overview) | 🟢 정상 (UP) | `200` | 142 ms |
| **내 집 찾기 (Search Auction 경매 지도 검색)** | [https://yangjunman-auction.vercel.app/](https://yangjunman-auction.vercel.app/) | 🟢 정상 (UP) | `200` | 255 ms |

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
