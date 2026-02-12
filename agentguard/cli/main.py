"""AgentGuard CLI."""
import click
import json
from pathlib import Path
from typing import Optional
import sys

from agentguard.scanner.core import Scanner, Severity


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """AgentGuard - Security scanner for AI agents."""
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
@click.option(
    "--severity",
    type=click.Choice(["critical", "high", "medium", "low", "info"]),
    help="Minimum severity to report",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path",
)
def scan(path: str, output_format: str, severity: Optional[str], output: Optional[str]):
    """Scan agent configuration for security issues."""
    scanner = Scanner()
    
    path_obj = Path(path)
    
    if path_obj.is_file():
        result = scanner.scan_file(path)
        results = [result]
    else:
        results = scanner.scan_directory(path)
    
    # Filter by severity if specified
    if severity:
        min_severity = Severity(severity)
        severity_order = ["critical", "high", "medium", "low", "info"]
        min_index = severity_order.index(min_severity.value)
        allowed = severity_order[: min_index + 1]
        
        for result in results:
            result.findings = [f for f in result.findings if f.severity.value in allowed]
    
    # Output results
    if output_format == "json":
        output_data = {
            "scan_results": [r.to_dict() for r in results],
            "total_files": len(results),
            "total_findings": sum(len(r.findings) for r in results),
        }
        output_text = json.dumps(output_data, indent=2)
    else:
        output_text = format_text_output(results)
    
    if output:
        Path(output).write_text(output_text)
        click.echo(f"Results saved to {output}")
    else:
        click.echo(output_text)
    
    # Exit with error code if critical findings
    critical_count = sum(
        1 for r in results for f in r.findings if f.severity == Severity.CRITICAL
    )
    if critical_count > 0:
        sys.exit(1)


def format_text_output(results) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 80)
    lines.append("AgentGuard Security Scan Results")
    lines.append("=" * 80)
    lines.append("")
    
    total_findings = 0
    for result in results:
        if not result.findings:
            continue
        
        lines.append(f"\n📁 {result.file_path}")
        lines.append("-" * 80)
        
        for finding in result.findings:
            total_findings += 1
            severity_emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🔵",
                "info": "⚪",
            }.get(finding.severity.value, "⚪")
            
            lines.append(f"\n  {severity_emoji} {finding.severity.value.upper()}: {finding.rule_name}")
            lines.append(f"     Rule: {finding.rule_id}")
            lines.append(f"     Line {finding.line_number}, Column {finding.column}")
            lines.append(f"     {finding.message}")
            lines.append(f"     Snippet: {finding.snippet}")
            lines.append(f"\n     💡 Remediation: {finding.remediation}")
            if finding.references:
                lines.append(f"\n     📚 References:")
                for ref in finding.references:
                    lines.append(f"       • {ref}")
    
    lines.append("\n" + "=" * 80)
    lines.append(f"Scan Complete: {total_findings} finding(s) detected")
    lines.append("=" * 80)
    
    return "\n".join(lines)


@cli.command()
def rules():
    """List all available security rules."""
    from agentguard.scanner.core import RULES
    
    click.echo("\n📋 AgentGuard Security Rules\n")
    click.echo("=" * 80)
    
    for rule in RULES:
        severity_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🔵",
            "info": "⚪",
        }.get(rule.severity.value, "⚪")
        
        click.echo(f"\n{severity_emoji} {rule.rule_id}: {rule.name}")
        click.echo(f"   Severity: {rule.severity.value.upper()}")
        click.echo(f"   Category: {rule.category.value}")
        click.echo(f"   {rule.description}")
    
    click.echo(f"\n{'=' * 80}")
    click.echo(f"Total: {len(RULES)} rules")


def main():
    """Entry point."""
    cli()


if __name__ == "__main__":
    main()
