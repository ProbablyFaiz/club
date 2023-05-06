"""club: A small counterpart CLI for Google Apps Script's clasp."""

import copy
import json
import os
import re
import subprocess
from pathlib import Path

import click


MANIFEST_NAME = ".clasp.json"
CLUB_KEY = "__club__"
PROJECT_ID_VALIDATOR = re.compile(r"[a-zA-Z0-9-_]{57}")
DEFAULT_PROJECT_NAME = "main"


def club_wd() -> Path:
    """Return the path to the working directory of club."""
    return os.getenv("CLUB_DIR", Path.cwd())


def club_manifest() -> Path:
    return club_wd() / MANIFEST_NAME


def read_manifest() -> dict:
    """Read the manifest file and return the parsed JSON."""
    with open(club_manifest(), "r") as f:
        return json.load(f)


def write_manifest(manifest: dict):
    """Write the manifest file with the given JSON."""
    with open(club_manifest(), "w") as f:
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


@cli.command(name="init")
def init_cmd():
    """Initialize the current directory as a club project."""
    if not club_manifest().exists():
        click.echo(f"Creating {club_manifest()}...")
        with open(club_manifest(), "w") as f:
            json.dump(
                {
                    "scriptId": "",
                    "parentId": [],
                },
                f,
                indent=2,
            )
    manifest = read_manifest()
    if CLUB_KEY in manifest:
        raise click.UsageError(
            "This directory is already a club project.",
        )
    manifest[CLUB_KEY] = {}
    if manifest.get("scriptId"):
        click.echo(f"Setting '{DEFAULT_PROJECT_NAME}' remote to current script ID...")
        manifest[CLUB_KEY][DEFAULT_PROJECT_NAME] = manifest["scriptId"]
    write_manifest(manifest)
    click.echo(f"Initialized club project in {club_wd()}.")


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


@click.command(name="rename")
@click.argument(
    "old_name",
    type=str,
    required=True,
)
@click.argument(
    "new_name",
    type=str,
    required=True,
)
def rename_remote_cmd(old_name: str, new_name: str):
    """Rename a remote destination for the project in the current directory."""
    manifest = read_manifest()
    if old_name not in manifest[CLUB_KEY]:
        raise click.BadParameter(
            f"Remote {old_name} does not exist.",
            param_hint="old_name",
        )
    if old_name == DEFAULT_PROJECT_NAME and len(manifest[CLUB_KEY]) > 1:
        click.confirm(
            f"Remote '{DEFAULT_PROJECT_NAME}' is the default destination for 'club push'. Renaming it will require you to specify a destination when pushing. Continue?",
            abort=True,
        )
    if new_name == "all":
        raise click.BadParameter(
            "Cannot rename remote to 'all'.",
            param_hint="new_name",
        )
    if new_name in manifest[CLUB_KEY]:
        click.confirm(
            f"Remote {new_name} already exists (project ID: {manifest[CLUB_KEY][new_name]}). Overwrite?",
            abort=True,
        )
    manifest[CLUB_KEY][new_name] = manifest[CLUB_KEY][old_name]
    if old_name != new_name:
        del manifest[CLUB_KEY][old_name]
    write_manifest(manifest)


@cli.command(name="push")
@click.argument(
    "names",
    type=str,
    required=False,
)
def push_cmd(names: str):
    """Push the project in the current directory to the remote destination(s), comma-separated. If "all" is given, push to all remotes."""
    manifest = read_manifest()
    if CLUB_KEY not in manifest:
        raise click.UsageError(
            "This directory is not set up as a club project. Run `club init` to initialize it with default settings or set a remote using `club set`.",
        )
    possible_names = list(manifest[CLUB_KEY].keys())
    if not names:
        if DEFAULT_PROJECT_NAME in possible_names:
            names = DEFAULT_PROJECT_NAME
        elif len(possible_names) == 1:
            names = possible_names[0]
        else:
            raise click.BadParameter(
                "No default remote is set and more than one exists. Please specify a remote to push to, or rename one of your remotes: `club rename [name] main`.",
                param_hint="names",
            )
    names = names.split(",") if names != "all" else list(manifest[CLUB_KEY].keys())
    for name in names:
        push(name, manifest)


if __name__ == "__main__":
    cli()
