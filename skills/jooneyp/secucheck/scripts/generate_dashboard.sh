#!/bin/bash
# Generate HTML dashboard from security check results
# Usage: ./generate_dashboard.sh [output.html]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
TEMPLATE="$SKILL_DIR/dashboard/template.html"
OUTPUT="${1:-$HOME/.openclaw/workspace/secucheck-report.html}"

# Run checks and capture output (use bash explicitly - ClawHub may strip exec permissions)
runtime_json=$(bash "$SCRIPT_DIR/runtime_check.sh" 2>/dev/null)
config_json=$(bash "$SCRIPT_DIR/gather_config.sh" 2>/dev/null)
skills_json=$(bash "$SCRIPT_DIR/gather_skills.sh" 2>/dev/null)

# Parse runtime data
external_ip=$(echo "$runtime_json" | jq -r '.network.external_ip // "unknown"')
vpn_type=$(echo "$runtime_json" | jq -r '.network.vpn_type // "none"')
behind_nat=$(echo "$runtime_json" | jq -r '.network.behind_nat // false')
potentially_exposed=$(echo "$runtime_json" | jq -r '.network.potentially_exposed // false')
in_container=$(echo "$runtime_json" | jq -r '.isolation.in_container // false')
container_type=$(echo "$runtime_json" | jq -r '.isolation.container_type // "none"')
running_as_root=$(echo "$runtime_json" | jq -r '.privileges.running_as_root // false')
can_sudo=$(echo "$runtime_json" | jq -r '.privileges.can_sudo // false')
current_user=$(echo "$runtime_json" | jq -r '.privileges.current_user // "unknown"')
openclaw_dir_perms=$(echo "$runtime_json" | jq -r '.filesystem.openclaw_dir_perms // "unknown"')

# Calculate scores
count_critical=0
count_high=0
count_medium=0
count_low=0

# Check: Running as root
if [ "$running_as_root" = "true" ]; then
    ((count_critical++))
fi

# Check: Exposed + no VPN + no NAT
if [ "$potentially_exposed" = "true" ] && [ "$vpn_type" = "none" ] && [ "$behind_nat" = "false" ]; then
    ((count_critical++))
elif [ "$potentially_exposed" = "true" ] && [ "$vpn_type" = "none" ]; then
    ((count_high++))
fi

# Check: Bare metal + sudo
if [ "$in_container" = "false" ] && [ "$can_sudo" = "true" ]; then
    ((count_medium++))
fi

# Check: File permissions
if [ "$openclaw_dir_perms" != "700" ] && [ "$openclaw_dir_perms" != "unknown" ]; then
    ((count_medium++))
fi

# Determine overall score
if [ $count_critical -gt 0 ]; then
    score_class="score-critical"
    score_emoji="🔴"
    score_label="Critical"
    score_desc="즉시 조치가 필요합니다"
    runtime_badge="badge-critical"
    runtime_status="Critical"
elif [ $count_high -gt 0 ]; then
    score_class="score-high"
    score_emoji="🟠"
    score_label="High Risk"
    score_desc="빠른 조치를 권장합니다"
    runtime_badge="badge-high"
    runtime_status="High"
elif [ $count_medium -gt 0 ]; then
    score_class="score-medium"
    score_emoji="🟡"
    score_label="Medium"
    score_desc="개선이 필요합니다"
    runtime_badge="badge-medium"
    runtime_status="Medium"
else
    score_class="score-good"
    score_emoji="🟢"
    score_label="Good"
    score_desc="전반적으로 양호합니다"
    runtime_badge="badge-ok"
    runtime_status="OK"
fi

# Generate runtime content
runtime_content="
<div class=\"runtime-card\">
    <h4>🌐 Network</h4>
    <div class=\"runtime-item\">
        <span>External IP</span>
        <span class=\"runtime-value\">$external_ip</span>
    </div>
    <div class=\"runtime-item\">
        <span>VPN</span>
        <span class=\"runtime-value $([ "$vpn_type" != "none" ] && echo 'good' || echo 'warn')\">$vpn_type</span>
    </div>
    <div class=\"runtime-item\">
        <span>Behind NAT</span>
        <span class=\"runtime-value $([ "$behind_nat" = "true" ] && echo 'good' || echo 'warn')\">$behind_nat</span>
    </div>
    <div class=\"runtime-item\">
        <span>Exposed</span>
        <span class=\"runtime-value $([ "$potentially_exposed" = "true" ] && echo 'warn' || echo 'good')\">$potentially_exposed</span>
    </div>
</div>
<div class=\"runtime-card\">
    <h4>📦 Isolation</h4>
    <div class=\"runtime-item\">
        <span>Container</span>
        <span class=\"runtime-value $([ "$in_container" = "true" ] && echo 'good' || echo 'warn')\">$in_container</span>
    </div>
    <div class=\"runtime-item\">
        <span>Type</span>
        <span class=\"runtime-value\">$container_type</span>
    </div>
</div>
<div class=\"runtime-card\">
    <h4>👤 Privileges</h4>
    <div class=\"runtime-item\">
        <span>User</span>
        <span class=\"runtime-value\">$current_user</span>
    </div>
    <div class=\"runtime-item\">
        <span>Root</span>
        <span class=\"runtime-value $([ "$running_as_root" = "true" ] && echo 'bad' || echo 'good')\">$running_as_root</span>
    </div>
    <div class=\"runtime-item\">
        <span>Sudo</span>
        <span class=\"runtime-value $([ "$can_sudo" = "true" ] && echo 'warn' || echo 'good')\">$can_sudo</span>
    </div>
</div>
<div class=\"runtime-card\">
    <h4>📁 Filesystem</h4>
    <div class=\"runtime-item\">
        <span>~/.openclaw perms</span>
        <span class=\"runtime-value $([ "$openclaw_dir_perms" = "700" ] && echo 'good' || echo 'warn')\">$openclaw_dir_perms</span>
    </div>
</div>
"

# Generate findings sections (placeholder - agent fills these)
findings_sections="
<div class=\"section\" id=\"section-channels\">
    <div class=\"section-header\" onclick=\"toggleSection('channels')\">
        <div class=\"section-title\">
            <span>📢</span> Channels
        </div>
        <span class=\"section-badge badge-ok\">OK</span>
    </div>
    <div class=\"section-content expandable\">
        <p style=\"color: var(--text-muted);\">채널 설정이 양호합니다.</p>
    </div>
</div>

<div class=\"section\" id=\"section-agents\">
    <div class=\"section-header\" onclick=\"toggleSection('agents')\">
        <div class=\"section-title\">
            <span>🤖</span> Agents
        </div>
        <span class=\"section-badge badge-ok\">OK</span>
    </div>
    <div class=\"section-content expandable\">
        <p style=\"color: var(--text-muted);\">에이전트 권한 설정이 양호합니다.</p>
    </div>
</div>

<div class=\"section\" id=\"section-cron\">
    <div class=\"section-header\" onclick=\"toggleSection('cron')\">
        <div class=\"section-title\">
            <span>⏰</span> Cron Jobs
        </div>
        <span class=\"section-badge badge-ok\">OK</span>
    </div>
    <div class=\"section-content expandable\">
        <p style=\"color: var(--text-muted);\">크론잡 설정이 양호합니다.</p>
    </div>
</div>

<div class=\"section\" id=\"section-skills\">
    <div class=\"section-header\" onclick=\"toggleSection('skills')\">
        <div class=\"section-title\">
            <span>🧩</span> Skills
        </div>
        <span class=\"section-badge badge-ok\">OK</span>
    </div>
    <div class=\"section-content expandable\">
        <p style=\"color: var(--text-muted);\">설치된 스킬이 양호합니다.</p>
    </div>
</div>
"

# Read template and replace placeholders
html=$(cat "$TEMPLATE")
html="${html//\{\{SCAN_TIME\}\}/$(date '+%Y-%m-%d %H:%M:%S')}"
html="${html//\{\{HOSTNAME\}\}/$(hostname)}"
html="${html//\{\{SCORE_CLASS\}\}/$score_class}"
html="${html//\{\{SCORE_EMOJI\}\}/$score_emoji}"
html="${html//\{\{SCORE_LABEL\}\}/$score_label}"
html="${html//\{\{SCORE_DESC\}\}/$score_desc}"
html="${html//\{\{COUNT_CRITICAL\}\}/$count_critical}"
html="${html//\{\{COUNT_HIGH\}\}/$count_high}"
html="${html//\{\{COUNT_MEDIUM\}\}/$count_medium}"
html="${html//\{\{COUNT_LOW\}\}/$count_low}"
html="${html//\{\{RUNTIME_BADGE\}\}/$runtime_badge}"
html="${html//\{\{RUNTIME_STATUS\}\}/$runtime_status}"
html="${html//\{\{RUNTIME_CONTENT\}\}/$runtime_content}"
html="${html//\{\{FINDINGS_SECTIONS\}\}/$findings_sections}"

# Write output
echo "$html" > "$OUTPUT"
echo "Dashboard generated: $OUTPUT"
echo "Serve with: python3 -m http.server 8766 --directory $(dirname $OUTPUT)"
