"""
Command-line interface for working with Bernese campaigns

"""

import logging
from pathlib import Path
import json
import datetime as dt
import itertools as it
from dataclasses import (
    dataclass,
    asdict,
)
from typing import Any

import click
from click_aliases import ClickAliasedGroup  # type: ignore
from rich import print
import humanize

from ab.cli import (
    _input,
    _filter,
    about,
)
from ab import (
    configuration,
    files as _files,
)
from ab.configuration import (
    sources as _sources,
    tasks as _tasks,
)
from ab.bsw import campaign as _campaign


log = logging.getLogger(__name__)


@click.group(cls=ClickAliasedGroup, invoke_without_command=True)
@click.pass_context
def campaign(ctx: click.Context) -> None:
    """
    Create campaigns and manage campaign-specific sources and run BPE tasks.

    """
    _campaign.init_template_dir()
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# @campaign.command
# @click.argument("name", type=str)
# def info(name: str) -> None:
#     """
#     Show campaign info

#     """
#     from ab.dates import date_range

#     config = _campaign.load(name)
#     metadata = _campaign.MetaData(**config.get("metadata", {}))
#     print(metadata)
#     epoch = metadata.beg + dt.timedelta((metadata.end - metadata.beg).days // 2)
#     print(f"Dates:")
#     for date in date_range(metadata.beg, metadata.end):
#         is_epoch = "*" if date.date() == epoch else ""
#         print(
#             f"{is_epoch:1s} {date.isoformat()[:10]} {date.doy:0>3d} {date.gps_week:0>4d} {date.gps_weekday:1d}"
#         )


@campaign.command
@click.option("--verbose", "-v", is_flag=True, help="Print more details.")
def ls(verbose: bool) -> None:
    """
    List existing campaigns

    """
    log.debug("List existing campaigns ...")
    print("Existing campaigns registered in the BSW campaign list:")
    # print("\n".join(_campaign.ls(verbose)))
    campaign_infos = _campaign.ls(verbose)
    # print(json.dumps([asdict(ci) for ci in campaign_infos]))
    fstr = "{directory: <40s} {size: >10s} {template} {version} {username} {created}"
    lines = []
    for campaign_info in campaign_infos:
        if campaign_info.size > 0:
            size = humanize.naturalsize(campaign_info.size, binary=True)
        else:
            size = ""
        kwargs = {
            **asdict(campaign_info),
            **{"size": size},
        }
        lines.append(fstr.format(**kwargs))
    print("\n".join(lines))


@campaign.command
@click.argument("template", default=None, type=str, required=False)
def templates(template: str | None) -> None:
    """
    List available campaign templates or show content of given template.

    """
    if template is None:
        log.debug("List available campaign templates ...")
        print("\n".join(_campaign.available_templates()))

    else:
        log.debug(f"Show raw template {template!r} ...")
        print(_campaign.read_template(template))


@campaign.command
@click.argument("name", type=str)
@click.option(
    "-t",
    "--template",
    type=str,
    default="default",
    required=False,
    help="Template for campaign configuration If not given, the default configuration is used.",
)
@click.option(
    "-b",
    "--beg",
    type=_input.date,
    required=True,
    help=f"Format: {_input.DATE_FORMAT}",
)
@click.option(
    "-e",
    "--end",
    type=_input.date,
    required=True,
    help=f"Format: {_input.DATE_FORMAT}",
)
def create(name: str, template: str, beg: dt.date, end: dt.date) -> None:
    """
    Create a Bernese campaign with directory content based on the specified
    template and add campaign path to the list of available campaigns in the BSW
    campaign menu.

    """
    msg = f"Create campaign {name=} using {template=} with {beg=} and {end=} ..."
    print(msg)
    log.info(msg)
    _campaign.create(name, template, beg, end)


@campaign.command
@click.argument("name", type=str)
@click.option("-i", "--identifier", multiple=True, type=str, default=[], required=False)
@click.option("--verbose", "-v", is_flag=True, help="Print more details.")
def sources(
    name: str, identifier: list[str] | None = None, verbose: bool = False
) -> None:
    """
    Print the campaign-specific sources.

    """
    raw_sources = _filter.get_raw(_campaign.load(name), "sources", identifier)
    if not raw_sources:
        msg = f"No sources in campaign ..."
        log.info(msg)
        print(msg)
        return

    sources = _sources.load_all(raw_sources)

    if not verbose:
        formatted = (f"{source}" for source in sources)

    else:
        join_pairs = lambda pairs: "\n".join(
            f"{p.path_remote} -> {p.path_local}/{p.fname}" for p in pairs
        )
        formatted = (
            f"{info}{join_pairs(source.resolve())}\n"
            for (source, info) in zip(sources, formatted)
        )

    print("\n".join(formatted))


@campaign.command(name="tasks")
@click.argument("name", type=str)
@click.option("-i", "--identifier", multiple=True, type=str, default=[], required=False)
@click.option("--verbose", "-v", is_flag=True, help="Print realised task data.")
def tasks_command(name: str, identifier: list[str], verbose: bool) -> None:
    """
    Show tasks for a campaign.

    """

    raw_task_defs = _filter.get_raw(_campaign.load(name), "tasks", identifier)

    if not raw_task_defs:
        return

    task_defs = _tasks.load_all(raw_task_defs)

    if not verbose:
        for task_def in task_defs:
            print(task_def)
            print()
        return

    # Resolve permutations of defined task arguments and view them, a kind of
    # dry-run showing the input, before running anything.
    print(list(it.chain(*(task_def.tasks() for task_def in task_defs))))


@campaign.command
@click.argument("campaign_name", type=str)
@click.option("-i", "--identifier", multiple=True, type=str, default=[], required=False)
def run(campaign_name: str, identifier: list[str]) -> None:
    """
    Resolve and run all or specified campaign tasks.

    """

    raw_task_defs = _filter.get_raw(_campaign.load(name), "tasks", identifier)

    if not raw_task_defs:
        return

    # We have candidates
    about.print_versions()

    # Create all combinations and group by task definition
    task_defs = _tasks.load_all(raw_task_defs)

    # For display purposes
    # Resolve and pre-process arguments and instantiate the tasks
    hierarchy = {task_def.identifier: task_def.tasks() for task_def in task_defs}

    print("Running the following tasks in the campaign configuration file")
    sz = max(len(task_def_id) for task_def_id in hierarchy)
    print(
        "\n".join(
            f"{task_def_id: >{sz}s}: {len(tasks): >3d} unique combinations"
            for (task_def_id, tasks) in hierarchy.items()
        )
    )
    proceed = _input.prompt_proceed()
    if not proceed:
        raise SystemExit

    # At this point, we are only concerned with the tasks that are now made
    # ready to run

    # Combine all the tasks
    all_tasks = it.chain(*hierarchy.values())
    # TODO: Loop differently, so that taskdefinition descriptions can be written to the terminal/log
    for task in all_tasks:
        msg = f"Running task {task.identifier} ..."
        log.info(msg)
        print(msg)
        try:
            task.run()
            if task.result.finished:
                postfix = " [green][ done ][/]"
            else:
                postfix = " [red][ error ][/]"
                log.info(
                    f"Task {task.identifier} failed with exception ({task.result.exception}) ..."
                )
            print(postfix)
            # TODO: Log the result(ing value)?
            # print(task.result)

        except KeyboardInterrupt:
            log.info(f"Task {task.identifier} interrupted by user ...")
            log.info("Asking user to continue with remaining tasks or exit completely.")
            exit_confirmed = input(
                "Do you want to exit completely ([y]/n)"
            ).lower() in ("", "y")
            if exit_confirmed:
                log.info("User confirmed breaking execution of remaining tasks.")
                break


@campaign.command
@click.argument("campaign_name", type=str)
def clean(campaign_name: str) -> None:
    """
    Delete content in specified campaign directories.

    """
    # Are there any directories specified?
    c = _campaign.just_load(campaign_name)
    paths = c.get("clean")

    if not paths:
        return

    dirs = _campaign.subdirectories(campaign_name)

    # Take those selected
    existing_chosen = [path for (name, path) in dirs.items() if name in paths]

    print("Deleting content in the following directories:")
    print("\n".join(existing_chosen))
    proceed = _input.prompt_proceed()
    if not proceed:
        raise SystemExit

    # And delete their contents, but not the directories
    for path in existing_chosen:
        _files.delete_directory_content(path)
