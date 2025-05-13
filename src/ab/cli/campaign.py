import logging
from pathlib import Path
import json
import datetime as dt
from dataclasses import (
    dataclass,
    asdict,
)

import click
from click_aliases import ClickAliasedGroup  # type: ignore
from rich import print
import humanize

from ab.cli import (
    about,
    _input,
)
from ab import (
    configuration,
    # dates,
    task as _task,
)
from ab.bsw import campaign as _campaign
from ab.data import source as _source


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
#     for date in date_range(metadata.beg, metadata.end, transformer=dates.GPSDate):
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
        print(_campaign.load_template(template))


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
@click.option("--verbose", "-v", is_flag=True, help="Print more details.")
def sources(name: str, verbose: bool = False) -> None:
    """
    Print the campaign-specific sources.

    """
    sources: list[_source.Source] | None = _campaign.load(name).get("sources", [])

    if not sources:
        msg = f"No sources found"
        print(msg)
        log.info(msg)
        return

    formatted = (
        f"""\
{source.identifier=}
{source.url=}
{source.destination=}
{source.protocol=}
"""
        for source in sources
    )

    if verbose:
        join = lambda pairs: "\n".join(
            f"{p.path_remote} -> {p.path_local}/{p.fname}" for p in pairs
        )
        formatted = (
            f"{info}{join(source.resolve())}\n"
            for (source, info) in zip(sources, formatted)
        )

    print("\n".join(sorted(formatted)))


@campaign.command
@click.argument("name", type=str)
@click.option("--verbose", "-v", is_flag=True, help="Print realised task data.")
def tasks(name: str, verbose: bool) -> None:
    """
    Show tasks for a campaign.

    """
    tasks: list[_task.TaskDefinition] | None = _campaign.load(name).get("tasks")

    if tasks is None:
        msg = f"No tasks found"
        print(msg)
        log.info(msg)
        return

    if not verbose:
        for task in tasks:
            print(task)
            print()
        return

    for task in tasks:
        for resolved in task.resolve():
            print(json.dumps(resolved, indent=2))
            print()


@campaign.command
@click.argument("campaign_name", type=str)
@click.option("-i", "--identifier", multiple=True, type=str, default=[], required=False)
def run(campaign_name: str, identifier: list[str]) -> None:
    """
    Resolve and run all or specified campaign tasks.

    """
    try:
        tasks: list[_task.TaskDefinition] | None = _campaign.load(campaign_name).get(
            "tasks"
        )
    except RuntimeError as e:
        print(e)
        raise SystemExit

    if tasks is None:
        msg = f"No tasks found"
        print(msg)
        log.info(msg)
        return

    about.print_versions()

    if len(identifier) > 0:
        tasks = [task for task in tasks if task.identifier in identifier]

    print("Running the following tasks in the campaign configuration file")
    sz = max(len(task.identifier) for task in tasks)
    print(
        "\n".join(
            f"{task.identifier: >{sz}s}: {len(task.runners()): >3d} unique combinations"
            for task in tasks
        )
    )
    proceed = input("Proceed (y/[n]): ").lower() == "y"
    if not proceed:
        raise SystemExit

    runner: _task.Task
    for task in tasks:
        task_type: str = type(task).__qualname__
        msg = (
            f"Running combinations for {task_type} instance with ID {task.identifier!r}"
        )
        log.info(msg)
        print(msg)
        try:
            # This assumes that the task instance is a BPETask
            for runner in task.runners():
                msg = f"{task_type} ID: {runner.arguments.get('taskid')}"
                log.info(msg)
                print(msg, end="")
                # TODO: This is not part of the protocol, but should be, when
                # other types of tasks are added.
                result = runner.run()
                if result.ok:
                    postfix = " [green][ done ][/]"
                else:
                    postfix = " [red][ error ][/]"
                print(postfix)
                print(result)

        except KeyboardInterrupt:
            log.info(
                "Asking user to continue or completely exit from list of campaign tasks."
            )
            exit_confirmed = input(
                "Do you want to exit completely ([y]/n)"
            ).lower() in ("", "y")
            if exit_confirmed:
                log.info(
                    "User confirmed breaking the execution of the remaining campaign tasks."
                )
                break


@campaign.command
@click.argument("campaign_name", type=str)
def clean(campaign_name: str) -> None:
    """
    Clean campaign sub directories specified in the campaign configuration.

    """
    _campaign.clean(campaign_name)
