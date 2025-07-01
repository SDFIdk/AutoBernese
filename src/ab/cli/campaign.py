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
    _output,
    _filter,
    _arguments,
    _options,
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
from ab.dates import GPSDate


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
# @_arguments.name
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
@_options.verbose
def ls(verbose: bool) -> None:
    """
    List existing campaigns

    """
    log.debug("List existing campaigns ...")
    print("Existing campaigns registered in the BSW campaign list:")
    campaign_infos = _campaign.ls(verbose)
    fstr = "{directory: <40s} {size: >10s} {template} {version} {username} {created}"
    lines = []
    registered_dirs = []
    for campaign_info in campaign_infos:
        registered_dirs.append(Path(campaign_info.directory))
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

    if verbose:
        project_dir = _campaign.project_dir()
        all_dirs = list(project_dir.glob("*/"))
        all_dirs_and_files = project_dir.glob("*")

        extraneous_dirs = sorted(set(all_dirs) - set(registered_dirs))
        extraneous_files = sorted(set(all_dirs_and_files) - set(all_dirs))

        print()
        print("All directories in the campaign directory container:")
        print("\n".join(str(path) for path in extraneous_dirs))
        print()
        print("All extraneous files in the campaign directory container:")
        print("\n".join(str(path) for path in extraneous_files))


@campaign.command
@_arguments.template
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
@_arguments.name
@_options.template
@_options.gps_week
@_options.beg
@_options.end
def create(
    name: str,
    template: str,
    gps_week: int | None = None,
    beg: dt.date | None = None,
    end: dt.date | None = None,
) -> None:
    """
    Create a Bernese campaign with directory content based on the specified
    template and add campaign path to the list of available campaigns in the BSW
    campaign menu.

    """
    if _campaign.dir_exists(name):
        raise SystemExit(f"Campaign {name} already exists ...")

    chosen_input = ""

    if gps_week is not None:
        chosen_input += f"{gps_week=} giving "
        beg = GPSDate.from_gps_week(gps_week)
        end = beg + dt.timedelta(days=7)

    if beg is None or end is None:
        msg = f"Expected campaign interval given as either GPS week or start and end dates. ..."
        log.error(msg)
        raise SystemExit(msg)

    chosen_input += f"{beg.isoformat()[:10]} and {end.isoformat()[:10]}"

    msg = f"Create campaign {name=} using {template=} with {chosen_input} ..."
    print(msg)
    log.info(msg)

    _campaign.create(name, template, beg, end)


@campaign.command
@_arguments.name
@_options.identifiers
@_options.exclude
@_options.verbose
def sources(
    name: str,
    identifiers: list[str] | None = None,
    exclude: list[str] | None = None,
    verbose: bool = False,
) -> None:
    """
    Print the campaign-specific sources.

    """
    raw_sources = _filter.get_raw(_campaign.load(name), "sources", identifiers, exclude)
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


@campaign.command
@_arguments.name
@_options.identifiers
@_options.exclude
@_options.verbose
def tasks(
    name: str,
    identifiers: list[str] | None = None,
    exclude: list[str] | None = None,
    verbose: bool = False,
) -> None:
    """
    Show tasks for a campaign.

    """
    raw_task_defs = _filter.get_raw(_campaign.load(name), "tasks", identifiers, exclude)
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
@_arguments.name
@_options.identifiers
@_options.exclude
@_options.yes
def run(
    name: str,
    identifiers: list[str] | None = None,
    exclude: list[str] | None = None,
    yes: bool = False,
) -> None:
    """
    Resolve and run all or specified campaign tasks.

    """

    raw_task_defs = _filter.get_raw(_campaign.load(name), "tasks", identifiers, exclude)

    if not raw_task_defs:
        msg = "No selection to run ..."
        log.info(msg)
        print(msg)
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
        print(msg, end=" ")
        try:
            task.run()
            result = task.result
            log.info(f"Task {task.identifier} returned: {result.return_value!r} ...")
            if result.finished and result.exception is None:
                postfix = "[green][ done ][/]"
            else:
                postfix = "[red][ error ][/]"
                log.info(
                    f"Task {task.identifier} failed with exception ({result.exception}) ..."
                )
            print(postfix)
            if result.return_value:
                print(_output.title_divide("Task return value"))
                print(result.return_value)
                print(_output.divide())

        except KeyboardInterrupt:
            log.info(f"Task {task.identifier} interrupted by user ...")
            log.info(f"Stopping the rest of the task execution. ...")
            break


@campaign.command
@_arguments.name
@_options.yes
def clean(name: str, yes: bool = False) -> None:
    """
    Delete content in specified campaign directories.

    """
    # Are there any directories specified?
    c = _campaign.just_load(name)
    paths = c.get("clean")

    if not paths:
        return

    dirs = _campaign.subdirectories(name)

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


@campaign.command
@_arguments.names
def register(names: tuple[str]) -> None:
    """
    Register existing campaign directory in Bernese-campaign menu.

    Adds the campaign located in the camapgin directory to the menu file.

    """
    if not names:
        return

    for name in names:
        path = _campaign.campaign_dir(name)
        if not path.is_dir():
            msg = f"Skipping {path} - Campaign directory does not exist ..."
            log.warn(msg)
            print(msg)
            continue
        msg = f"Adding {path} to Bernese-campaign menu"
        log.info(msg)
        print(msg)
        _campaign.add_campaign_to_bsw_menu(name)


@campaign.command
@_arguments.names
def unregister(names: tuple[str]) -> None:
    """
    Unregister campaign in Bernese-campaign menu.

    Removes campaign name from Bernese-campaign menu.

    The campaign directory itself is untouched and does not need to exist.

    """
    if not names:
        return

    for name in names:
        path = _campaign.campaign_dir(name)
        msg = f"Removing {path} from Bernese-campaign menu"
        log.info(msg)
        print(msg)
        _campaign.remove_campaign_from_bsw_menu(name)
