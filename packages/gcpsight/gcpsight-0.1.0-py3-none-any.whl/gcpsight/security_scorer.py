# security_scorer.py
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.columns import Columns
from rich.rule import Rule
from rich.progress import Progress, BarColumn, TextColumn
from rich.align import Align

class RiskLevel(Enum):
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    INFO = 1

@dataclass
class SecurityFinding:
    check_type: str
    resource_name: str
    risk_level: RiskLevel
    score_impact: int
    description: str
    details: Dict[str, Any]
    remediation: str

@dataclass
class SecurityScore:
    total_score: int
    max_possible_score: int
    percentage: float
    risk_level: RiskLevel
    findings_count: Dict[str, int]
    findings: List[SecurityFinding]

class SecurityScorer:
    def __init__(self):
        self.max_score_per_check = 100
        self.weight_multipliers = {
            RiskLevel.CRITICAL: 1.0,
            RiskLevel.HIGH: 0.8,
            RiskLevel.MEDIUM: 0.6,
            RiskLevel.LOW: 0.4,
            RiskLevel.INFO: 0.2
        }

    def score_firewall_findings(self, firewall_results: List[Dict]) -> List[SecurityFinding]:
        findings = []
        if not firewall_results or firewall_results == ["Error: Permission Denied"] or isinstance(firewall_results[0], str):
            return findings

        for firewall in firewall_results:
            risk_level = self._assess_firewall_risk(firewall)
            score_impact = self._calculate_score_impact(risk_level)
            
            findings.append(SecurityFinding(
                check_type="Open Firewall",
                resource_name=firewall.get("name", "Unknown"),
                risk_level=risk_level,
                score_impact=score_impact,
                description=f"Firewall rule '{firewall.get('name')}' allows unrestricted access from 0.0.0.0/0",
                details={
                    "network": firewall.get("network"),
                    "source_ranges": firewall.get("source_ranges", []),
                    "allowed_ports": firewall.get("allowed_ports", [])
                },
                remediation="Restrict source ranges to specific IP addresses or networks. Remove 0.0.0.0/0 unless absolutely necessary."
            ))
        return findings

    def score_bucket_findings(self, bucket_results: List[Dict]) -> List[SecurityFinding]:
        findings = []
        if not bucket_results or bucket_results == ["Error: Permission Denied"] or isinstance(bucket_results[0], str):
            return findings

        for bucket in bucket_results:
            risk_level = self._assess_bucket_risk(bucket)
            score_impact = self._calculate_score_impact(risk_level)
            
            findings.append(SecurityFinding(
                check_type="Public Bucket",
                resource_name=bucket.get("name", "Unknown"),
                risk_level=risk_level,
                score_impact=score_impact,
                description=f"Storage bucket '{bucket.get('name')}' is publicly accessible",
                details={
                    "roles": bucket.get("roles", [])
                },
                remediation="Remove public access (allUsers/allAuthenticatedUsers) and use IAM conditions or signed URLs for controlled access."
            ))
        return findings

    def score_iam_findings(self, iam_results: List[Dict]) -> List[SecurityFinding]:
        findings = []
        if not iam_results or iam_results == ["Error: Permission Denied"] or isinstance(iam_results[0], str):
            return findings

        for iam_binding in iam_results:
            risk_level = self._assess_iam_risk(iam_binding)
            score_impact = self._calculate_score_impact(risk_level)
            
            findings.append(SecurityFinding(
                check_type="Overly Permissive IAM",
                resource_name=f"Role: {iam_binding.get('role', 'Unknown')}",
                risk_level=risk_level,
                score_impact=score_impact,
                description=f"Role '{iam_binding.get('role')}' granted to {iam_binding.get('member_count', 0)} members",
                details={
                    "role": iam_binding.get("role"),
                    "member_count": iam_binding.get("member_count", 0),
                    "members": iam_binding.get("members", [])
                },
                remediation="Follow principle of least privilege. Use custom roles with minimal permissions instead of broad roles like Owner/Editor."
            ))
        return findings

    def score_bigquery_findings(self, bigquery_results: List[Dict]) -> List[SecurityFinding]:
        findings = []
        if not bigquery_results or bigquery_results == ["Error: Permission Denied"] or isinstance(bigquery_results[0], str):
            return findings

        for dataset in bigquery_results:
            risk_level = self._assess_bigquery_risk(dataset)
            score_impact = self._calculate_score_impact(risk_level)
            
            findings.append(SecurityFinding(
                check_type="Public BigQuery Dataset",
                resource_name=dataset.get("dataset_id", "Unknown"),
                risk_level=risk_level,
                score_impact=score_impact,
                description=f"BigQuery dataset '{dataset.get('dataset_id')}' has public access",
                details={
                    "dataset_id": dataset.get("dataset_id"),
                    "project_id": dataset.get("project_id"),
                    "access_entries": dataset.get("access_entries", [])
                },
                remediation="Remove public access from BigQuery datasets. Use authorized views or service accounts for data sharing."
            ))
        return findings

    def score_cloud_functions_findings(self, cloud_functions_results: List[Dict]) -> List[SecurityFinding]:
        findings = []
        if not cloud_functions_results or cloud_functions_results == ["Error: Permission Denied"] or isinstance(cloud_functions_results[0], str):
            return findings

        for function in cloud_functions_results:
            risk_level = self._assess_cloud_function_risk(function)
            score_impact = self._calculate_score_impact(risk_level)
            
            # Join security issues for description
            issues_summary = "; ".join(function.get("security_issues", []))
            
            findings.append(SecurityFinding(
                check_type="Insecure Cloud Function",
                resource_name=function.get("name", "Unknown"),
                risk_level=risk_level,
                score_impact=score_impact,
                description=f"Cloud Function '{function.get('name')}' has security issues: {issues_summary}",
                details={
                    "location": function.get("location"),
                    "trigger_type": function.get("trigger_type"),
                    "runtime": function.get("runtime"),
                    "status": function.get("status"),
                    "security_issues": function.get("security_issues", [])
                },
                remediation="Review function IAM policies, update runtime versions, secure environment variables, and configure VPC connectors for network isolation."
            ))
        return findings

    def calculate_overall_score(self, all_findings: List[SecurityFinding]) -> SecurityScore:
        if not all_findings:
            return SecurityScore(
                total_score=100,
                max_possible_score=100,
                percentage=100.0,
                risk_level=RiskLevel.INFO,
                findings_count={},
                findings=[]
            )

        total_deductions = sum(finding.score_impact for finding in all_findings)
        total_score = max(0, 100 - total_deductions)
        
        findings_count = {}
        for level in RiskLevel:
            findings_count[level.name] = len([f for f in all_findings if f.risk_level == level])

        overall_risk = self._determine_overall_risk(all_findings)
        
        return SecurityScore(
            total_score=total_score,
            max_possible_score=100,
            percentage=total_score,
            risk_level=overall_risk,
            findings_count=findings_count,
            findings=all_findings
        )

    def _assess_firewall_risk(self, firewall: Dict) -> RiskLevel:
        allowed_ports = firewall.get("allowed_ports", [])
        
        for port_rule in allowed_ports:
            if isinstance(port_rule, str):
                if "tcp:22" in port_rule.lower() or "tcp:3389" in port_rule.lower():
                    return RiskLevel.CRITICAL
                elif "tcp:any" in port_rule.lower() or ":any" in port_rule.lower():
                    return RiskLevel.HIGH
                elif any(dangerous_port in port_rule.lower() for dangerous_port in ["80", "443", "21", "23"]):
                    return RiskLevel.MEDIUM
        
        return RiskLevel.LOW

    def _assess_bucket_risk(self, bucket: Dict) -> RiskLevel:
        roles = bucket.get("roles", [])
        
        for role in roles:
            if isinstance(role, str):
                if "allUsers" in role:
                    return RiskLevel.CRITICAL
                elif "allAuthenticatedUsers" in role:
                    return RiskLevel.HIGH
        
        return RiskLevel.MEDIUM

    def _assess_iam_risk(self, iam_binding: Dict) -> RiskLevel:
        role = iam_binding.get("role", "")
        member_count = iam_binding.get("member_count", 0)
        
        if "owner" in role.lower():
            if member_count > 10:
                return RiskLevel.CRITICAL
            elif member_count > 5:
                return RiskLevel.HIGH
            else:
                return RiskLevel.MEDIUM
        elif "editor" in role.lower():
            if member_count > 15:
                return RiskLevel.HIGH
            elif member_count > 10:
                return RiskLevel.MEDIUM
            else:
                return RiskLevel.LOW
        
        return RiskLevel.LOW

    def _assess_bigquery_risk(self, dataset: Dict) -> RiskLevel:
        access_entries = dataset.get("access_entries", [])
        
        for entry in access_entries:
            if isinstance(entry, str):
                if "allUsers" in entry:
                    return RiskLevel.CRITICAL
                elif "allAuthenticatedUsers" in entry:
                    return RiskLevel.HIGH
        
        return RiskLevel.MEDIUM

    def _assess_cloud_function_risk(self, function: Dict) -> RiskLevel:
        security_issues = function.get("security_issues", [])
        
        # Check for critical security issues
        for issue in security_issues:
            if "public access" in issue.lower() or "unauthenticated" in issue.lower():
                return RiskLevel.CRITICAL
            elif "allAuthenticatedUsers" in issue:
                return RiskLevel.HIGH
            elif "secret" in issue.lower() and "environment variable" in issue.lower():
                return RiskLevel.HIGH
        
        # Check for high risk issues
        high_risk_indicators = ["outdated runtime", "overly broad", "direct internet access"]
        for issue in security_issues:
            if any(indicator in issue.lower() for indicator in high_risk_indicators):
                return RiskLevel.HIGH
        
        # If there are security issues but not critical/high, classify as medium
        if security_issues:
            return RiskLevel.MEDIUM
        
        return RiskLevel.LOW

    def _calculate_score_impact(self, risk_level: RiskLevel) -> int:
        base_impact = {
            RiskLevel.CRITICAL: 25,
            RiskLevel.HIGH: 15,
            RiskLevel.MEDIUM: 10,
            RiskLevel.LOW: 5,
            RiskLevel.INFO: 1
        }
        return base_impact.get(risk_level, 5)

    def _determine_overall_risk(self, findings: List[SecurityFinding]) -> RiskLevel:
        if not findings:
            return RiskLevel.INFO
        
        critical_count = len([f for f in findings if f.risk_level == RiskLevel.CRITICAL])
        high_count = len([f for f in findings if f.risk_level == RiskLevel.HIGH])
        
        if critical_count > 0:
            return RiskLevel.CRITICAL
        elif high_count > 2:
            return RiskLevel.CRITICAL
        elif high_count > 0:
            return RiskLevel.HIGH
        else:
            return RiskLevel.MEDIUM

    def generate_report(self, security_score: SecurityScore) -> str:
        console = Console()
        
        # Capture console output to string
        with console.capture() as capture:
            self._generate_rich_report(console, security_score)
        
        return capture.get()
    
    def _generate_rich_report(self, console: Console, security_score: SecurityScore):
        # Header with styling
        console.print()
        console.print(
            Panel.fit(
                "[bold white]🛡️  GCP SECURITY ASSESSMENT REPORT  🛡️[/bold white]",
                style="bold blue",
                border_style="bright_blue"
            ),
            justify="center"
        )
        console.print()
        
        # Security Score Section with progress bar
        score_color = self._get_score_color(security_score.total_score)
        risk_color = self._get_risk_color(security_score.risk_level)
        
        score_table = Table(show_header=False, box=None, padding=(0, 2))
        score_table.add_column(justify="left", style="bold")
        score_table.add_column(justify="left")
        
        score_table.add_row(
            "🎯 Security Score:",
            f"[{score_color}]{security_score.total_score}/100 ({security_score.percentage:.1f}%)[/{score_color}]"
        )
        score_table.add_row(
            "⚠️  Risk Level:",
            f"[{risk_color}]{security_score.risk_level.name}[/{risk_color}]"
        )
        
        console.print(Panel(score_table, title="[bold]📊 Overall Assessment[/bold]", border_style="green"))
        console.print()
        
        # Progress bar for security score
        progress = Progress(
            TextColumn("[bold blue]Security Score Progress", justify="left"),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.1f}%"),
            expand=False,
        )
        with progress:
            task = progress.add_task("Security Score", total=100)
            progress.update(task, completed=security_score.total_score)
            console.print(progress)
        console.print()
        
        # Findings Summary with colored badges
        if security_score.findings_count:
            findings_table = Table(title="📋 Findings Summary", show_header=True, header_style="bold magenta")
            findings_table.add_column("Risk Level", style="bold", justify="center")
            findings_table.add_column("Count", justify="center")
            findings_table.add_column("Visual", justify="center")
            
            for level_name, count in security_score.findings_count.items():
                if count > 0:
                    level_enum = RiskLevel[level_name]
                    color = self._get_risk_color(level_enum)
                    emoji = self._get_risk_emoji(level_enum)
                    visual = "●" * min(count, 10)  # Max 10 dots for visual
                    findings_table.add_row(
                        f"[{color}]{emoji} {level_name}[/{color}]",
                        f"[{color}]{count}[/{color}]",
                        f"[{color}]{visual}[/{color}]"
                    )
            
            console.print(findings_table)
            console.print()
        
        # Detailed Findings
        if security_score.findings:
            console.print(Rule("[bold blue]🔍 Detailed Findings[/bold blue]"))
            console.print()
            
            for i, finding in enumerate(security_score.findings, 1):
                risk_color = self._get_risk_color(finding.risk_level)
                risk_emoji = self._get_risk_emoji(finding.risk_level)
                
                # Create finding panel
                finding_content = Table(show_header=False, box=None, padding=(0, 1))
                finding_content.add_column(style="bold", min_width=12)
                finding_content.add_column()
                
                finding_content.add_row("🏷️  Resource:", f"[cyan]{finding.resource_name}[/cyan]")
                finding_content.add_row("📝 Issue:", finding.description)
                finding_content.add_row("📉 Impact:", f"[red]-{finding.score_impact} points[/red]")
                finding_content.add_row("🔧 Fix:", f"[green]{finding.remediation}[/green]")
                
                panel_title = f"[{risk_color}]{risk_emoji} {finding.check_type} [{finding.risk_level.name}][/{risk_color}]"
                console.print(
                    Panel(
                        finding_content,
                        title=panel_title,
                        border_style=risk_color,
                        title_align="left"
                    )
                )
                console.print()
        
        # Recommendations Section
        console.print(Rule("[bold green]💡 Recommendations[/bold green]"))
        console.print()
        
        recommendations = self._get_recommendations(security_score.risk_level)
        rec_panel = Panel(
            "\n".join(recommendations),
            title="[bold]🎯 Action Items[/bold]",
            border_style=risk_color,
            padding=(1, 2)
        )
        console.print(rec_panel)
        console.print()
        
        # Footer
        console.print(
            Align.center(
                "[dim]Generated by gcpsight - GCP Security Assessment Tool[/dim]"
            )
        )
    
    def _get_score_color(self, score: int) -> str:
        if score >= 90:
            return "bright_green"
        elif score >= 75:
            return "green"
        elif score >= 60:
            return "yellow"
        elif score >= 40:
            return "orange"
        else:
            return "red"
    
    def _get_risk_color(self, risk_level: RiskLevel) -> str:
        colors = {
            RiskLevel.CRITICAL: "bright_red",
            RiskLevel.HIGH: "red",
            RiskLevel.MEDIUM: "yellow",
            RiskLevel.LOW: "green",
            RiskLevel.INFO: "blue"
        }
        return colors.get(risk_level, "white")
    
    def _get_risk_emoji(self, risk_level: RiskLevel) -> str:
        emojis = {
            RiskLevel.CRITICAL: "🚨",
            RiskLevel.HIGH: "⚠️",
            RiskLevel.MEDIUM: "⚡",
            RiskLevel.LOW: "ℹ️",
            RiskLevel.INFO: "📘"
        }
        return emojis.get(risk_level, "•")
    
    def _get_recommendations(self, risk_level: RiskLevel) -> List[str]:
        if risk_level == RiskLevel.CRITICAL:
            return [
                "🚨 [bold red]IMMEDIATE ACTION REQUIRED[/bold red] - Critical security vulnerabilities detected",
                "🔥 Address critical findings immediately to prevent potential breaches",
                "⏰ Review and patch within the next 2-4 hours",
                "📞 Consider engaging security team or external experts"
            ]
        elif risk_level == RiskLevel.HIGH:
            return [
                "⚠️  [bold orange]High priority security issues[/bold orange] require prompt attention",
                "🎯 Review and remediate findings within 24-48 hours",
                "📊 Monitor affected resources closely",
                "🔍 Consider additional security audits"
            ]
        elif risk_level == RiskLevel.MEDIUM:
            return [
                "⚡ [bold yellow]Moderate security improvements[/bold yellow] recommended",
                "📅 Plan remediation within the next week",
                "🔄 Implement regular security reviews",
                "📈 Consider security automation tools"
            ]
        else:
            return [
                "✅ [bold green]Good security posture[/bold green] with minor improvements possible",
                "🔄 Continue regular security monitoring",
                "📚 Stay updated with security best practices",
                "🎯 Consider proactive security measures"
            ]