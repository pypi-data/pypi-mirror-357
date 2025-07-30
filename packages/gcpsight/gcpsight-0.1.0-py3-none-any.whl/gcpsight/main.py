# main.py
import click
import os
import json # Added to pretty-print JSON
from dotenv import load_dotenv
from . import gcp_scanner  # Our module for GCP checks
from . import gemini_processor # Our module for Gemini interaction
from . import security_scorer # Our module for security scoring
from tabulate import tabulate # Added for table formatting
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

load_dotenv() # Load environment variables from .env

@click.group()
def cli():
    """A CLI tool for GCP Security Analysis powered by Gemini."""
    pass

@cli.command()
@click.option('--project-id', required=True, help='The GCP project ID to scan.')
def list_open_firewalls(project_id):
    """Checks for firewall rules open to the internet (0.0.0.0/0)."""
    console = Console()
    console.print(f"[bold blue]🔍 Checking open firewall rules for project[/bold blue] [cyan]{project_id}[/cyan]...")
    
    results = gcp_scanner.check_open_firewalls(project_id)
    if results and not isinstance(results[0], str):
        table = Table(title="🔥 Open Firewall Rules", show_header=True, header_style="bold red")
        table.add_column("Name", style="bold yellow")
        table.add_column("Network", style="cyan")
        table.add_column("Source Ranges", style="red")
        table.add_column("Allowed Ports", style="green")
        
        for firewall in results:
            table.add_row(
                firewall.get("name", "Unknown"),
                firewall.get("network", "Unknown"),
                ", ".join(firewall.get("source_ranges", [])),
                ", ".join(firewall.get("allowed_ports", []))
            )
        console.print(table)
    else:
        console.print("[green]✅ No open firewall rules found or an error occurred.[/green]")

@cli.command()
@click.option('--project-id', required=True, help='The GCP project ID to scan.')
def check_public_buckets(project_id):
    """Checks for publicly accessible GCS buckets."""
    console = Console()
    console.print(f"[bold blue]🔍 Checking public buckets for project[/bold blue] [cyan]{project_id}[/cyan]...")
    
    results = gcp_scanner.check_public_buckets(project_id)
    if results and not isinstance(results[0], str):
        table = Table(title="🪣 Public Storage Buckets", show_header=True, header_style="bold red")
        table.add_column("Bucket Name", style="bold yellow")
        table.add_column("Public Roles", style="red")
        
        for bucket in results:
            table.add_row(
                bucket.get("name", "Unknown"),
                "\n".join(bucket.get("roles", []))
            )
        console.print(table)
    else:
        console.print("[green]✅ No public buckets found or an error occurred.[/green]")

@cli.command()
@click.option('--project-id', required=True, help='The GCP project ID to scan.')
def check_overly_permissive_iam_roles(project_id):
    """Checks for IAM policies that grant overly permissive roles to a wide range of members."""
    console = Console()
    console.print(f"[bold blue]🔍 Checking overly permissive IAM roles for project[/bold blue] [cyan]{project_id}[/cyan]...")
    
    results = gcp_scanner.check_overly_permissive_iam_roles(project_id)
    if results and not isinstance(results[0], str):
        table = Table(title="👥 Overly Permissive IAM Roles", show_header=True, header_style="bold red")
        table.add_column("Role", style="bold yellow")
        table.add_column("Member Count", style="red", justify="center")
        table.add_column("Members", style="cyan")
        
        for iam_binding in results:
            members_display = "\n".join(iam_binding.get("members", [])[:5])  # Show first 5 members
            if len(iam_binding.get("members", [])) > 5:
                members_display += f"\n... and {len(iam_binding.get('members', [])) - 5} more"
            
            table.add_row(
                iam_binding.get("role", "Unknown"),
                str(iam_binding.get("member_count", 0)),
                members_display
            )
        console.print(table)
    else:
        console.print("[green]✅ No overly permissive IAM roles found or an error occurred.[/green]")

@cli.command()
@click.option('--project-id', required=True, help='The GCP project ID to scan.')
def check_public_bigquery_datasets(project_id):
    """Checks for BigQuery datasets with public access."""
    console = Console()
    console.print(f"[bold blue]🔍 Checking public BigQuery datasets for project[/bold blue] [cyan]{project_id}[/cyan]...")
    
    results = gcp_scanner.check_public_bigquery_datasets(project_id)
    if results and not isinstance(results[0], str):
        table = Table(title="📊 Public BigQuery Datasets", show_header=True, header_style="bold red")
        table.add_column("Dataset ID", style="bold yellow")
        table.add_column("Project ID", style="cyan")
        table.add_column("Access Entries", style="red")
        
        for dataset in results:
            table.add_row(
                dataset.get("dataset_id", "Unknown"),
                dataset.get("project_id", "Unknown"),
                "\n".join(dataset.get("access_entries", []))
            )
        console.print(table)
    else:
        console.print("[green]✅ No public BigQuery datasets found or an error occurred.[/green]")

@cli.command()
@click.option('--project-id', required=True, help='The GCP project ID to scan.')
def check_insecure_cloud_functions(project_id):
    """Checks for Cloud Functions with security misconfigurations."""
    console = Console()
    console.print(f"[bold blue]🔍 Checking insecure Cloud Functions for project[/bold blue] [cyan]{project_id}[/cyan]...")
    
    results = gcp_scanner.check_insecure_cloud_functions(project_id)
    if results and not isinstance(results[0], str):
        table = Table(title="⚡ Insecure Cloud Functions", show_header=True, header_style="bold red")
        table.add_column("Function Name", style="bold yellow")
        table.add_column("Location", style="cyan")
        table.add_column("Trigger Type", style="blue")
        table.add_column("Runtime", style="green")
        table.add_column("Security Issues", style="red")
        
        for function in results:
            issues_display = "\n".join(function.get("security_issues", []))
            
            table.add_row(
                function.get("name", "Unknown"),
                function.get("location", "Unknown"),
                function.get("trigger_type", "Unknown"),
                function.get("runtime", "Unknown"),
                issues_display
            )
        console.print(table)
    else:
        console.print("[green]✅ No insecure Cloud Functions found or an error occurred.[/green]")

@cli.command()
@click.option('--project-id', required=True, help='The GCP project ID to run all checks on.')
def run_all_checks(project_id):
    """Runs all available security checks on the specified project."""
    console = Console()
    console.print(f"[bold green]🚀 Running all security checks for project[/bold green] [cyan]{project_id}[/cyan]")
    console.print()
    
    list_open_firewalls.callback(project_id)
    console.print()
    check_public_buckets.callback(project_id)
    console.print()
    check_overly_permissive_iam_roles.callback(project_id)
    console.print()
    check_public_bigquery_datasets.callback(project_id)
    console.print()
    check_insecure_cloud_functions.callback(project_id)
    console.print()
    
    console.print(f"[bold green]✅ All checks completed for project[/bold green] [cyan]{project_id}[/cyan]")

@cli.command()
@click.option('--project-id', required=True, help='The GCP project ID to assess.')
@click.option('--output-format', type=click.Choice(['table', 'json', 'report']), default='report', help='Output format for the security assessment.')
def security_assessment(project_id, output_format):
    """Runs comprehensive security assessment with scoring and risk analysis."""
    click.echo(f"=== Running Security Assessment for project {project_id} ===")
    
    scorer = security_scorer.SecurityScorer()
    all_findings = []
    
    # Run all security checks and collect findings
    click.echo("Checking firewall rules...")
    firewall_results = gcp_scanner.check_open_firewalls(project_id)
    firewall_findings = scorer.score_firewall_findings(firewall_results)
    all_findings.extend(firewall_findings)
    
    click.echo("Checking public buckets...")
    bucket_results = gcp_scanner.check_public_buckets(project_id)
    bucket_findings = scorer.score_bucket_findings(bucket_results)
    all_findings.extend(bucket_findings)
    
    click.echo("Checking IAM roles...")
    iam_results = gcp_scanner.check_overly_permissive_iam_roles(project_id)
    iam_findings = scorer.score_iam_findings(iam_results)
    all_findings.extend(iam_findings)
    
    click.echo("Checking BigQuery datasets...")
    bigquery_results = gcp_scanner.check_public_bigquery_datasets(project_id)
    bigquery_findings = scorer.score_bigquery_findings(bigquery_results)
    all_findings.extend(bigquery_findings)
    
    click.echo("Checking Cloud Functions...")
    cloud_functions_results = gcp_scanner.check_insecure_cloud_functions(project_id)
    cloud_functions_findings = scorer.score_cloud_functions_findings(cloud_functions_results)
    all_findings.extend(cloud_functions_findings)
    
    # Calculate overall security score
    security_score = scorer.calculate_overall_score(all_findings)
    
    # Output results based on format
    if output_format == 'json':
        # Convert to JSON-serializable format
        json_output = {
            "project_id": project_id,
            "security_score": security_score.total_score,
            "percentage": security_score.percentage,
            "risk_level": security_score.risk_level.name,
            "findings_summary": security_score.findings_count,
            "findings": [
                {
                    "check_type": f.check_type,
                    "resource_name": f.resource_name,
                    "risk_level": f.risk_level.name,
                    "score_impact": f.score_impact,
                    "description": f.description,
                    "details": f.details,
                    "remediation": f.remediation
                }
                for f in security_score.findings
            ]
        }
        click.echo(json.dumps(json_output, indent=2))
    
    elif output_format == 'table':
        console = Console()
        
        # Security Score Summary Table
        summary_table = Table(title="🛡️  Security Assessment Summary", show_header=True, header_style="bold magenta")
        summary_table.add_column("Metric", style="bold cyan", justify="left")
        summary_table.add_column("Value", justify="left")
        
        score_color = scorer._get_score_color(security_score.total_score)
        risk_color = scorer._get_risk_color(security_score.risk_level)
        
        summary_table.add_row(
            "🎯 Security Score", 
            f"[{score_color}]{security_score.total_score}/100 ({security_score.percentage:.1f}%)[/{score_color}]"
        )
        summary_table.add_row(
            "⚠️  Risk Level", 
            f"[{risk_color}]{security_score.risk_level.name}[/{risk_color}]"
        )
        summary_table.add_row(
            "📊 Total Findings", 
            f"[bold]{len(security_score.findings)}[/bold]"
        )
        
        console.print(summary_table)
        console.print()
        
        # Findings Details Table
        if security_score.findings:
            findings_table = Table(title="🔍 Detailed Security Findings", show_header=True, header_style="bold blue")
            findings_table.add_column("Check Type", style="bold", justify="left")
            findings_table.add_column("Resource", style="cyan", justify="left")
            findings_table.add_column("Risk Level", justify="center")
            findings_table.add_column("Score Impact", style="red", justify="center")
            
            for finding in security_score.findings:
                risk_color = scorer._get_risk_color(finding.risk_level)
                risk_emoji = scorer._get_risk_emoji(finding.risk_level)
                
                findings_table.add_row(
                    finding.check_type,
                    finding.resource_name,
                    f"[{risk_color}]{risk_emoji} {finding.risk_level.name}[/{risk_color}]",
                    f"[red]-{finding.score_impact}[/red]"
                )
            
            console.print(findings_table)
    
    else:  # report format (default)
        report = scorer.generate_report(security_score)
        click.echo(report)

# This is where the Gemini magic happens
@cli.command()
@click.option('--project-id', required=True, help='The GCP project ID for context.')
@click.argument('query', type=str)
def ask(project_id, query):
    """Ask a security question in natural language."""
    click.echo(f"Processing your query: '{query}' for project {project_id}")

    # 1. Define available actions/commands the tool *actually* knows how to perform
    available_actions = {
        "list_open_firewalls": "Checks for firewall rules open to the internet (0.0.0.0/0).",
        "check_public_buckets": "Checks for publicly accessible GCS buckets.",
        "check_overly_permissive_iam_roles": "Checks for IAM policies that grant overly permissive roles to a wide range of members.",
        "check_public_bigquery_datasets": "Checks for BigQuery datasets with public access.",
        "check_insecure_cloud_functions": "Checks for Cloud Functions with security misconfigurations.",
        "run_all_checks": "Runs all available security checks on the specified project.",
        "security_assessment": "Runs comprehensive security assessment with scoring and risk analysis."
    }

    # 2. Ask Gemini to map the query to an action
    action_name = gemini_processor.get_suggested_action(query, available_actions)

    click.echo(f"Gemini suggested action: {action_name}")

    # 3. Execute the corresponding action if recognized
    if action_name == "list_open_firewalls":
        list_open_firewalls.callback(project_id)
    elif action_name == "check_public_buckets":
        check_public_buckets.callback(project_id)
    elif action_name == "check_overly_permissive_iam_roles":
        check_overly_permissive_iam_roles.callback(project_id)
    elif action_name == "check_public_bigquery_datasets":
        check_public_bigquery_datasets.callback(project_id)
    elif action_name == "check_insecure_cloud_functions":
        check_insecure_cloud_functions.callback(project_id)
    elif action_name == "run_all_checks":
        run_all_checks.callback(project_id)
    elif action_name == "security_assessment":
        security_assessment.callback(project_id, "report")
    elif action_name == "UNKNOWN":
        click.echo("Sorry, I couldn't map your query to a known action.")
    else:
        click.echo(f"Action '{action_name}' is not implemented yet.")


if __name__ == '__main__':
    cli()