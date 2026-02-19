#!/usr/bin/env python3
"""
카카오톡 채널 웹훅 서버
카카오 i 오픈빌더 v2 호환

아키텍처:
  카카오톡 채널 → 오픈빌더 웹훅 → 이 서버(포트 8401) → Ollama(qwen3:8b) → Gemini fallback

환경변수:
  KAKAOTALK_PORT           기본 8401
  OLLAMA_HOST              기본 http://localhost:11434
  OLLAMA_MODEL             기본 qwen3:8b
  GEMINI_API_KEY           Gemini 2.5 Flash Lite fallback용
  KAKAO_CALLBACK_SECRET    웹훅 서명 검증 (선택)
  KAKAOTALK_PERSONA_NAME   AI 이름 (기본 "AI 비서")
  KAKAOTALK_SYSTEM_PROMPT  시스템 프롬프트 (기본값 사용 or 직접 지정)
  KAKAOTALK_LOG_DIR        로그 디렉터리 (기본 ~/.openclaw/logs)

Python 3.9+ / stdlib only
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import re
import sys
import threading
import urllib.request
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# ─── 설정 ─────────────────────────────────────────────────────────────────────

PORT = int(os.environ.get("KAKAOTALK_PORT", 8401))
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:8b")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
KAKAO_SECRET = os.environ.get("KAKAO_CALLBACK_SECRET", "")
PERSONA_NAME = os.environ.get("KAKAOTALK_PERSONA_NAME", "AI 비서")

_default_log_dir = Path.home() / ".openclaw" / "logs"
LOG_DIR = Path(os.environ.get("KAKAOTALK_LOG_DIR", str(_default_log_dir)))
LOG_FILE = LOG_DIR / "kakaotalk.log"

TEXT_LIMIT = 900          # 카카오 SimpleText 최대 1000자, 안전 마진
MAX_HISTORY = 20          # 최대 10턴 (user+assistant = 20 messages)
RESPONSE_TIMEOUT = 4.5    # 카카오 5초 제한보다 0.5초 여유
OLLAMA_TIMEOUT = 90       # Ollama 최대 대기 시간

# ─── 시스템 프롬프트 (환경변수로 완전 교체 가능) ──────────────────────────────

_DEFAULT_SYSTEM_PROMPT = f"""당신은 {PERSONA_NAME}입니다.
한국어로 답변하세요. 친절하고 실용적으로.
빈말 금지. 바로 본론부터.
"좋은 질문이네요!" 같은 빈말 절대 금지.
답변은 핵심만, 간결하게 (500자 이내 권장)."""

SYSTEM_PROMPT = os.environ.get("KAKAOTALK_SYSTEM_PROMPT", _DEFAULT_SYSTEM_PROMPT)

# ─── 빠른 응답 버튼 ───────────────────────────────────────────────────────────

QUICK_REPLIES = [
    {"label": "다시 물어보기", "action": "message", "messageText": "다시 물어보기"},
    {"label": "처음으로",      "action": "message", "messageText": "처음으로"},
]

# ─── 인메모리 저장소 ──────────────────────────────────────────────────────────

# user_id → {"history": [{"role": ..., "content": ...}, ...]}
sessions: dict[str, dict] = {}

# user_id → {"response": str | None, "ready": bool}
pending_responses: dict[str, dict] = {}

_lock = threading.Lock()

# ─── 로깅 ─────────────────────────────────────────────────────────────────────

def _log(msg: str) -> None:
    """파일 + stdout 동시 출력."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

# ─── 보안: 서명 검증 ──────────────────────────────────────────────────────────

def _verify_signature(body: bytes, signature: str) -> bool:
    """KAKAO_CALLBACK_SECRET 기반 HMAC-SHA1 검증. 시크릿 없으면 스킵."""
    if not KAKAO_SECRET:
        return True
    expected = hmac.new(
        KAKAO_SECRET.encode("utf-8"),
        body,
        hashlib.sha1,
    ).hexdigest()
    return hmac.compare_digest(expected, signature or "")

# ─── LLM 호출 ─────────────────────────────────────────────────────────────────

def _strip_thinking_tags(text: str) -> str:
    """<think>...</think> 태그 제거 (qwen3 thinking mode)."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def _call_ollama(messages: list[dict]) -> str:
    """Ollama chat API 호출 (qwen3:8b)."""
    payload = json.dumps({
        "model": "qwen3:8b",
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 600,
        },
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{OLLAMA_HOST}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT) as resp:
        data = json.load(resp)
        text = data["message"]["content"].strip()
        return _strip_thinking_tags(text)


def _call_gemini(messages: list[dict]) -> str:
    """Gemini 2.5 Flash Lite fallback 호출."""
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY 미설정")

    # 시스템 프롬프트를 첫 user 메시지에 prepend
    contents = []
    for msg in messages:
        if msg["role"] == "system":
            # Gemini에는 system role 없음 — 첫 user에 합치거나 별도 처리
            continue
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})

    # 시스템 프롬프트를 systemInstruction으로 전달
    system_msgs = [m for m in messages if m["role"] == "system"]
    system_instruction = system_msgs[0]["content"] if system_msgs else SYSTEM_PROMPT

    payload = json.dumps({
        "system_instruction": {"parts": [{"text": system_instruction}]},
        "contents": contents,
        "generationConfig": {
            "maxOutputTokens": 600,
            "temperature": 0.7,
        },
    }).encode("utf-8")

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
    )
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()


def _get_llm_response(user_id: str, utterance: str, history: list[dict]) -> str | None:
    """Ollama → Gemini 순서로 LLM 응답 생성."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history[-MAX_HISTORY:])
    messages.append({"role": "user", "content": utterance})

    # 1차: Ollama qwen3:8b
    try:
        response = _call_ollama(messages)
        _log(f"✅ Ollama 응답 완료: user={user_id}, len={len(response)}")
        return response
    except Exception as e:
        _log(f"⚠️ Ollama 실패: {e} — Gemini fallback 시도")

    # 2차: Gemini 2.5 Flash Lite
    try:
        response = _call_gemini(messages)
        _log(f"✅ Gemini 응답 완료: user={user_id}, len={len(response)}")
        return response
    except Exception as e:
        _log(f"❌ Gemini 실패: {e}")
        return None

# ─── 카카오 응답 포맷 ─────────────────────────────────────────────────────────

def _kakao_response(text: str, include_quick_replies: bool = True) -> dict:
    """카카오 오픈빌더 v2 응답 딕셔너리 생성."""
    # 900자 제한 자동 트런케이트
    if len(text) > TEXT_LIMIT:
        text = text[: TEXT_LIMIT - 3] + "..."

    result: dict = {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": text}}],
        },
    }

    if include_quick_replies:
        result["template"]["quickReplies"] = QUICK_REPLIES

    return result

# ─── HTTP 핸들러 ──────────────────────────────────────────────────────────────

class KakaoWebhookHandler(BaseHTTPRequestHandler):
    """카카오 i 오픈빌더 웹훅 요청 처리."""

    # 기본 httpd 로그 억제
    def log_message(self, fmt, *args):  # noqa: N802
        pass

    def _send_json(self, data: dict, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # ── GET /health ──────────────────────────────────────────────────────────

    def do_GET(self):  # noqa: N802
        if self.path in ("/health", "/"):
            with _lock:
                active_sessions = len(sessions)
                pending = len(pending_responses)
            self._send_json({
                "status": "ok",
                "port": PORT,
                "active_sessions": active_sessions,
                "pending_responses": pending,
            })
        else:
            self.send_response(404)
            self.end_headers()

    # ── POST /kakao ───────────────────────────────────────────────────────────

    def do_POST(self):  # noqa: N802
        # 항상 200 반환 (카카오 요구사항)
        try:
            self._handle_post()
        except Exception as e:
            _log(f"❌ 핸들러 예외: {e}")
            self._send_json(_kakao_response("일시적 오류가 발생했어요. 잠시 후 다시 시도해주세요 😊"))

    def _handle_post(self) -> None:
        # 바디 읽기
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length)
        except Exception as e:
            _log(f"❌ 바디 읽기 실패: {e}")
            self._send_json(_kakao_response("요청을 읽을 수 없어요."))
            return

        # 서명 검증 (선택)
        signature = self.headers.get("X-Kakao-Signature", "")
        if not _verify_signature(body_bytes, signature):
            _log("⚠️ 서명 검증 실패 — 요청 무시")
            self._send_json(_kakao_response("인증 실패."))
            return

        # JSON 파싱
        try:
            body = json.loads(body_bytes.decode("utf-8"))
        except json.JSONDecodeError as e:
            _log(f"❌ JSON 파싱 실패: {e}")
            self._send_json(_kakao_response("잘못된 요청 형식이에요."))
            return

        # utterance / user_id 추출
        user_request = body.get("userRequest", {})
        utterance = user_request.get("utterance", "").strip()
        user_id = user_request.get("user", {}).get("id", "unknown")

        _log(f"📩 user={user_id[:12]}... | utterance={utterance[:60]}")

        if not utterance:
            self._send_json(_kakao_response("메시지를 입력해주세요 😊"))
            return

        # ── 세션 초기화 명령 ──────────────────────────────────────────────────
        RESET_TRIGGERS = {"처음으로", "처음부터", "시작", "안녕", "안녕하세요", "hi", "hello", "/reset"}
        if utterance.lower() in RESET_TRIGGERS:
            with _lock:
                sessions.pop(user_id, None)
                pending_responses.pop(user_id, None)
            welcome = (
                f"안녕하세요! 저는 {PERSONA_NAME}이에요 🙌\n\n"
                "무엇이든 물어보세요!"
            )
            self._send_json(_kakao_response(welcome))
            return

        # ── "다시 물어보기" — 캐시된 결과 반환 ─────────────────────────────
        if utterance == "다시 물어보기":
            with _lock:
                pending = pending_responses.get(user_id)

            if pending is None:
                self._send_json(_kakao_response("이전 질문이 없어요. 새로 질문해주세요 😊"))
                return

            if not pending.get("ready"):
                self._send_json(_kakao_response("아직 생각 중이에요! 잠시 후 다시 눌러주세요 🤔"))
                return

            # 준비 완료
            cached_text = pending.get("response") or ""
            with _lock:
                pending_responses.pop(user_id, None)

            if cached_text:
                self._send_json(_kakao_response(cached_text))
            else:
                self._send_json(_kakao_response("응답 생성에 실패했어요. 다시 질문해주세요 😊"))
            return

        # ── 일반 질문 처리 ────────────────────────────────────────────────────
        with _lock:
            if user_id not in sessions:
                sessions[user_id] = {"history": []}
            history = list(sessions[user_id]["history"])

        # 결과 홀더 준비
        result_holder: dict = {"response": None, "ready": False}
        event = threading.Event()

        with _lock:
            pending_responses[user_id] = result_holder

        def llm_task() -> None:
            """백그라운드 LLM 호출 + 세션 업데이트."""
            response = _get_llm_response(user_id, utterance, history)
            result_holder["response"] = response
            result_holder["ready"] = True
            event.set()

            # 세션 히스토리 업데이트
            with _lock:
                if user_id in sessions:
                    sess_hist = sessions[user_id]["history"]
                    sess_hist.append({"role": "user", "content": utterance})
                    sess_hist.append({"role": "assistant", "content": response or ""})
                    # 최대 10턴(20 messages) 유지
                    if len(sess_hist) > MAX_HISTORY:
                        sessions[user_id]["history"] = sess_hist[-MAX_HISTORY:]

        thread = threading.Thread(target=llm_task, daemon=True)
        thread.start()

        # 4.5초 이내 응답 대기
        event.wait(timeout=RESPONSE_TIMEOUT)

        if result_holder["ready"] and result_holder["response"]:
            # LLM이 제때 응답 완료 → 즉시 반환
            with _lock:
                pending_responses.pop(user_id, None)
            self._send_json(_kakao_response(result_holder["response"]))
        else:
            # 타임아웃 → thinking 메시지 반환 (백그라운드 계속 실행)
            _log(f"⏳ 타임아웃: user={user_id[:12]}... — 백그라운드 계속 실행 중")
            thinking_msg = (
                f"{PERSONA_NAME}이 생각 중이에요... 잠시만요 🤔\n\n"
                "답변이 준비되면 '다시 물어보기'를 눌러주세요!"
            )
            self._send_json(_kakao_response(thinking_msg))

# ─── 메인 ─────────────────────────────────────────────────────────────────────

def main() -> None:
    _log(f"🚀 카카오 채널 웹훅 서버 시작 — 포트 {PORT}")
    _log(f"   Ollama: {OLLAMA_HOST}")
    _log(f"   Gemini: {'설정됨' if GEMINI_API_KEY else '미설정'}")
    _log(f"   서명검증: {'활성화' if KAKAO_SECRET else '비활성화(선택사항)'}")
    _log(f"   로그: {LOG_FILE}")

    server = HTTPServer(("0.0.0.0", PORT), KakaoWebhookHandler)
    _log(f"   웹훅 엔드포인트: POST http://0.0.0.0:{PORT}/kakao")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        _log("🛑 서버 종료")
        server.server_close()


if __name__ == "__main__":
    main()
