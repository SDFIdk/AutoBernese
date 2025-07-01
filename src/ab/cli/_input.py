"""
Handle command-line interface input

"""

import os
from typing import Final
import datetime as dt


class ENV_VARS:
    AB_CLI_PROMPT_ANSWER = "AB_CLI_PROMPT_ANSWER"


DATE_FORMAT: Final = "%Y-%m-%d"


def date(s: str) -> dt.date:
    return dt.datetime.strptime(s, DATE_FORMAT).date()


def set_prompt_proceed_yes() -> None:
    os.environ[ENV_VARS.AB_CLI_PROMPT_ANSWER] = "Y"


def prompt_proceed() -> bool:
    answer = os.getenv(ENV_VARS.AB_CLI_PROMPT_ANSWER)
    if answer is None:
        answer = input("Proceed? (y/[n]): ")
    return answer.lower() == "y"
