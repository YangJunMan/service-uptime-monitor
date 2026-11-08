# 서비스 가동 상태 모니터

## [실시간 대시보드 열기](https://yangjunman.github.io/service-uptime-monitor/)

서비스 가동 상태와 방문자 브라우저에서 측정한 핑, 홈서버 `jammy-sub`의 CPU, RAM, VRAM 사용량을 확인할 수 있습니다.

## 서비스 가동 현황

마지막 자동 점검: 2026-11-08 21:12:40 KST · GitHub Actions에서 5분마다 점검

| 서비스명 | 대상 주소 | 상태 | HTTP 상태 | 응답 시간 |
| :--- | :--- | :---: | :---: | :---: |
| **포트폴리오 & 기술 블로그** | [https://www.yangjunman.com](https://www.yangjunman.com) | 정상 | `200` | 144 ms |
| **양준혁의 실험실 (Lab Portal)** | [https://www.yangjunman.com/lab](https://www.yangjunman.com/lab) | 정상 | `200` | 148 ms |
| **회의록 만들기 (홈서버 AI 음성 전사·요약)** | [https://lab.yangjunman.com/minutes/](https://lab.yangjunman.com/minutes/) | 정상 | `200` | 679 ms |
| **Windows Server AD 랩 (권한 격리 실습 포털)** | [https://lab.yangjunman.com/winlab/](https://lab.yangjunman.com/winlab/) | 정상 | `200` | 594 ms |
| **Token Savings Benchmark (대시보드)** | [https://yangjunman.github.io/claude-code-token-savings-benchmark/web/#overview](https://yangjunman.github.io/claude-code-token-savings-benchmark/web/#overview) | 정상 | `200` | 120 ms |
| **내 집 찾기 (Search Auction 경매 지도 검색)** | [https://yangjunman-auction.vercel.app/](https://yangjunman-auction.vercel.app/) | 정상 | `200` | 159 ms |

## 모니터링 방식

- GitHub Actions가 서비스에 HTTP 요청을 보내 상태와 응답 시간을 기록합니다.
- 최초 장애 감지와 복구 시 GitHub Issue 생성을 시도합니다.
- `history.json`에는 서비스별 최근 점검 결과를 최대 288개 저장합니다. 기존 기록은 누적되기 시작한 시점부터 확인할 수 있습니다.
- 브라우저 핑은 방문자의 네트워크에서 측정하며, 자동 점검 결과와 다를 수 있습니다.

## 바로가기

- [이력서](https://www.yangjunman.com/resume)
- [실험실](https://www.yangjunman.com/lab)
- [기술 블로그](https://www.yangjunman.com/blog)
