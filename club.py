"""club: A small counterpart CLI for Google Apps Script's clasp."""

import copy
import json
import re
import subprocess
from pathlib import Path

import click

CLUB_KEY = "__club__"
PROJECT_ID_VALIDATOR = re.compile(r"[a-zA-Z0-9-_]{57}")


def read_manifest() -> dict:
    """Read the manifest file and return the parsed JSON."""
    with open(Path.cwd() / ".clasp.json", "r") as f:
        return json.load(f)


def write_manifest(manifest: dict):
    """Write the manifest file with the given JSON."""
    with open(Path.cwd() / ".clasp.json", "w") as f:
        json.dump(manifest, f, indent=2)


def set_club_key(manifest: dict, name: str, project_id: str):
    if CLUB_KEY not in manifest:
        manifest[CLUB_KEY] = {}
    manifest[CLUB_KEY][name] = project_id


def push(name: str, manifest: dict = None):
    manifest = manifest or read_manifest()
    if name not in manifest[CLUB_KEY]:
        raise click.BadParameter(
            f"Remote {name} does not exist.",
            param_hint="name",
        )
    manifest_backup = copy.deepcopy(manifest)
    manifest["scriptId"] = manifest[CLUB_KEY][name]
    write_manifest(manifest)
    click.echo(f"Pushing to {name}...")
    try:
        subprocess.run(["clasp", "push"], check=True)
    except subprocess.CalledProcessError:
        write_manifest(manifest_backup)
        raise
    write_manifest(manifest_backup)


@click.group()
def cli():
    """A small counterpart CLI for Google Apps Script's clasp."""
    pass


@cli.command(name="set")
@click.argument(
    "name",
    type=str,
    required=True,
)
@click.argument(
    "project_id",
    type=str,
    required=True,
)
def set_remote_cmd(name: str, project_id: str):
    """Add a remote destination for the project in the current directory."""
    if not PROJECT_ID_VALIDATOR.match(project_id):
        raise click.BadParameter(
            f"Invalid project ID: {project_id}",
            param_hint="project_id",
        )
    if name == "all":
        raise click.BadParameter(
            "Cannot set remote named 'all'.",
            param_hint="name",
        )
    manifest = read_manifest()
    set_club_key(manifest, name, project_id)
    write_manifest(manifest)


@cli.command(name="remove")
@click.argument(
    "name",
    type=str,
    required=True,
)
def remove_remote_cmd(name: str):
    """Remove a remote destination for the project in the current directory."""
    manifest = read_manifest()
    if name not in manifest[CLUB_KEY]:
        raise click.BadParameter(
            f"Remote {name} does not exist.",
            param_hint="name",
        )
    del manifest[CLUB_KEY][name]
    write_manifest(manifest)


@cli.command(name="push")
@click.argument(
    "name",
    type=str,
    required=True,
)
def push_cmd(name: str):
    """Push the project in the current directory to the remote destination. If "all" is given, push to all remotes."""
    manifest = read_manifest()
    names = [name] if name != "all" else list(manifest[CLUB_KEY].keys())
    for name in names:
        push(name, manifest)


if __name__ == "__main__":
    cli()
