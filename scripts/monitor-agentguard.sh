#!/bin/bash
# monitor-agentguard.sh - Autonomous monitoring for AgentGuard

REPO="KyleChen26/agentguard"
LOG_FILE="${AGENTGUARD_LOG:-$HOME/.agentguard/metrics.log}"

# Get current metrics
STARS=$(curl -s "https://api.github.com/repos/$REPO" | grep -o '"stargazers_count": [0-9]*' | cut -d' ' -f2)
FORKS=$(curl -s "https://api.github.com/repos/$REPO" | grep -o '"forks_count": [0-9]*' | cut -d' ' -f2)
ISSUES=$(curl -s "https://api.github.com/repos/$REPO" | grep -o '"open_issues_count": [0-9]*' | cut -d' ' -f2)

# Log with timestamp
echo "$(date '+%Y-%m-%d %H:%M:%S') | Stars: $STARS | Forks: $FORKS | Issues: $ISSUES" >> "$LOG_FILE"

# Alert on significant changes (for autonomous response)
if [ "$STARS" -gt 0 ] 2>/dev/null; then
    echo "🎉 Activity detected! Stars: $STARS"
fi

# Check for new issues
NEW_ISSUES=$(curl -s "https://api.github.com/repos/$REPO/issues?state=open" 2>/dev/null | grep -c '"number":' || echo "0")
NEW_ISSUES=$(echo "$NEW_ISSUES" | tr -d '[:space:]')

# If issues exist, alert (for autonomous response)
if [ "$NEW_ISSUES" -gt 0 ] 2>/dev/null; then
    echo "⚠️  $NEW_ISSUES open issues detected - review needed"
    # In autonomous mode, would trigger review
fi

echo "✅ Monitoring complete | Stars: $STARS | Forks: $FORKS | Issues: $ISSUES"
