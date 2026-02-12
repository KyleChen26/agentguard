# AgentGuard

Pre-deployment security scanner for AI agent skills and configurations.

[![GitHub Actions](https://github.com/KyleChen26/agentguard/actions/workflows/agentguard-scan.yml/badge.svg)](https://github.com/KyleChen26/agentguard/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Quick Start

```bash
# Install
pip install agentguard

# Scan a configuration file
agentguard scan ./my-agent-config.yaml

# Scan with JSON output
agentguard scan --format json ./config/

# List all rules
agentguard rules
```

## GitHub Actions

Add to your workflow:

```yaml
name: AgentGuard Security Scan
on: [push, pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: kylechen26/agentguard-action@v1
```

## Supported Vulnerabilities

| ID | Name | Severity |
|----|------|----------|
| AG-001 | Prompt Injection Vector | 🔴 Critical |
| AG-002 | Hardcoded API Key | 🔴 Critical |
| AG-003 | Unrestricted Tool Permissions | 🟠 High |
| AG-004 | Unrestricted File System Access | 🟠 High |
| AG-005 | Potential Data Exfiltration | 🟡 Medium |

## Documentation

- [Language Choice Analysis](docs/language-choice-analysis.md)
- [Deployment Architecture](docs/deployment-architecture.md)
- [Free Deployment Plan](docs/free-deployment-plan.md)
- [Business Plan](docs/business-plan.md)

## License

MIT © KyleChen
