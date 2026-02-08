# Security Checkup Report Template

Use this structure for the full audit report.

---

## Header

```markdown
# 🔒 OpenClaw 보안 점검 리포트

**점검 일시**: {datetime}
**점검 대상**: {hostname or identifier}
**사용자 레벨**: {beginner|intermediate|expert}
```

## Executive Summary

For all user levels, start with a brief summary:

```markdown
## 📊 요약

| 위험도 | 발견 수 |
|--------|---------|
| 🔴 심각 | {count} |
| 🟠 높음 | {count} |
| 🟡 중간 | {count} |
| 🟢 낮음 | {count} |

**전체 평가**: {overall assessment}
```

### Overall Assessment Examples

- 🟢 "현재 설정은 전반적으로 안전합니다. 몇 가지 개선 권장사항이 있습니다."
- 🟡 "주의가 필요한 설정이 있습니다. 권장 조치를 검토해주세요."
- 🟠 "보안 위험이 발견되었습니다. 가능한 빨리 조치가 필요합니다."
- 🔴 "심각한 보안 문제가 있습니다. 즉시 조치해주세요."

## Findings Section

List findings by severity (critical first):

```markdown
## 🔍 발견 사항

### 🔴 심각 (Critical)

{findings}

### 🟠 높음 (High)

{findings}

### 🟡 중간 (Medium)

{findings}

### 🟢 낮음 / 권장사항 (Low / Recommendations)

{findings}
```

## Individual Finding Format

Use `templates/finding.md` structure for each finding.

## Recommendations Section

```markdown
## ✅ 권장 조치

### 즉시 필요 (Immediate)

1. {action 1}
2. {action 2}

### 계획 필요 (Planned)

1. {action 1}
2. {action 2}

### 참고 사항 (FYI)

1. {note 1}
```

## Context Section (if user provided)

```markdown
## 📝 환경 정보

- **네트워크 환경**: {VPN/public/etc}
- **사용자 수**: {single/team/public}
- **용도**: {personal/work/public service}

이 정보를 바탕으로 일부 발견 사항의 심각도가 조정되었습니다.
```

## User-Level Adaptations

### For Beginners

- Use analogies and simple language
- Avoid technical jargon
- Focus on "what to do" not "why technically"
- Provide step-by-step instructions
- Include "도움이 필요하시면 말씀해주세요" notes

### For Intermediate

- Include technical details
- Explain the reasoning
- Provide config examples
- Reference documentation

### For Experts

- Focus on attack vectors
- Include edge cases
- Provide defense-in-depth options
- Reference CVEs or known exploits if relevant

## Footer

```markdown
---

**다음 단계**:
- 위 권장 조치를 검토해주세요
- 적용하고 싶은 항목이 있으면 말씀해주세요
- 정기 점검을 원하시면 크론잡을 설정해드릴 수 있습니다

💡 "상세 분석 보여줘" - 특정 항목의 자세한 내용 확인
💡 "이 설정 적용해줘" - 권장 설정 적용 (확인 후 진행)
```
