"""AgentGuard - Core scanner module."""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import re
import yaml
import json
from pathlib import Path


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class RuleCategory(Enum):
    PROMPT_INJECTION = "prompt_injection"
    SECRETS = "secrets"
    PERMISSIONS = "permissions"
    FILE_ACCESS = "file_access"
    NETWORK = "network"
    MEMORY = "memory"


@dataclass
class Finding:
    """A security finding."""
    rule_id: str
    rule_name: str
    category: RuleCategory
    severity: Severity
    message: str
    file_path: str
    line_number: int
    column: int
    snippet: str
    remediation: str
    references: List[str] = field(default_factory=list)


@dataclass
class ScanResult:
    """Result of a scan."""
    file_path: str
    findings: List[Finding]
    scanned_at: str
    duration_ms: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "scanned_at": self.scanned_at,
            "duration_ms": self.duration_ms,
            "findings": [
                {
                    "rule_id": f.rule_id,
                    "rule_name": f.rule_name,
                    "category": f.category.value,
                    "severity": f.severity.value,
                    "message": f.message,
                    "line_number": f.line_number,
                    "column": f.column,
                    "snippet": f.snippet,
                    "remediation": f.remediation,
                    "references": f.references,
                }
                for f in self.findings
            ],
        }


class Rule:
    """Base class for security rules."""
    
    def __init__(
        self,
        rule_id: str,
        name: str,
        description: str,
        category: RuleCategory,
        severity: Severity,
        remediation: str,
        references: List[str],
    ):
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.category = category
        self.severity = severity
        self.remediation = remediation
        self.references = references
    
    def check(self, content: str, file_path: str) -> List[Finding]:
        """Check content for violations of this rule."""
        raise NotImplementedError


class PatternRule(Rule):
    """Rule that checks for regex patterns."""
    
    def __init__(
        self,
        rule_id: str,
        name: str,
        description: str,
        category: RuleCategory,
        severity: Severity,
        pattern: str,
        remediation: str,
        references: List[str],
        message_template: str = "Potential {category} issue found",
    ):
        super().__init__(
            rule_id, name, description, category, severity, remediation, references
        )
        self.pattern = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
        self.message_template = message_template
    
    def check(self, content: str, file_path: str) -> List[Finding]:
        findings = []
        lines = content.split("\n")
        
        for line_num, line in enumerate(lines, 1):
            for match in self.pattern.finditer(line):
                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        category=self.category,
                        severity=self.severity,
                        message=self.message_template.format(category=self.category.value),
                        file_path=file_path,
                        line_number=line_num,
                        column=match.start() + 1,
                        snippet=line.strip()[:100],
                        remediation=self.remediation,
                        references=self.references,
                    )
                )
        
        return findings


# Define all security rules
RULES = [
    # Rule 1: Prompt Injection - User input in system prompts
    PatternRule(
        rule_id="AG-001",
        name="Prompt Injection Vector",
        description="User input is being directly concatenated into system prompts without sanitization",
        category=RuleCategory.PROMPT_INJECTION,
        severity=Severity.CRITICAL,
        pattern=r'(system_prompt|system|prompt)\s*[=:]\s*["\'].*(\{user_input|\{input|\{\{|%s|%d|\$\{)',
        remediation="Use prompt templates with strict parameter validation. Never concatenate user input directly into system prompts.",
        references=[
            "https://owasp.org/www-project-llm-top-10/",
            "https://portswigger.net/web-security/llm-attacks",
        ],
        message_template="Potential prompt injection: User input concatenated in system prompt",
    ),
    
    # Rule 2: Hardcoded Secrets
    PatternRule(
        rule_id="AG-002",
        name="Hardcoded API Key",
        description="API keys or secrets are hardcoded in configuration",
        category=RuleCategory.SECRETS,
        severity=Severity.CRITICAL,
        pattern=r'(api[_-]?key|apikey|token|secret|password)\s*[=:]\s*["\'][a-zA-Z0-9_-]{20,}["\']',
        remediation="Use environment variables or a secrets manager. Never hardcode credentials.",
        references=[
            "https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html",
        ],
        message_template="Hardcoded credential detected: {category}",
    ),
    
    # Rule 3: Tool Permission Overreach
    PatternRule(
        rule_id="AG-003",
        name="Unrestricted Tool Permissions",
        description="Tools have excessive permissions without validation",
        category=RuleCategory.PERMISSIONS,
        severity=Severity.HIGH,
        pattern=r'(allow_all|unrestricted|bypass.*auth|disable.*check)',
        remediation="Implement least privilege principle. Validate all tool invocations.",
        references=[
            "https://owasp.org/www-project-top-10/",
        ],
        message_template="Excessive permissions detected: {category}",
    ),
    
    # Rule 4: Insecure File Access
    PatternRule(
        rule_id="AG-004",
        name="Unrestricted File System Access",
        description="File system operations without path validation",
        category=RuleCategory.FILE_ACCESS,
        severity=Severity.HIGH,
        pattern=r'(read_file|write_file|delete_file)\s*[=:]\s*True|allow_all_files|bypass_path_validation',
        remediation="Validate all file paths against allowed directories. Use path canonicalization.",
        references=[
            "https://owasp.org/www-community/attacks/Path_Traversal",
        ],
        message_template="Unrestricted file access: {category}",
    ),
    
    # Rule 5: Data Exfiltration
    PatternRule(
        rule_id="AG-005",
        name="Potential Data Exfiltration",
        description="Tools can send data to external URLs without validation",
        category=RuleCategory.NETWORK,
        severity=Severity.MEDIUM,
        pattern=r'(http://|https://|fetch\(|requests\.|urllib)',
        remediation="Validate all external URLs against an allowlist. Log all outbound requests.",
        references=[
            "https://owasp.org/www-project-top-10/",
        ],
        message_template="External network access detected: {category}",
    ),
]


class Scanner:
    """Main scanner class."""
    
    def __init__(self, rules: Optional[List[Rule]] = None):
        self.rules = rules or RULES
    
    def scan_file(self, file_path: str) -> ScanResult:
        """Scan a single file."""
        from datetime import datetime
        import time
        
        start_time = time.time()
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        content = path.read_text(encoding="utf-8")
        findings = []
        
        for rule in self.rules:
            try:
                rule_findings = rule.check(content, file_path)
                findings.extend(rule_findings)
            except Exception as e:
                print(f"Error running rule {rule.rule_id}: {e}")
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        return ScanResult(
            file_path=file_path,
            findings=findings,
            scanned_at=datetime.utcnow().isoformat(),
            duration_ms=duration_ms,
        )
    
    def scan_directory(self, directory: str) -> List[ScanResult]:
        """Scan all files in a directory."""
        results = []
        path = Path(directory)
        
        for file_path in path.rglob("*"):
            if file_path.is_file() and file_path.suffix in [".yaml", ".yml", ".json", ".py"]:
                try:
                    result = self.scan_file(str(file_path))
                    results.append(result)
                except Exception as e:
                    print(f"Error scanning {file_path}: {e}")
        
        return results
