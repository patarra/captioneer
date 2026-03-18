#!/usr/bin/env python3
"""Shared Rich console and UI helpers for captioneer."""

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.text import Text

console = Console()


def print_header(title: str, subtitle: str) -> None:
    content = Text(justify="center")
    content.append(title + "\n", style="bold cyan")
    content.append(subtitle, style="dim")
    console.print(Panel(content, border_style="cyan", padding=(0, 2)))


def print_step(n: int, total: int, label: str) -> None:
    console.print(f"\n[bold cyan][{n}/{total}][/] {label}")


def print_done(path: str) -> None:
    console.print(f"\n[bold green]✓ Done[/] → [cyan]{path}[/]")


def print_info(label: str, value: str) -> None:
    console.print(f"  [dim]{label}:[/] {value}")


def make_progress(description: str) -> Progress:
    """Return a Rich Progress configured for captioneer output."""
    return Progress(
        SpinnerColumn(),
        TextColumn(f"[cyan]{description:<14}[/]"),
        BarColumn(bar_width=32),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    )
