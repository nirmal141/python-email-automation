import logging
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table

from .config import Settings
from .engine import EmailCampaign
from .models import CampaignConfig, EmailTemplate

app = typer.Typer(
    name="email-automation",
    help="Professional bulk email CLI powered by Pydantic and SMTP.",
    add_completion=False,
)
console = Console()


def _load_settings() -> Settings:
    try:
        return Settings()  # type: ignore[call-arg]
    except Exception as exc:
        console.print(f"[red]Failed to load settings:[/red] {exc}")
        console.print("Run [bold]email-automation init[/bold] to create a .env file.")
        raise typer.Exit(1)


@app.command()
def init() -> None:
    """Interactively create a .env configuration file."""
    env_path = Path(".env")
    if env_path.exists():
        overwrite = typer.confirm(".env already exists. Overwrite?", default=False)
        if not overwrite:
            raise typer.Exit()

    console.print("[bold]Email Automation Setup[/bold]\n")

    smtp_host = typer.prompt("SMTP host", default="smtp.gmail.com")
    smtp_port = typer.prompt("SMTP port", default=587, type=int)
    smtp_username = typer.prompt("SMTP username (email)")
    smtp_password = typer.prompt("SMTP password (app password)", hide_input=True)
    sender_name = typer.prompt("Sender display name")
    sender_email = typer.prompt("Sender email address", default=smtp_username)
    delay = typer.prompt("Delay between emails (seconds)", default=2.0, type=float)

    lines = [
        f"EA_SMTP_HOST={smtp_host}",
        f"EA_SMTP_PORT={smtp_port}",
        f"EA_SMTP_USERNAME={smtp_username}",
        f"EA_SMTP_PASSWORD={smtp_password}",
        f"EA_SENDER_NAME={sender_name}",
        f"EA_SENDER_EMAIL={sender_email}",
        f"EA_EMAIL_DELAY_SECONDS={delay}",
        "EA_LOG_LEVEL=INFO",
    ]
    env_path.write_text("\n".join(lines) + "\n")
    console.print(f"\n[green]Saved configuration to {env_path}[/green]")


@app.command()
def test() -> None:
    """Test the SMTP connection using current settings."""
    settings = _load_settings()

    from .smtp import SMTPConnection

    console.print("Testing SMTP connection ...")
    conn = SMTPConnection(settings)
    if conn.test_connection():
        console.print("[green]Connection successful![/green]")
    else:
        console.print("[red]Connection failed.[/red]")
        raise typer.Exit(1)


@app.command()
def preview(
    csv_path: Path = typer.Argument(..., help="Path to the contacts CSV file."),
) -> None:
    """Preview contacts and a sample email from a CSV file."""
    settings = _load_settings()
    campaign = EmailCampaign(settings)

    contacts = campaign.load_contacts(csv_path)

    table = Table(title=f"Contacts ({len(contacts)} total)")
    table.add_column("#", style="dim")
    table.add_column("Company")
    table.add_column("Role")
    table.add_column("Email")
    table.add_column("Name")

    for i, c in enumerate(contacts, 1):
        table.add_row(
            str(i),
            c.company_name,
            c.role,
            c.recruiter_email,
            c.recruiter_first_name or "—",
        )

    console.print(table)

    if contacts:
        sample = campaign.create_email(contacts[0])
        console.print("\n[bold]Sample email (first contact):[/bold]")
        console.print(f"  Subject: {sample.subject}")
        console.print(f"  Body:\n{sample.text_body}")


@app.command()
def send(
    csv_path: Path = typer.Argument(..., help="Path to the contacts CSV file."),
    test_mode: bool = typer.Option(True, "--test-mode/--live", help="Dry-run without sending."),
    delay: float = typer.Option(None, "--delay", help="Override delay between emails (seconds)."),
    resume: Path = typer.Option(None, "--resume", help="Path to resume/attachment file."),
) -> None:
    """Run an email campaign from a CSV file."""
    settings = _load_settings()

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    campaign = EmailCampaign(settings)

    effective_delay = delay if delay is not None else settings.email_delay_seconds
    config = CampaignConfig(
        csv_path=csv_path,
        test_mode=test_mode,
        delay_seconds=effective_delay,
        resume_path=resume,
    )

    mode_label = "[yellow]TEST MODE[/yellow]" if test_mode else "[red]LIVE[/red]"
    console.print(f"Starting campaign ({mode_label}) ...")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        contacts = campaign.load_contacts(csv_path)
        task = progress.add_task("Sending emails", total=len(contacts))

        def on_progress(current: int, total: int) -> None:
            progress.update(task, completed=current)

        result = campaign.run(config, on_progress=on_progress)

    console.print()
    result_table = Table(title="Campaign Results")
    result_table.add_column("Metric", style="bold")
    result_table.add_column("Value")
    result_table.add_row("Total", str(result.total))
    result_table.add_row("Sent", f"[green]{result.sent}[/green]")
    result_table.add_row("Failed", f"[red]{result.failed}[/red]" if result.failed else "0")
    result_table.add_row("Duration", f"{result.duration_seconds:.1f}s")

    console.print(result_table)

    if result.failed_emails:
        console.print(f"\n[red]Failed emails:[/red] {', '.join(result.failed_emails)}")
