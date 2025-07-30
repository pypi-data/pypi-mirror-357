# SPDX-License-Identifier: GPL-3.0-or-later
"""Utility functions for ZebraStream CLI."""
import json
import typer
from rich import print
from api_client.models.http_validation_error import HTTPValidationError

def status_is_success(status_code):
    """
    Returns True if the status code is in the 2xx range.
    """
    return 200 <= int(status_code) < 300

def print_exit_api_error(response):
    if status_is_success(response.status_code):
        return
    code = getattr(response, "status_code", None)
    phrase = getattr(code, "phrase", "")
    print(f"[red]API error {code} ({phrase})[/red]")
    parsed = getattr(response, "parsed", None)
    if isinstance(parsed, HTTPValidationError):
        for err in parsed.detail:
            loc = ".".join(map(str, err.loc))
            print(f"[red]- {loc} - {err.msg}[/red]")
    elif hasattr(response, "content"):
        print(f"[red]- {json.loads(response.content).get('detail')}[/red]")  # Assuming JSON response (API dependency)
    else:
        print(f"[red]{response}\n[/red]")
    raise typer.Exit(1)
