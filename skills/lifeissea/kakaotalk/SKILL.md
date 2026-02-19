---
name: kakaotalk
version: 1.0.0
description: "카카오톡 채널 웹훅 브릿지 AI 비서. 카카오 i 오픈빌더와 연동해 라온(Raon) AI 비서와 대화. Ollama(qwen3:8b) → Gemini 2.5 Flash Lite fallback, 세션 관리, 900자 자동 트런케이트."
author: Yeomyeonggeori Inc. <iam@dawn.kim>
license: MIT
metadata:
  openclaw:
    env:
      - name: GEMINI_API_KEY
        description: "Google Gemini 2.5 Flash Lite API 키 (Ollama 실패 시 fallback)"
        required: false
      - name: KAKAO_CALLBACK_SECRET
        description: "카카오 오픈빌더 웹훅 서명 검증 시크릿 (선택, 보안 강화)"
        required: false
      - name: KAKAOTALK_PORT
        description: "웹훅 서버 포트 (기본 8401)"
        required: false
      - name: OLLAMA_HOST
        description: "Ollama 서버 주소 (기본 http://localhost:11434)"
        required: false
    requires:
      bins: ["python3"]
    notes: "Ollama가 로컬에 설치되어 있고 qwen3:8b 모델이 pull되어 있어야 합니다. GEMINI_API_KEY는 Ollama 실패 시 자동 fallback에 사용됩니다."
---

# kakaotalk — 카카오톡 AI 비서 스킬

카카오톡 채널에서 라온(Raon) AI 비서와 대화할 수 있는 OpenClaw 스킬.  
카카오 i 오픈빌더 "폴백 블록"의 스킬 서버로 등록해 사용합니다.

## 아키텍처

```
카카오톡 채널
     ↓
카카오 i 오픈빌더 (폴백 블록 → 스킬 서버)
     ↓ POST /kakao
Python 웹훅 서버 (포트 8401)
     ↓
Ollama qwen3:8b (90초, 로컬) → 실패 시 Gemini 2.5 Flash Lite
     ↓
카카오 v2 응답 (simpleText + quickReplies)
```

---

## 환경변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `GEMINI_API_KEY` | Gemini 2.5 Flash Lite API 키 (Ollama fallback) | — |
| `KAKAO_CALLBACK_SECRET` | 웹훅 서명 검증 시크릿 (선택) | — |
| `KAKAOTALK_PORT` | 서버 포트 | `8401` |
| `OLLAMA_HOST` | Ollama 주소 | `http://localhost:11434` |
| `OLLAMA_MODEL` | Ollama 모델 | `qwen3:8b` |
| `KAKAOTALK_PERSONA_NAME` | AI 이름 (웰컴·처리중 메시지에 표시) | `AI 비서` |
| `KAKAOTALK_SYSTEM_PROMPT` | 시스템 프롬프트 전체 교체 | 기본 프롬프트 |
| `KAKAOTALK_LOG_DIR` | 로그 저장 경로 | `~/.openclaw/logs` |

```bash
# ~/.openclaw/.env 에 추가
GEMINI_API_KEY=내_API_키
KAKAO_CALLBACK_SECRET=오픈빌더_시크릿  # 선택
KAKAOTALK_PERSONA_NAME=라온            # AI 이름 커스텀
# KAKAOTALK_SYSTEM_PROMPT=당신은 ...   # 프롬프트 완전 교체 시
```

---

## 설치 및 실행

### 1. Ollama 모델 준비

```bash
ollama pull qwen3:8b
```

### 2. 서비스 등록 (launchd — macOS 부팅 시 자동 실행)

```bash
bash scripts/install-service.sh
```

- launchd label: `com.yeomyeonggeori.kakaotalk`
- 로그: `/Users/tomas/.openclaw/workspace/logs/kakaotalk.log`

### 3. 수동 실행 (테스트용)

```bash
python3 scripts/server.py
# 기본 포트 8401, Ctrl+C로 종료
```

---

## 카카오 오픈빌더 설정 순서

1. **카카오 비즈니스 계정** — https://business.kakao.com 에서 계정 생성
2. **카카오 i 오픈빌더** — https://i.kakao.com 접속 → 봇 생성
3. **스킬 등록**  
   좌측 메뉴 **스킬** → **스킬 추가** → 스킬 서버 URL 입력:
   ```
   https://<ngrok_URL_or_server>/kakao
   ```
4. **폴백 블록 연결**  
   **시나리오** → **폴백 블록** → 스킬 탭 → 위에서 만든 스킬 선택 → 저장
5. (선택) **카카오 채널 연결**  
   카카오채널 관리자센터 → 봇 연결

---

## 로컬 테스트 (ngrok)

```bash
# ngrok 터널 생성 + URL 자동 출력
bash scripts/ngrok-setup.sh

# 출력된 URL을 카카오 오픈빌더 스킬 서버 URL에 입력
# 예: https://abc123.ngrok.io/kakao
```

### curl 직접 테스트

```bash
curl -s -X POST http://localhost:8401/kakao \
  -H "Content-Type: application/json" \
  -d '{
    "userRequest": {
      "utterance": "TIPS 신청 방법 알려줘",
      "user": {"id": "test_user_001"}
    },
    "bot": {"id": "test_bot"},
    "intent": {"name": "폴백 블록"}
  }' | python3 -m json.tool
```

헬스체크:
```bash
curl http://localhost:8401/health
```

---

## 응답 동작 방식

| 상황 | 동작 |
|------|------|
| LLM 4.5초 이내 응답 | 바로 답변 반환 |
| LLM 4.5초 초과 | "라온이 생각 중..." 반환, 백그라운드 계속 생성 |
| "다시 물어보기" 클릭 | 캐시된 완료 응답 반환 |
| "처음으로" 클릭 | 세션 초기화 + 웰컴 메시지 |

---

## 서비스 관리

```bash
# 중지
launchctl unload ~/Library/LaunchAgents/com.yeomyeonggeori.kakaotalk.plist

# 시작
launchctl load ~/Library/LaunchAgents/com.yeomyeonggeori.kakaotalk.plist

# 로그 실시간 확인
tail -f /Users/tomas/.openclaw/workspace/logs/kakaotalk.log

# 상태 확인
launchctl list | grep kakaotalk
```

---

## 파일 구조

```
skills/kakaotalk/
├── SKILL.md                  # 이 파일
├── package.json              # ClawHub 배포 메타
├── scripts/
│   ├── server.py             # 웹훅 서버 (Python stdlib)
│   ├── install-service.sh    # launchd 서비스 등록
│   └── ngrok-setup.sh        # ngrok 터널 도우미
└── references/
    └── kakao-api.md          # 카카오 오픈빌더 v2 API 레퍼런스
```
